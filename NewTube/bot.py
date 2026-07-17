import os, sys, json, time, urllib.parse, asyncio, requests, hashlib, hmac, secrets, pyfiglet
from datetime import datetime
from telethon import TelegramClient, functions
from termcolor import colored
import random

# ========== BANNER ==========
def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    ascii_art = pyfiglet.figlet_format("Scriptify", font="slant")
    lines = ascii_art.split('\n')
    
    colours = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    
    print("\n" + "="*60)
    print(colored("🌟 WELCOME TO SCRIPTIFY 🌟", "cyan", attrs=["bold"]))
    print("="*60 + "\n")
    
    for line in lines:
        if line.strip():
            coloured_line = ""
            for char in line:
                if char != ' ':
                    colour = random.choice(colours)
                    coloured_line += colored(char, colour, attrs=["bold"])
                else:
                    coloured_line += char
            print(coloured_line)
    
    print("\n" + "="*60)
    print(colored("✨ NEWTUBE AUTO BOT ✨", "magenta", attrs=["bold"]))
    print(colored("   UNKNOWN | SCRIPTER | Full Auto   ", "yellow"))
    print("="*60 + "\n")

# ========== CONFIG ==========
API_ID = 21518358
API_HASH = "3c9576476fb4d4456b98d5619c9c0f3d"
SESSIONS_DIR = "sessions"
AD_WATCH_TIME = 15
CYCLE_WAIT = 5

# ========== COLORS ==========
R = "\033[1;31m"
G = "\033[1;92m"
C = "\033[1;96m"
Y = "\033[1;93m"
B = "\033[1;34m"
P = "\033[1;35m"
D = "\033[0m"
U = "\033[4m"

# ========== SESSION CREATION ==========
async def create_session():
    show_banner()
    
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
    
    print(f"\n{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    print(f"{Y}📱 {U}TELEGRAM SESSION SETUP{U}{D}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}\n")
    
    phone = input(f"{Y}📞 Enter phone number (with country code, e.g., +1234567890): {D}").strip()
    
    if not phone:
        print(f"{R}❌ Phone number is required!{D}")
        return None
    
    session_path = os.path.join(SESSIONS_DIR, f"{phone}.session")
    
    if os.path.exists(session_path):
        use_existing = input(f"{Y}⚠️ Session already exists. Use existing? (y/n): {D}").lower()
        if use_existing == 'y':
            return session_path
    
    client = TelegramClient(session_path, API_ID, API_HASH)
    
    try:
        print(f"\n{C}🔄 Connecting to Telegram...{D}")
        await client.start(phone=phone)
        me = await client.get_me()
        
        print(f"\n{G}✅ Session created successfully!{D}")
        print(f"   {C}👤 Name:{D} {me.first_name} {me.last_name or ''}")
        print(f"   {C}🆔 User ID:{D} {me.id}")
        print(f"   {C}📁 File:{D} {session_path}")
        
        await client.disconnect()
        return session_path
        
    except Exception as e:
        print(f"\n{R}❌ Failed to create session: {e}{D}")
        if os.path.exists(session_path):
            os.remove(session_path)
        return None

def get_session():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
    
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    
    if sessions:
        print(f"\n{C}📁 Found existing session: {sessions[0]}{D}")
        use_existing = input(f"{Y}Use this session? (y/n, or 'new' for new): {D}").lower()
        if use_existing == 'y':
            return os.path.join(SESSIONS_DIR, sessions[0])
        elif use_existing == 'new':
            return asyncio.run(create_session())
        else:
            return asyncio.run(create_session())
    else:
        return asyncio.run(create_session())

