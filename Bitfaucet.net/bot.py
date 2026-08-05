#!/usr/bin/env python3
"""
BITFAUCET AUTO CLAIM + PTC TASKS + SHORTLINK HANDLING (with retry)
- Faucet claims with automatic shortlink solving (retries on failure)
- PTC tasks (bitcotask) with corrected index encoding
- Menu: 1=Faucet, 2=PTC, 3=Both, 4=Refresh Balance, 5=Shortlinks, 6=Exit
- All captcha solving via remote BuxAds API
"""

import os, sys, time, json, hashlib, hmac, random, requests, re, base64, io
from datetime import datetime
from urllib.parse import urljoin, urlencode, urlparse, quote
from pathlib import Path
from PIL import Image

# ------------------- CONFIG FILE -------------------
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def prompt_for_config():
    print("\n⚙️  First-time setup – enter your details:")
    email = input("Bitfaucet email: ").strip()
    user_agent = input("User-Agent (press Enter for default): ").strip()
    if not user_agent:
        user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
    api_key = input("BuxAds API key (from @buxads_bot): ").strip()
    config = {
        "email": email,
        "password": "",
        "user_agent": user_agent,
        "api_key": api_key
    }
    save_config(config)
    return config

config = load_config()
if not config:
    config = prompt_for_config()
    if not config["email"] or not config["api_key"]:
        print("❌ Email and API key are required. Exiting.")
        sys.exit(1)

EMAIL = config["email"]
PASSWORD = config["password"]
USER_AGENT = config["user_agent"]
API_KEY = config["api_key"]

SYMBOL = "LTC"
MAX_CLAIMS_PER_DAY = 500
DELAY_MIN = 10
DELAY_MAX = 30
SIGNATURE_SECRET = "InstantFaucet2026!"
API_URL = "http://37.60.224.60:7860/api"

# Only these shortlink domains can be bypassed by your API
SUPPORTED_DOMAINS = ["shrinkme.io", "adlink.click", "clk.sh", "shrinkearn.com"]
HCAPTCHA_SITEKEY = "60deca42-063c-409c-8058-b61a995233b6"
HCAPTCHA_DOMAIN = "https://bitfaucet.net/"

# ----------------------------------------------------

def get_timezone() -> str:
    try: return datetime.now().astimezone().tzname()
    except: return "UTC"

def generate_fingerprint() -> str:
    return hashlib.md5(f"{time.time()}{random.randint(0, 999999)}".encode()).hexdigest()

def build_signature(user_id: str, timestamp: str) -> str:
    return hmac.new(SIGNATURE_SECRET.encode(), f"{user_id}{timestamp}".encode(), hashlib.sha256).hexdigest()

def format_amount(amount: float, decimals: int = 8) -> str:
    return f"{amount:.{decimals}f}".rstrip('0').rstrip('.')

# ------------------- REMOTE API HELPERS -------------------
def get_balance():
    payload = {"apikey": API_KEY, "mode": "getbalance"}
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("balance")
    except Exception as e:
        print(f"⚠️  Balance check failed: {e}")
        return None

def api_submit(mode, extra_payload):
    payload = {"apikey": API_KEY, "mode": mode}
    payload.update(extra_payload)
    resp = requests.post(API_URL, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"API error: {data['error']}")
    job_id = data.get("jobId")
    if not job_id:
        raise RuntimeError("No jobId returned")
    return job_id

