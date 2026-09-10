import os
import asyncio
import glob
import urllib.parse
import random
import shutil
import re
import json
import time
import aiohttp
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.errors import FloodWaitError
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

API_ID = 28752231
API_HASH = "ec1c1f2c30e2f1855c3edee7e348480b"
BOT_USERNAME = "TaskyAppbot"
BASE_URL = "https://tasky3.onrender.com"

# 🔥 REFERRAL CODE - CHANGE THIS
REFERRAL_CODE = "TASKY146377389"

# Daily limits
MONETAG_LIMIT = 30
GIGAPUB_LIMIT = 30
TASK_LIMIT = 60

# Batch size for login only
LOGIN_BATCH_SIZE = 1

# Required channels
REQUIRED_CHANNELS = []

# ============================================================
# COLOR & BANNER
# ============================================================

class C:
    RES = '\033[0m'
    CYA = '\033[96m'
    GRE = '\033[92m'
    YEL = '\033[93m'
    RED = '\033[91m'
    MAG = '\033[95m'
    WHT = '\033[97m'
    BLD = '\033[1m'

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_term_width():
    cols = shutil.get_terminal_size((50, 20)).columns
    return min(cols, 70)

def print_banner():
    clr()
    w = get_term_width()
    print(f"{C.CYA}{C.BLD}┌{'─' * (w-2)}┐{C.RES}")
    print(f"{C.CYA}{C.BLD}│{C.WHT} T A S K Y 3   A U T O M A T I O N {C.CYA}".center(w + 10) + f"{C.BLD}│{C.RES}")
    print(f"{C.CYA}{C.BLD}│{C.MAG} ❖ Scriptify Myra ❖ {C.CYA}".center(w + 10) + f"{C.BLD}│{C.RES}")
    print(f"{C.CYA}{C.BLD}├{'─' * (w-2)}┤{C.RES}")
    print(f"{C.CYA}{C.BLD}│ {C.WHT}REF CODE: {C.GRE}{REFERRAL_CODE}{C.CYA}".ljust(w + 10) + f"│{C.RES}")
    print(f"{C.CYA}{C.BLD}│ {C.WHT}STATUS: {C.GRE}ACTIVE{C.CYA}".ljust(w + 10) + f"│{C.RES}")
    print(f"{C.CYA}{C.BLD}│ {C.WHT}MODE  : {C.GRE}Scriptify{C.CYA}".ljust(w + 10) + f"│{C.RES}")
    print(f"{C.CYA}{C.BLD}│ {C.WHT}LOGIN : {C.GRE}BATCH OF {LOGIN_BATCH_SIZE}{C.CYA}".ljust(w + 10) + f"│{C.RES}")
    print(f"{C.CYA}{C.BLD}└{'─' * (w-2)}┘{C.RES}\n")

def get_base_headers():
    return {
        'Accept': "application/json, text/plain, */*",
        'sec-ch-ua': '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': "?1",
        'sec-ch-ua-platform': '"Android"',
        'X-Requested-With': "org.telegram.messenger.web",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Accept-Language': "en-US,en;q=0.9",
        'User-Agent': "Mozilla/5.0 (Linux; Android 15; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.9.1",
    }

# ============================================================
# GLOBAL STATE
# ============================================================

account_progress = {}
progress_lock = asyncio.Lock()
login_semaphore = asyncio.Semaphore(LOGIN_BATCH_SIZE)  # ✅ 10 accounts max login at a time
api_semaphore = asyncio.Semaphore(20)  # ✅ 20 concurrent API calls

def format_progress(account_name):
    if account_name not in account_progress:
        return f"{account_name:14} ⏳ Initializing..."
    
    p = account_progress[account_name]
    status = p.get('status', '⏳')
    monetag = p.get('monetag', 0)
    gigapub = p.get('gigapub', 0)
    tasks = p.get('tasks', 0)
    balance = p.get('balance', 0)
    action = p.get('action', '')
    total_ads = p.get('total_ads', 0)
    
    status_emoji = '✅' if status == 'done' else '❌' if status == 'error' else '🔄' if status == 'working' else '⏳'
    
    all_done = monetag >= MONETAG_LIMIT and gigapub >= GIGAPUB_LIMIT and tasks >= TASK_LIMIT
    if all_done:
        status_emoji = '✅'
        action = 'COMPLETE! 🎉'
    
    return f"{account_name:14} {status_emoji} M:{monetag:2}/{MONETAG_LIMIT:2} G:{gigapub:2}/{GIGAPUB_LIMIT:2} T:{tasks:2}/{TASK_LIMIT:2} 📊:{total_ads:2} {action:20} {balance:7.0f}"