# ========== TELEGRAM INIT DATA ==========
async def get_init_data(session_path):
    client = TelegramClient(session_path, API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return None
        
        bot = await client.get_input_entity("@NewTube12_bot")
        web = await client(functions.messages.RequestWebViewRequest(
            peer=bot, bot=bot, platform='android',
            from_bot_menu=False, url="https://newtube-ton.vercel.app/"
        ))
        url = web.url
        if 'tgWebAppData=' not in url:
            return None
        init = url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        init = urllib.parse.unquote(init)
        
        user = {}
        for part in init.split('&'):
            if part.startswith('user='):
                user = json.loads(urllib.parse.unquote(part[5:]))
        
        await client.disconnect()
        return {"init_data": init, "user_info": user}
    except Exception as e:
        print(f"      {R}❌ Login error: {str(e)[:50]}{D}")
        return None
    finally:
        try:
            if client and client.is_connected():
                await client.disconnect()
        except:
            pass

# ========== NEWTUBE API ==========
class NewTubeAPI:
    def __init__(self, init_data, user_info):
        self.init_data = init_data
        self.user_info = user_info
        self.sess = requests.Session()
        self.base_url = "https://newtube-ton.vercel.app"
        self.fingerprint = "9fed0a434c53ffc7138b4bc03c7c5d6ab292b3d32829bd245ce8c4c2f5429b76"
        
        # Ad limits tracking
        self.ad_limits = {
            'adsgramDaily': {'limit': 10, 'count': 0, 'name': 'AdsGram Daily'},
            'adsgramSpecial': {'limit': 5, 'count': 0, 'name': 'AdsGram Special'},
            'monetag': {'limit': 20, 'count': 0, 'name': 'Monetag'},
            'giga': {'limit': 20, 'count': 0, 'name': 'GigaPub'}
        }
        
        self.sess.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.46 Mobile Safari/537.36 Telegram-Android/12.6.4",
            "Origin": "https://newtube-ton.vercel.app",
            "Referer": "https://newtube-ton.vercel.app/",
            "sec-ch-ua-platform": "Android",
            "sec-ch-ua-mobile": "?1",
            "Accept": "*/*",
            "X-Requested-With": "org.telegram.messenger.web"
        })
    
    def _request(self, method, path, data=None):
        url = f"{self.base_url}{path}"
        
        for attempt in range(3):
            try:
                if method == "GET":
                    r = self.sess.get(url, timeout=30)
                else:
                    if data:
                        r = self.sess.post(url, json=data, timeout=30)
                    else:
                        r = self.sess.post(url, timeout=30)
                
                if r.status_code == 200:
                    return r.json()
                return None
            except:
                if attempt == 2:
                    return None
                time.sleep(1)
        return None
    
    # ===== INIT USER =====
    def init_user(self):
        payload = {
            "action": "init",
            "fingerprint": self.fingerprint,
            "initData": self.init_data
        }
        return self._request("POST", "/api/user", payload)
    
    # ===== CLAIM AD REWARD =====
    def claim_ad(self, network):
        payload = {
            "action": "claimAdReward",
            "network": network,
            "initData": self.init_data
        }
        result = self._request("POST", "/api/earn", payload)
        if result and result.get('ok'):
            reward = result.get('reward', 0)
            count = result.get('countToday', 0)
            limit = result.get('dailyLimit', 0)
            
            # Update tracking
            if network in self.ad_limits:
                self.ad_limits[network]['count'] = count
                self.ad_limits[network]['limit'] = limit
            
            return reward, count, limit
        return None, None, None
    
    def get_remaining(self, network):
        if network in self.ad_limits:
            return max(0, self.ad_limits[network]['limit'] - self.ad_limits[network]['count'])
        return 0
    
    def is_limit_reached(self, network):
        if network in self.ad_limits:
            return self.ad_limits[network]['count'] >= self.ad_limits[network]['limit']
        return True

# ========== SIMULATE AD WATCH ==========
def simulate_ad_watch(provider_name):
    print(f"      {Y}⏳ {provider_name}: [{D}", end="", flush=True)
    for sec in range(AD_WATCH_TIME):
        progress = int((sec + 1) / AD_WATCH_TIME * 20)
        bar = "█" * progress + "░" * (20 - progress)
        pct = int((sec + 1) / AD_WATCH_TIME * 100)
        print(f"\r      {Y}⏳ {provider_name}: [{C}{bar}{Y}] {pct}%{D}", end="", flush=True)
        time.sleep(1)
    print(f"\r      {G}✅ {provider_name}: [{'█'*20}] 100%     {D}")
    print(f"      {G}👆 Clicking ad...{D}")
    time.sleep(0.5)
    print(f"      {G}✅ Ad completed!{D}")