def api_poll(job_id):
    for _ in range(12):
        time.sleep(10)
        poll_payload = {"apikey": API_KEY, "action": "get", "id": job_id}
        resp = requests.post(API_URL, json=poll_payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") is True:
            return data
        elif data.get("status") == "pending":
            continue
        else:
            raise RuntimeError(f"Poll status: {data.get('status')}")
    raise RuntimeError("Polling timeout")

def solve_adslab_remote(sitekey, domain, subid="widget_user", max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            job_id = api_submit("adslab", {"sitekey": sitekey, "domain": domain, "subid": subid})
            result = api_poll(job_id)
            token = result.get("token")
            if token:
                return token
            else:
                raise RuntimeError("No token in response")
        except RuntimeError as e:
            if attempt == max_retries:
                raise
            print(f"  ⚠️  Attempt {attempt} failed: {e}. Retrying...")
            time.sleep(2)
    raise RuntimeError("Failed after max retries")

def solve_bitcotask_remote(main_base64, options_base64):
    job_id = api_submit("bitcotask", {"main": main_base64, "options": options_base64})
    result = api_poll(job_id)
    index = result.get("index")
    if index is None:
        raise RuntimeError("No index in response")
    return int(index)

# ------------------- SHORTLINK SOLVER (with retry across providers) -------------------
def solve_hcaptcha_shortlink():
    return api_poll(api_submit("hcaptcha", {
        "domain": HCAPTCHA_DOMAIN,
        "siteKey": HCAPTCHA_SITEKEY
    }))["token"]

def bypass_shortlink(url):
    """Send a shortlink URL to API for bypass; return original URL."""
    print(f"    🔗 Bypassing shortlink: {url}")
    job_id = api_submit("shortlink", {"url": url})
    for _ in range(20):
        time.sleep(5)
        poll_payload = {"apikey": API_KEY, "action": "get", "id": job_id}
        resp = requests.post(API_URL, json=poll_payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") is True:
            original_url = data.get("original_url")
            if original_url:
                return original_url
            else:
                raise RuntimeError("No original_url in bypass response")
        elif data.get("status") == "pending":
            continue
        else:
            raise RuntimeError(f"Bypass poll status: {data.get('status')}")
    raise RuntimeError("Bypass polling timeout")

def process_single_shortlink(access_token, provider):
    """Attempt to complete one shortlink with the given provider. Returns True if successful."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": USER_AGENT
    }

    print(f"  🔗 Trying shortlink: {provider['name']} ({provider['domain']})")

    # Solve hCaptcha
    print("  🔐 Solving hCaptcha for shortlink...")
    hcaptcha_token = solve_hcaptcha_shortlink()

    # Start shortlink
    start_payload = {
        "shortlinkId": provider["_id"],
        "symbol": SYMBOL,
        "captchaToken": hcaptcha_token,
        "captchaType": "hcaptcha"
    }
    resp = requests.post("https://bitfaucet.net/api/shortlinks/start",
                         json=start_payload, headers=headers)
    resp.raise_for_status()
    start_data = resp.json()
    if not start_data.get("success"):
        print(f"  ❌ Shortlink start failed: {start_data}")
        return False

    redirect_url = start_data["url"]
    print(f"  🔗 Shortlink URL: {redirect_url}")

    # Bypass to get verification URL
    try:
        original_url = bypass_shortlink(redirect_url)
    except RuntimeError as e:
        print(f"  ❌ Bypass failed: {e}")
        return False

    print(f"  🎯 Bypassed to: {original_url}")

    # Extract key from verification URL
    key_match = re.search(r'/verify/([a-f0-9]+)', original_url)
    if not key_match:
        print(f"  ❌ Could not extract verification key from {original_url}")
        return False

    key = key_match.group(1)
    print(f"  🔑 Verification key: {key}")

    # Wait 60-90 seconds
    wait_time = random.randint(60, 90)
    print(f"  ⏳ Waiting {wait_time}s before verification...")
    time.sleep(wait_time)

    # Verify
    verify_payload = {"key": key}
    resp = requests.post("https://bitfaucet.net/api/shortlinks/verify",
                         json=verify_payload, headers=headers)
    resp.raise_for_status()
    verify_data = resp.json()
    if verify_data.get("success"):
        print(f"  ✅ Shortlink completed. Reward: {verify_data.get('cryptoAmount')} {verify_data.get('symbol')}")
        return True
    else:
        print(f"  ❌ Verification failed: {verify_data}")
        return False

def try_all_shortlinks(access_token):
    """Iterate through all supported shortlink providers with available daily limit until one succeeds."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": USER_AGENT
    }
    # Fetch fresh provider list
    resp = requests.get("https://bitfaucet.net/api/shortlinks", headers=headers)
    resp.raise_for_status()
    providers = resp.json()

    # Filter supported domains that still have remaining daily limit
    candidates = [p for p in providers
                  if p["domain"] in SUPPORTED_DOMAINS and p["userVisitsToday"] < p["dailyLimit"]]

    if not candidates:
        print("  ❌ No supported shortlink available or all daily limits reached.")
        return False

    for provider in candidates:
        try:
            if process_single_shortlink(access_token, provider):
                return True
        except Exception as e:
            print(f"  ❌ Shortlink attempt failed with {provider['name']}: {e}")
        # Small delay before trying the next provider
        time.sleep(3)
    print("  ❌ All shortlink providers failed.")
    return False

def run_shortlinks_only(scraper, access_token, user_id):
    print("\n🔗 Starting shortlinks only...")
    count = 0
    while True:
        if try_all_shortlinks(access_token):
            count += 1
            time.sleep(random.randint(5, 10))
        else:
            print(f"No more shortlinks available. Completed {count} shortlink(s).")
            break

# ------------------- PTC / BITCOTASK HELPERS -------------------
def raw_rgba_to_png_base64(raw_base64, width, height):
    raw = base64.b64decode(raw_base64)
    expected_len = width * height * 4
    if len(raw) != expected_len:
        return None
    img = Image.frombytes('RGBA', (width, height), raw)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

def extract_captcha_data(js_content, referer_url):
    hidden_id = None
    m = re.search(r'<input[^>]*type="hidden"[^>]*id="([^"]+)"[^>]*>', js_content, re.I)
    if m:
        hidden_id = m.group(1)
    base_data = None
    m = re.search(r'var payload\s*=\s*"([^"]*)"', js_content)
    if m:
        base_data = m.group(1)
    post_url = None
    m = re.search(r'xhr\.open\(\s*"POST"\s*,\s*"([^"]+)"\s*,', js_content)
    if m:
        post_url = m.group(1)
        if not post_url.startswith('http'):
            post_url = urljoin(referer_url, post_url)
    token_property = None
    m = re.search(r'cctoken\s*=\s*response\.([a-zA-Z0-9_]+)\s*;', js_content)
    if m:
        token_property = m.group(1)
    if base_data is None or post_url is None:
        return None
    return {'hidden_id': hidden_id, 'base_data': base_data, 'post_url': post_url, 'token_property': token_property}

def solve_pow(challenge, difficulty=4):
    prefix = '0' * difficulty
    nonce = 0
    while True:
        test = f"{challenge}:{nonce}"
        h = hashlib.sha256(test.encode()).hexdigest()
        if h.startswith(prefix):
            return nonce, h
        nonce += 1

def save_debug_images(task_title, main_b64, options_b64_list, api_index):
    DEBUG_DIR = Path(__file__).parent / "ptc_debug"
    DEBUG_DIR.mkdir(exist_ok=True)
    timestamp = int(time.time())
    folder = DEBUG_DIR / f"{task_title[:30]}_{timestamp}"
    folder.mkdir(exist_ok=True)
    with open(folder / "main.png", "wb") as f:
        f.write(base64.b64decode(main_b64))
    for i, opt_b64 in enumerate(options_b64_list):
        with open(folder / f"option_{i}.png", "wb") as f:
            f.write(base64.b64decode(opt_b64))
    with open(folder / "api_index.txt", "w") as f:
        f.write(f"API returned index: {api_index}\n")
    print(f"    💾 Wrong answer – saved debug images to {folder}")

def solve_bitcotask_captcha(page_html, referer_url, session, task_title="unknown"):
    m = re.search(r'<script\s+src="([^"]+captcha2/[^"]+\.js\?action=captcha)"', page_html)
    if not m:
        raise RuntimeError("Captcha JS URL not found")
    captcha_url = m.group(1)
    if not captcha_url.startswith('http'):
        captcha_url = urljoin(referer_url, captcha_url)

    headers = {"User-Agent": USER_AGENT, "Accept": "*/*", "Referer": referer_url}
    resp = session.get(captcha_url, headers=headers)
    resp.raise_for_status()
    js_content = resp.text

    payload = {"t": int(time.time() * 1000), "r": random.random()}
    resp = session.post(captcha_url, headers=headers, json=payload)
    resp.raise_for_status()
    challenge_data = resp.json()

    target_width = challenge_data.get('width', 200)
    target_height = challenge_data.get('height', 100)
    main_b64 = raw_rgba_to_png_base64(challenge_data['pixel'], target_width, target_height)
    if not main_b64:
        raise RuntimeError("Failed to convert main image")

    options_b64_list = []
    for opt in challenge_data['options']:
        b64 = raw_rgba_to_png_base64(opt['pixels'], opt['width'], opt['height'])
        if not b64:
            raise RuntimeError("Failed to convert option image")
        options_b64_list.append(b64)

    api_index = solve_bitcotask_remote(main_b64, options_b64_list)
    print(f"    👉 API returned index: {api_index}")

    data = extract_captcha_data(js_content, referer_url)
    if not data:
        raise RuntimeError("Could not extract captcha data")

    challenge = challenge_data.get('challenge', '')
    difficulty = challenge_data.get('difficulty', 4)
    if challenge:
        nonce, pow_hash = solve_pow(challenge, difficulty)
        pw = json.dumps({"nonce": nonce, "hash": pow_hash})
    else:
        nonce = 0
        pw = 'null'

    _et = random.randint(10000, 13000)
    _mv = random.randint(2, 3)
    _cf = random.randint(4000, 5000)
    _ch = challenge
    _bindRaw = f"{_et}:{nonce}:{_ch}"
    _bh = hashlib.sha256(_bindRaw.encode()).hexdigest()

    # Fix: use quote() for index part (no '=' sign)
    post_body = data['base_data'] + quote(f"[{api_index}]") + '&' + urlencode({
        '_et': _et,
        '_mv': _mv,
        '_cf': _cf,
        '_pw': pw,
        '_ch': _ch,
        '_bh': _bh
    })

    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": f"https://{urlparse(referer_url).hostname}",
        "Referer": referer_url
    }
    resp = session.post(data['post_url'], data=post_body, headers=headers)
    resp.raise_for_status()
    result_json = resp.json()
    print(f"    📦 Captcha POST response: {json.dumps(result_json)}")

    token_value = None
    if data['token_property'] and data['token_property'] in result_json:
        token_value = result_json[data['token_property']]
    if not token_value and data['hidden_id'] and data['hidden_id'] in result_json:
        token_value = result_json[data['hidden_id']]
    if not token_value:
        for key in result_json:
            if key not in ('success', 'error'):
                token_value = result_json[key]
                break

    if token_value is False:
        save_debug_images(task_title, main_b64, options_b64_list, api_index)
        raise RuntimeError("Captcha answer rejected (false). Images saved.")

    if token_value:
        print(f"    ✅ Extracted token: {token_value}")
        return data['hidden_id'], token_value
    else:
        save_debug_images(task_title, main_b64, options_b64_list, api_index)
        raise RuntimeError("Could not extract token from captcha response")

def process_bitcotask_ptc(task_data, session):
    url = task_data['url']
    duration = int(task_data['duration'])
    print(f"  🔗 {task_data['title']} ({duration}s)")

    resp = session.get(url, allow_redirects=True, timeout=30)
    final_url = resp.url
    page_html = resp.text

    m = re.search(r'window\.location\.href\s*=\s*[\'"]([^\'"]+)[\'"]', page_html)
    if m:
        redirect = m.group(1)
        final_url = urljoin(final_url, redirect)
        resp = session.get(final_url)
        page_html = resp.text

    duration_var = re.search(r'var duration\s*=\s*([0-9]+)', page_html)
    token_var   = re.search(r"var token\s*=\s*'([^']+)'", page_html)
    sub_id_var  = re.search(r"var sub_id\s*=\s*'([^']+)'", page_html)
    hash_var    = re.search(r"var hash\s*=\s*'([^']+)'", page_html)
    api_key_var = re.search(r"var api_key\s*=\s*'([^']+)'", page_html)

    if not all([duration_var, token_var, sub_id_var, hash_var, api_key_var]):
        print("  ❌ Missing page variables")
        return False

    wait_time = int(duration_var.group(1))
    token = token_var.group(1)
    sub_id = sub_id_var.group(1)
    hash_val = hash_var.group(1)
    api_key = api_key_var.group(1)

    ajax_headers = {"X-Requested-With": "XMLHttpRequest", "User-Agent": USER_AGENT, "Referer": final_url}
    session.post(final_url, data={"action": "start_view"}, headers=ajax_headers)

    print(f"  ⏳ Waiting {wait_time}s...")
    time.sleep(wait_time)

    print("  🧩 Solving captcha...")
    try:
        token_id, captcha_token = solve_bitcotask_captcha(page_html, final_url, session, task_data['title'])
    except Exception as e:
        print(f"  ❌ Captcha failed: {e}")
        return False

    post_data = {
        "hash": hash_val, "sub_id": sub_id, "key": api_key, "token": token,
        token_id: captcha_token, "action": "proccessLead"
    }
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
               "X-Requested-With": "XMLHttpRequest", "User-Agent": USER_AGENT, "Referer": final_url}
    resp = session.post("https://bitcotasks.com/system/ajax.php", data=post_data, headers=headers)
    resp.raise_for_status()
    result = resp.json()
    print(f"  ✅ {result.get('message', 'Success')}")
    return True

