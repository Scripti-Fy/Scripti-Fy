#!/usr/bin/env python3
"""
Session Creator
Creates only .session files without any claiming logic
"""

import os
import asyncio

try:
    from telethon import TelegramClient
except ImportError:
    print("\033[1;31m[!] Telethon not found. Run: pip install telethon\033[0m")
    exit(1)

# Configuration
API_ID = 21518358
API_HASH = "3c9576476fb4d4456b98d5619c9c0f3d"
SESSIONS_DIR = "sessions"
BOT_USERNAME = "litebits_faucet_bot"

# Colors
G = "\033[1;92m"
C = "\033[1;96m"
Y = "\033[1;93m"
R = "\033[1;91m"
D = "\033[0m"

def ensure_session_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
        print(f"{G}[✓] Created {SESSIONS_DIR} directory{D}")

def get_existing_session():
    """Check if any session file exists"""
    if not os.path.exists(SESSIONS_DIR):
        return None
    
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    if sessions:
        return sessions[0]
    return None

async def create_session():
    print(f"{C}\n╔══════════════════════════════════════════╗")
    print(f"║        SESSION CREATOR         ║")
    print(f"╚══════════════════════════════════════════╝{D}\n")
    
    # Check for existing session first
    existing_session = get_existing_session()
    if existing_session:
        print(f"{Y}[!] You already have a session: {existing_session}{D}")
        print(f"{Y}[!] Only one session is allowed{D}")
        return
    
    phone = input(f"{Y}[?] Enter phone number (with country code): {D}").strip()
    
    session_path = os.path.join(SESSIONS_DIR, f"{phone}.session")
    
    client = TelegramClient(session_path, API_ID, API_HASH)
    
    try:
        await client.start(phone=phone)
        me = await client.get_me()
        
        print(f"\n{G}[✓] Session created successfully!{D}")
        print(f"    Name: {me.first_name} {me.last_name or ''}")
        print(f"    Username: @{me.username or 'None'}")
        print(f"    User ID: {me.id}")
        print(f"    File: {session_path}")
        
        # Optional: Send a test message to the bot
        send_test = input(f"\n{Y}[?] Send test message to bot? (y/n): {D}").lower()
        if send_test == 'y':
            await client.send_message(BOT_USERNAME, "/start")
            print(f"{G}[✓] Test message sent to @{BOT_USERNAME}{D}")
        
    except Exception as e:
        print(f"\n{R}[✗] Failed: {e}{D}")
        if os.path.exists(session_path):
            os.remove(session_path)
    finally:
        await client.disconnect()

async def list_sessions():
    existing_session = get_existing_session()
    if not existing_session:
        print(f"{Y}[!] No session found{D}")
    else:
        print(f"\n{G}[✓] Existing session:{D}")
        print(f"    {existing_session}")

async def delete_session():
    existing_session = get_existing_session()
    if not existing_session:
        print(f"{Y}[!] No session found to delete{D}")
        return
    
    confirm = input(f"{Y}[!] Delete session {existing_session}? (y/n): {D}").lower()
    if confirm == 'y':
        session_path = os.path.join(SESSIONS_DIR, existing_session)
        os.remove(session_path)
        print(f"{G}[✓] Session deleted successfully!{D}")
    else:
        print(f"{Y}[!] Cancelled{D}")

async def main():
    ensure_session_dir()
    
    while True:
        print(f"\n{C}════════════════════════════════════════{D}")
        print(f"{Y}[1] Create new session{D}")
        print(f"{Y}[2] Check existing session{D}")
        print(f"{Y}[3] Delete session{D}")
        print(f"{Y}[4] Exit{D}")
        print(f"{C}════════════════════════════════════════{D}")
        
        choice = input(f"\n{Y}[?] Select option: {D}").strip()
        
        if choice == '1':
            await create_session()
        elif choice == '2':
            await list_sessions()
        elif choice == '3':
            await delete_session()
        elif choice == '4':
            print(f"{G}[✓] Goodbye!{D}")
            break
        else:
            print(f"{R}[✗] Invalid option{D}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Cancelled{D}")