# ========== FEATURE: DAILY ADS ==========
def do_daily_ads(api):
    print(f"\n{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    print(f"{Y}📢 {U}DAILY ADS - ALL PROVIDERS{U}{D}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    
    # Init user first
    print(f"\n   {C}🔄 Initializing user...{D}")
    init = api.init_user()
    if init:
        print(f"   {G}✅ User initialized{D}")
    
    # Show initial limits
    print(f"\n   {B}📊 DAILY LIMITS:{D}")
    for key, data in api.ad_limits.items():
        remaining = api.get_remaining(key)
        print(f"   {C}┌─── {data['name']}:{D} {data['count']}/{data['limit']} (Remaining: {remaining})")
    
    # Check if all limits reached
    all_done = True
    for key in api.ad_limits:
        if not api.is_limit_reached(key):
            all_done = False
            break
    
    if all_done:
        print(f"\n   {G}🎯 All providers reached daily limit!{D}")
        return 0, 0
    
    # Ads providers list
    providers = [
        ('adsgramDaily', 'AdsGram Daily'),
        ('adsgramSpecial', 'AdsGram Special'),
        ('monetag', 'Monetag'),
        ('giga', 'GigaPub')
    ]
    
    total_earned = 0
    total_ads_done = 0
    cycle = 0
    max_cycles = 25
    
    while cycle < max_cycles:
        # Check if all providers done
        all_done = True
        for key, _ in providers:
            if not api.is_limit_reached(key):
                all_done = False
                break
        
        if all_done:
            print(f"\n   {G}🎯 All providers reached daily limit!{D}")
            break
        
        cycle += 1
        print(f"\n   {B}─── CYCLE #{cycle} ───{D}")
        cycle_earned = 0
        cycle_ads = 0
        
        for network, name in providers:
            if api.is_limit_reached(network):
                print(f"\n   {Y}▶ {name}: SKIPPED (Limit reached {api.ad_limits[network]['count']}/{api.ad_limits[network]['limit']}){D}")
                continue
            
            remaining = api.get_remaining(network)
            print(f"\n   {C}▶ {name} ({remaining} remaining){D}")
            
            # Simulate ad watch
            simulate_ad_watch(name)
            
            # Claim ad
            reward, count, limit = api.claim_ad(network)
            
            if reward is not None:
                cycle_earned += reward
                cycle_ads += 1
                total_earned += reward
                total_ads_done += 1
                remaining_new = api.get_remaining(network)
                print(f"   {G}✅ +{reward} points | {count}/{limit} | Remaining: {remaining_new}{D}")
                
                if remaining_new <= 0:
                    print(f"   {G}🎯 {name} daily limit reached ({limit}/{limit})!{D}")
            else:
                print(f"   {R}❌ Failed - marking as limit reached{D}")
                api.ad_limits[network]['count'] = api.ad_limits[network]['limit']
            
            time.sleep(0.5)
        
        if cycle_ads == 0:
            # Check if all done
            all_done = True
            for key, _ in providers:
                if not api.is_limit_reached(key):
                    all_done = False
                    break
            if all_done:
                print(f"\n   {G}🎯 All providers reached daily limit!{D}")
            else:
                print(f"\n   {Y}⏳ No ads completed this cycle.{D}")
            break
        
        print(f"\n   {B}└─ Cycle #{cycle}: {cycle_ads} ads | +{cycle_earned} points{D}")
        
        # 5 second wait before next cycle
        print(f"\n   {Y}⏳ Waiting {CYCLE_WAIT} seconds before next cycle...{D}")
        for i in range(CYCLE_WAIT, 0, -1):
            print(f"\r   {Y}⏳ {i}s remaining{D}", end="", flush=True)
            time.sleep(1)
        print()
    
    print(f"\n   {B}{'─'*40}{D}")
    print(f"   {B}📊 ADS SUMMARY{D}")
    print(f"   {B}{'─'*40}{D}")
    print(f"   {C}🔄 Cycles Run:{D} {cycle}")
    print(f"   {C}✅ Ads Completed:{D} {total_ads_done}")
    print(f"   {C}💰 Total Earned:{D} +{total_earned} points")
    print(f"\n   {B}📊 FINAL STATUS:{D}")
    for key, data in api.ad_limits.items():
        status = "✅ DONE" if data['count'] >= data['limit'] else f"⏳ {data['count']}/{data['limit']}"
        print(f"   {C}┌─── {data['name']}:{D} {status}")
    print(f"   {B}{'─'*40}{D}")
    
    return total_ads_done, total_earned

# ========== MAIN MENU ==========
def show_menu():
    print(f"\n{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    print(f"{Y}📋 {U}MAIN MENU{U}{D}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    print(f"  {C}1.{D} Daily Ads")
    print(f"  {C}2.{D} Exit")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    choice = input(f"{Y}👉 Select option (1-2): {D}").strip()
    return choice

# ========== MAIN ==========
def main():
    show_banner()
    
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
    
    print(f"\n{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    print(f"{Y}📱 {U}TELEGRAM SESSION{U}{D}")
    print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{D}")
    
    session_path = get_session()
    if not session_path:
        print(f"{R}❌ No session found{D}")
        return
    
    print(f"\n{G}✅ Session loaded: {session_path}{D}")
    
    print(f"\n{C}🔄 Getting Telegram data...{D}")
    data = asyncio.run(get_init_data(session_path))
    if not data:
        print(f"{R}❌ Failed to get Telegram data{D}")
        return
    
    init_data, user = data["init_data"], data["user_info"]
    name = user.get('first_name', 'Unknown')
    username = user.get('username', '')
    
    print(f"{G}✅ Logged in as: {C}{name}{D} (@{username})")
    
    api = NewTubeAPI(init_data, user)
    
    while True:
        show_banner()
        choice = show_menu()
        
        if choice == '1':
            do_daily_ads(api)
        elif choice == '2':
            print(f"\n{G}👋 Goodbye!{D}")
            break
        else:
            print(f"\n{R}❌ Invalid option!{D}")
        
        input(f"\n{Y}Press Enter to continue...{D}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Y}🛑 Interrupted{D}")
        sys.exit(0)