async def display_progress():
    clr()
    print_banner()
    
    names = list(account_progress.keys())
    for name in names:
        print(format_progress(name))
    
    total_accounts = len(names)
    done = sum(1 for p in account_progress.values() if p.get('status') == 'done')
    error = sum(1 for p in account_progress.values() if p.get('status') == 'error')
    working = total_accounts - done - error
    
    print(f"\n{C.CYA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RES}")
    print(f"{C.WHT}📊 Total: {total_accounts} | ✅ Done: {done} | 🔄 Working: {working} | ❌ Error: {error}{C.RES}")

async def update_progress(account_name, **kwargs):
    async with progress_lock:
        if account_name not in account_progress:
            account_progress[account_name] = {}
        account_progress[account_name].update(kwargs)

# ============================================================
# MAIN BOT CLASS
# ============================================================

class Tasky3AutoBot:
    def __init__(self, session_path, session_name):
        self.session_path = session_path
        self.session_name = session_name
        self.client = None
        self.telegram_id = None
        self.username = None
        self.first_name = None
        self.balance = 0
        self.start_balance = 0
        self.total_earned = 0

        self.monetag_count = 0
        self.gigapub_count = 0
        self.task_count = 0
        self.total_ads = 0
        self.channels_verified = False

        self.monetag_limit_reached = False
        self.gigapub_limit_reached = False
        self.task_limit_reached = False

        self.headers = get_base_headers()
        self.init_data = None
        self.start_time = None
        self.session = None
        
        self.display_name = session_name[:14]
        self.is_ready = False

    # ---------- TELEGRAM SESSION (WITH SEMAPHORE) ----------
    async def initialize_telethon(self):
        """Login with semaphore - max 10 concurrent logins"""
        async with login_semaphore:
            await update_progress(self.display_name, status='login', action='Logging in...')
            
            self.client = TelegramClient(self.session_path, API_ID, API_HASH)
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await update_progress(self.display_name, status='error', action='Unauthorized!')
                return False
            
            me = await self.client.get_me()
            self.telegram_id = str(me.id)
            self.username = me.username or f"user_{me.id}"
            self.first_name = me.first_name or "User"
            
            await update_progress(self.display_name, status='login', action='Logged in ✅')
            return True

    async def join_channels(self):
        for channel in REQUIRED_CHANNELS:
            try:
                await self.client(JoinChannelRequest(channel))
            except:
                pass
            await asyncio.sleep(0.2)

    async def send_start_with_referral(self):
        try:
            bot_entity = await self.client.get_input_entity(BOT_USERNAME)
            await self.client.send_message(bot_entity, f"/start {REFERRAL_CODE}")
            await asyncio.sleep(0.5)
            return True
        except:
            try:
                bot_entity = await self.client.get_input_entity(BOT_USERNAME)
                await self.client.send_message(bot_entity, "/start")
                await asyncio.sleep(0.5)
                return True
            except:
                return False

    async def get_init_data(self):
        await update_progress(self.display_name, action='Getting auth...')
        try:
            bot_entity = await self.client.get_input_entity(BOT_USERNAME)
            await self.send_start_with_referral()
            webview_url = f"{BASE_URL}?startapp={REFERRAL_CODE}"
            result = await self.client(RequestWebViewRequest(
                peer=bot_entity,
                bot=bot_entity,
                platform='android',
                from_bot_menu=False,
                url=webview_url
            ))
            raw_init_data = result.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
            self.init_data = urllib.parse.unquote(raw_init_data)
            return True
        except:
            await update_progress(self.display_name, status='error', action='Auth failed')
            return False

    # ---------- HTTP REQUESTS ----------
    async def _post(self, url, **kwargs):
        async with api_semaphore:
            return await self.session.post(url, **kwargs)

    async def _get(self, url, **kwargs):
        async with api_semaphore:
            return await self.session.get(url, **kwargs)

    async def fetch_status(self):
        url = f"{BASE_URL}/api/gram/status/{self.telegram_id}"
        try:
            async with await self._get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                elif resp.status == 400:
                    return {'limit_reached': True}
                return None
        except:
            return None

    async def register_user(self):
        url = f"{BASE_URL}/api/users/register"
        payload = {
            "telegram_id": int(self.telegram_id),
            "username": self.username,
            "first_name": self.first_name,
            "ref": REFERRAL_CODE
        }
        try:
            async with await self._post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.balance = float(data.get("balance", 0))
                    self.start_balance = self.balance
                    await update_progress(self.display_name, balance=self.balance)
                    return True
                return False
        except:
            return False

    async def check_channel_status(self):
        url = f"{BASE_URL}/api/users/channel-status"
        params = {"telegram_id": self.telegram_id, "_t": int(time.time() * 1000)}
        try:
            async with await self._get(url, params=params, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.channels_verified = data.get("all_joined", False)
                    return data
        except:
            pass
        return None

    async def verify_channels(self):
        url = f"{BASE_URL}/api/users/verify-channels"
        payload = {"telegram_id": self.telegram_id}
        try:
            async with await self._post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        self.channels_verified = True
                        if data.get("reward_granted", False):
                            self.balance = data.get("new_balance", self.balance)
                            await update_progress(self.display_name, balance=self.balance)
                        return True
        except:
            pass
        return False

    # ---------- ADS ----------
    async def start_watch(self, provider):
        url = f"{BASE_URL}/api/gram/start-watch"
        payload = {"telegram_id": self.telegram_id, "provider": provider}
        try:
            async with await self._post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return data.get("session_token")
        except:
            pass
        return None

    async def watch_ad(self, provider, session_token):
        url = f"{BASE_URL}/api/gram/watch-ad"
        payload = {"telegram_id": self.telegram_id, "provider": provider, "session_token": session_token}
        try:
            async with await self._post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return True, data
                elif resp.status == 400:
                    return False, {'limit_reached': True}
        except:
            pass
        return False, {}

    async def watch_single_ad(self, provider):
        provider_name = "Monetag" if provider == "monetag" else "Gigapub"
        await update_progress(self.display_name, action=f'Watching {provider_name}...')
        
        session_token = await self.start_watch(provider)
        if not session_token:
            return False
        
        await asyncio.sleep(15)
        
        success, data = await self.watch_ad(provider, session_token)
        if success:
            if provider == "monetag":
                self.monetag_count = data.get("monetag_ads_watched_today", self.monetag_count + 1)
                if self.monetag_count >= MONETAG_LIMIT:
                    self.monetag_limit_reached = True
            else:
                self.gigapub_count = data.get("gigapub_ads_watched_today", self.gigapub_count + 1)
                if self.gigapub_count >= GIGAPUB_LIMIT:
                    self.gigapub_limit_reached = True
            
            self.total_ads = data.get("ads_watched_today", self.total_ads + 1)
            self.balance = data.get("new_balance", self.balance)
            self.total_earned += data.get("reward", 0)
            
            await update_progress(
                self.display_name,
                monetag=self.monetag_count,
                gigapub=self.gigapub_count,
                tasks=self.task_count,
                total_ads=self.total_ads,
                balance=self.balance,
                status='working'
            )
            return True
        elif data.get('limit_reached'):
            if provider == "monetag":
                self.monetag_limit_reached = True
                self.monetag_count = MONETAG_LIMIT
            else:
                self.gigapub_limit_reached = True
                self.gigapub_count = GIGAPUB_LIMIT
            await update_progress(
                self.display_name,
                monetag=self.monetag_count,
                gigapub=self.gigapub_count,
                tasks=self.task_count
            )
            return False
        return False

    # ---------- TASKS ----------
    async def complete_task(self, task_id=16, max_retries=2):
        await update_progress(self.display_name, action='Doing task...')
        
        url = f"{BASE_URL}/api/tasks/complete"
        payload = {
            "telegram_id": self.telegram_id,
            "task_id": task_id,
            "proof_screenshot_url": None,
            "proof_url": None,
            "telegram_user": {
                "id": int(self.telegram_id),
                "first_name": self.first_name,
                "last_name": "",
                "username": self.username,
                "language_code": "en",
                "allows_write_to_pm": True
            }
        }

        retries = 0
        while retries < max_retries:
            try:
                async with await self._post(url, json=payload, headers=self.headers) as resp:
                    if resp.status == 400:
                        self.task_limit_reached = True
                        self.task_count = TASK_LIMIT
                        await update_progress(self.display_name, tasks=self.task_count, status='working')
                        return False, "daily_limit"
                    if resp.status == 429:
                        await asyncio.sleep(1)
                        retries += 1
                        continue
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('status') == 'approved':
                            earned = data.get('tokens_earned', 0)
                            self.balance = data.get('new_balance', self.balance)
                            self.task_count += 1
                            self.total_earned += earned
                            await update_progress(
                                self.display_name,
                                tasks=self.task_count,
                                balance=self.balance
                            )
                            return True, "success"
                        else:
                            return False, data.get('status', 'unknown')
                    retries += 1
                    await asyncio.sleep(0.5)
            except:
                retries += 1
                await asyncio.sleep(0.5)

        return False, "max_retries"

    async def update_from_status_api(self):
        status_data = await self.fetch_status()
        if status_data:
            if status_data.get('limit_reached'):
                self.monetag_count = MONETAG_LIMIT
                self.gigapub_count = GIGAPUB_LIMIT
                self.monetag_limit_reached = True
                self.gigapub_limit_reached = True
                await update_progress(
                    self.display_name,
                    monetag=self.monetag_count,
                    gigapub=self.gigapub_count,
                    status='working'
                )
                return
            
            self.monetag_count = status_data.get('monetag_ads_watched_today', self.monetag_count)
            self.gigapub_count = status_data.get('gigapub_ads_watched_today', self.gigapub_count)
            self.total_ads = status_data.get('ads_watched_today', self.total_ads)
            
            if self.monetag_count >= MONETAG_LIMIT:
                self.monetag_limit_reached = True
            if self.gigapub_count >= GIGAPUB_LIMIT:
                self.gigapub_limit_reached = True
            
            await update_progress(
                self.display_name,
                monetag=self.monetag_count,
                gigapub=self.gigapub_count,
                total_ads=self.total_ads,
                balance=self.balance
            )

    # ---------- PARALLEL ACTIONS ----------
    async def run_parallel_actions(self):
        await self.update_from_status_api()
        
        tasks = []
        
        if not self.channels_verified:
            await self.check_channel_status()
            if not self.channels_verified:
                await self.verify_channels()
        
        if not self.task_limit_reached and self.task_count < TASK_LIMIT:
            tasks.append(self.complete_task())
        
        if not self.monetag_limit_reached and self.monetag_count < MONETAG_LIMIT:
            tasks.append(self.watch_single_ad("monetag"))
        
        if not self.gigapub_limit_reached and self.gigapub_count < GIGAPUB_LIMIT:
            tasks.append(self.watch_single_ad("gigapub"))
        
        if not tasks:
            return False

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            
            if i == 0 and not self.task_limit_reached:
                if isinstance(result, tuple):
                    success, status = result
                    if status == "daily_limit":
                        self.task_limit_reached = True
                        self.task_count = TASK_LIMIT
                    elif success:
                        self.task_count += 1
            
            elif i == 1 and not self.monetag_limit_reached:
                if result:
                    self.monetag_count += 1
                    if self.monetag_count >= MONETAG_LIMIT:
                        self.monetag_limit_reached = True
            
            elif i == 2 and not self.gigapub_limit_reached:
                if result:
                    self.gigapub_count += 1
                    if self.gigapub_count >= GIGAPUB_LIMIT:
                        self.gigapub_limit_reached = True

        await update_progress(
            self.display_name,
            monetag=self.monetag_count,
            gigapub=self.gigapub_count,
            tasks=self.task_count,
            balance=self.balance,
            total_ads=self.total_ads
        )
        
        return True

    # ---------- MAIN LOOP ----------
    async def run_until_limits(self):
        await update_progress(self.display_name, status='login', action='Initializing...')
        
        if not await self.initialize_telethon():
            await update_progress(self.display_name, status='error', action='Auth failed')
            return
        
        await update_progress(self.display_name, action='Joining channels...')
        await self.join_channels()
        
        if not await self.get_init_data():
            return

        async with aiohttp.ClientSession() as self.session:
            self.headers['Origin'] = BASE_URL
            self.headers['Referer'] = f"{BASE_URL}/?startapp={REFERRAL_CODE}"

            await update_progress(self.display_name, action='Registering...')
            if not await self.register_user():
                await update_progress(self.display_name, status='error', action='Register failed')
                return

            await self.check_channel_status()
            if not self.channels_verified:
                await self.verify_channels()

            await self.update_from_status_api()
            
            if not self.task_limit_reached:
                success, status = await self.complete_task()
                if status == "daily_limit":
                    self.task_limit_reached = True
                    self.task_count = TASK_LIMIT
                elif success:
                    self.task_count += 1

            await update_progress(
                self.display_name,
                monetag=self.monetag_count,
                gigapub=self.gigapub_count,
                tasks=self.task_count,
                total_ads=self.total_ads,
                balance=self.balance,
                status='working',
                action='Farming... 🚀'
            )

            # ✅ FAST LOOP - sab accounts ek saath full speed
            while not self.all_limits_reached():
                await self.run_parallel_actions()
                await asyncio.sleep(0.1)  # ✅ Minimal delay for max speed

            await self.get_final_balance()
            
            await self.update_from_status_api()
            
            await update_progress(
                self.display_name,
                status='done',
                action='COMPLETE! 🎉',
                monetag=self.monetag_count,
                gigapub=self.gigapub_count,
                tasks=self.task_count,
                total_ads=self.total_ads,
                balance=self.balance
            )

        if self.client:
            await self.client.disconnect()

    async def get_final_balance(self):
        url = f"{BASE_URL}/api/users/register"
        payload = {
            "telegram_id": int(self.telegram_id),
            "username": self.username,
            "first_name": self.first_name,
            "ref": REFERRAL_CODE
        }
        try:
            async with await self._post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.balance = float(data.get("balance", self.balance))
                    await update_progress(self.display_name, balance=self.balance)
        except:
            pass

    def all_limits_reached(self):
        return (self.monetag_count >= MONETAG_LIMIT and
                self.gigapub_count >= GIGAPUB_LIMIT and
                self.task_count >= TASK_LIMIT)

# ============================================================
# MAIN EXECUTION
# ============================================================

async def progress_display_task():
    while True:
        await display_progress()
        await asyncio.sleep(0.5)  # ✅ Faster updates

async def process_account(session_path):
    session_name = os.path.basename(session_path).replace(".session", "")
    bot = Tasky3AutoBot(session_path, session_name)
    await bot.run_until_limits()

async def main():
    print_banner()
    
    session_folder = "sessions"
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
        print(f"{C.YEL}📁 Created 'sessions' folder. Place .session files there!{C.RES}")
        return

    sessions = glob.glob(os.path.join(session_folder, "*.session"))
    if not sessions:
        print(f"{C.RED}❌ NO SESSION FILES FOUND!{C.RES}")
        return

    print(f"{C.CYA}🚀 Found {len(sessions)} account(s){C.RES}")
    print(f"{C.CYA}🔐 Login batch size: {LOGIN_BATCH_SIZE} accounts at a time{C.RES}")
    print(f"{C.CYA}⚡ ScriptiFy {C.RES}\n")
    await asyncio.sleep(2)

    progress_task = asyncio.create_task(progress_display_task())
    
    # ✅ 
    tasks = [process_account(session_path) for session_path in sessions]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    progress_task.cancel()
    try:
        await progress_task
    except asyncio.CancelledError:
        pass
    
    await display_progress()
    print(f"\n{C.GRE}✅ ACCOUNT COMPLETED!{C.RES}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.RED}⛔ Stopped by user{C.RES}")