def process_ptc_tasks(session, access_token, user_id):
    print("\n🔄 Fetching PTC tasks...")
    headers = {"Authorization": f"Bearer {access_token}", "User-Agent": USER_AGENT}
    resp = session.get("https://bitfaucet.net/api/tasks/bitcotasks-ptc", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        print("❌ Could not fetch PTC tasks")
        return

    tasks = data.get("data", [])
    print(f"📋 {len(tasks)} tasks available.")

    ptc_session = requests.Session()
    ptc_session.headers.update({"User-Agent": USER_AGENT})

    for task in tasks:
        process_bitcotask_ptc(task, ptc_session)
        time.sleep(random.randint(3, 7))

# ------------------- BITFAUCET API HELPERS -------------------
def login(session, email, password, captcha_token, fp_hash, timezone):
    url = "https://bitfaucet.net/api/auth/login"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Origin": "https://bitfaucet.net",
        "Referer": "https://bitfaucet.net/",
    }
    payload = {
        "email": email,
        "password": password or "",
        "referral": "",
        "captchaToken": captcha_token,
        "captchaType": "adslab_pro",
        "fpHash": fp_hash,
        "deviceTimezone": timezone,
    }
    resp = session.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Login failed: {data}")
    return data, data["token"], data["user"]["_id"]

def get_stats(session, token, symbol):
    url = "https://bitfaucet.net/api/faucets/stats"
    headers = {"Authorization": f"Bearer {token}", "Referer": f"https://bitfaucet.net/faucets/{symbol}", "User-Agent": USER_AGENT}
    resp = session.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def claim_faucet(session, token, symbol, captcha_token, user_id):
    url = "https://bitfaucet.net/api/faucets/claim"
    timestamp = str(int(time.time() * 1000))
    signature = build_signature(user_id, timestamp)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://bitfaucet.net",
        "Referer": f"https://bitfaucet.net/faucets/{symbol}",
        "x-claim-timestamp": timestamp,
        "x-claim-signature": signature,
        "User-Agent": USER_AGENT,
    }
    payload = {"symbol": symbol, "captchaToken": captcha_token, "captchaType": "adslab_pro", "adBlockCheck": True}
    resp = session.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def handle_ad(session, token, symbol, user_id, ad_type):
    print(f"    ⚠️ Ad required: {ad_type}. Waiting 15s...")
    time.sleep(15)
    return {"requiresAd": False, "retry": True}

# ------------------- FAUCET LOOP (with shortlink retry) -------------------
def run_faucet_only(scraper, access_token, user_id):
    print(f"\n💰 Starting faucet loop for {SYMBOL} (max {MAX_CLAIMS_PER_DAY} claims/day)")
    while True:
        stats = get_stats(scraper, access_token, SYMBOL)
        claims_today = stats.get("claimsToday", 0)
        print(f"\n📊 Claims today: {claims_today} / {MAX_CLAIMS_PER_DAY}")
        if claims_today >= MAX_CLAIMS_PER_DAY:
            print("🏁 Daily limit reached.")
            break

        start = time.time()
        print("🔄 Solving claim captcha...")
        try:
            claim_token = solve_adslab_remote(
                sitekey="apv_5b59491111790f2472e83fba637745f55523",
                domain="bitfaucet.net"
            )
        except RuntimeError as e:
            print(f"❌ Captcha solving failed: {e}")
            time.sleep(30)
            continue

        print("📤 Claiming...")
        try:
            resp = claim_faucet(scraper, access_token, SYMBOL, claim_token, user_id)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("❌ Rate limited. Waiting 60s...")
                time.sleep(60)
                continue
            elif e.response.status_code == 403:
                # Check if it's a shortlink requirement
                try:
                    error_body = e.response.json()
                except:
                    error_body = {}
                if isinstance(error_body, dict) and "error" in error_body and "Shortlink" in error_body.get("error", ""):
                    print("  ⛓️ Shortlink required – trying all available providers...")
                    if try_all_shortlinks(access_token):
                        print("  ➡️ Shortlink done, retrying claim...")
                        time.sleep(5)
                        continue
                    else:
                        print("  ❌ Shortlink processing failed, cannot continue faucet.")
                        break
                else:
                    print(f"❌ Claim failed with 403: {e.response.text}")
                    break
            else:
                raise

        elapsed = time.time() - start
        if resp.get("success"):
            amount = resp.get("cryptoAmount", 0)
            satoshis = resp.get("satoshis", 0)
            print(f"✅ Solved in {elapsed:.1f}s → {format_amount(amount)} {SYMBOL} ({satoshis} satoshis)")
        elif resp.get("requiresAd"):
            ad_type = resp.get("adType")
            handle_ad(scraper, access_token, SYMBOL, user_id, ad_type)
            time.sleep(5)
            retry_resp = claim_faucet(scraper, access_token, SYMBOL, claim_token, user_id)
            if retry_resp.get("success"):
                amount = retry_resp.get("cryptoAmount", 0)
                print(f"✅ Solved in {elapsed:.1f}s (after ad) → {format_amount(amount)} {SYMBOL}")
            else:
                print("❌ Ad claim failed")
        elif resp.get("error") and "Shortlink" in resp.get("error", ""):
            print("  ⛓️ Shortlink required – trying all available providers...")
            if try_all_shortlinks(access_token):
                print("  ➡️ Shortlink done, retrying claim...")
                time.sleep(5)
                continue
            else:
                print("  ❌ Shortlink processing failed, cannot continue faucet.")
                break
        else:
            print(f"❌ Claim failed: {resp.get('message', resp.get('error', 'unknown'))}")
            if resp.get("error") == "highrisk":
                print("🚫 High risk flag – exiting.")
                break

        time.sleep(random.randint(DELAY_MIN, DELAY_MAX))

# ------------------- MENU & MAIN -------------------
def show_menu(balance):
    print("\n" + "="*40)
    print("  BITFAUCET AUTO EARNER")
    if balance is not None:
        print(f"  Balance: ${balance:.6f}")
    else:
        print("  Balance: unknown")
    print("="*40)
    print("  1. Faucet claims only")
    print("  2. PTC tasks only")
    print("  3. Both (faucet then PTC)")
    print("  4. Refresh balance")
    print("  5. Shortlinks only")
    print("  6. Exit")
    print("="*40)

def main():
    import cloudscraper
    scraper = cloudscraper.create_scraper()
    scraper.headers.update({"User-Agent": USER_AGENT})
    print("🌐 Visiting bitfaucet.net...")
    scraper.get("https://bitfaucet.net/", timeout=30)

    timezone = get_timezone()
    fp_hash = generate_fingerprint()

    balance = get_balance()
    if balance is not None:
        print(f"💰 BuxAds Balance: ${balance:.6f}")

    print("🔐 Solving login captcha via remote API...")
    login_token = solve_adslab_remote(
        sitekey="apv_5b59491111790f2472e83fba637745f55523",
        domain="bitfaucet.net"
    )

    print("🔑 Logging in...")
    login_data, access_token, user_id = login(scraper, EMAIL, PASSWORD, login_token, fp_hash, timezone)
    print(f"✅ Login successful! User: {login_data['user']['email']}")

    while True:
        balance = get_balance()
        show_menu(balance)
        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            run_faucet_only(scraper, access_token, user_id)
        elif choice == "2":
            process_ptc_tasks(scraper, access_token, user_id)
        elif choice == "3":
            run_faucet_only(scraper, access_token, user_id)
            process_ptc_tasks(scraper, access_token, user_id)
        elif choice == "4":
            balance = get_balance()
            if balance is not None:
                print(f"💰 Current Balance: ${balance:.6f}")
            else:
                print("❌ Failed to fetch balance")
        elif choice == "5":
            run_shortlinks_only(scraper, access_token, user_id)
        elif choice == "6":
            print("👋 Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

    print("\n🎉 All done.")

if __name__ == "__main__":
    main()
