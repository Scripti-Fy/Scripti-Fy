#!/usr/bin/env python3
"""
Session Creator for Paidz Bot
Creates only .session files without any claiming logic
"""

import os
import asyncio
import shutil

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
    
    # Check write permissions
    test_file = os.path.join(SESSIONS_DIR, ".test_write")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        print(f"{R}[✗] No write permission in {SESSIONS_DIR}: {e}{D}")
        return False
    return True

def get_all_sessions():
    """Get all session files"""
    if not os.path.exists(SESSIONS_DIR):
        return []
    
    sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    return sessions

def cleanup_corrupted_session(session_path):
    """Delete corrupted session files"""
    try:
        if os.path.exists(session_path):
            os.remove(session_path)
            print(f"{Y}[!] Removed corrupted session file{D}")
        # Also remove journal files if exist
        journal_path = session_path + "-journal"
        if os.path.exists(journal_path):
            os.remove(journal_path)
    except Exception as e:
        print(f"{Y}[!] Could not remove corrupted files: {e}{D}")

async def create_session():
    print(f"{C}\n╔══════════════════════════════════════════╗")
    print(f"║       Paidz SESSION CREATOR         ║")
    print(f"╚══════════════════════════════════════════╝{D}\n")
    
    # Check directory permissions
    if not ensure_session_dir():
        return
    
    # Show existing sessions count
    existing_sessions = get_all_sessions()
    if existing_sessions:
        print(f"{Y}[!] Existing sessions: {len(existing_sessions)}{D}")
        for session in existing_sessions:
            print(f"    • {session}")
        print()
    
    phone = input(f"{Y}[?] Enter phone number (with country code): {D}").strip()
    
    # Validate phone number (basic check)
    if not phone or len(phone) < 8:
        print(f"{R}[✗] Invalid phone number. Must include country code.{D}")
        return
    
    # Check if session with same phone exists
    session_filename = f"{phone}.session"
    session_path = os.path.join(SESSIONS_DIR, session_filename)
    
    if os.path.exists(session_path):
        overwrite = input(f"{Y}[!] Session for {phone} already exists. Overwrite? (y/n): {D}").lower()
        if overwrite != 'y':
            print(f"{Y}[!] Cancelled{D}")
            return
        # Clean up old session files
        cleanup_corrupted_session(session_path)
    
    # Create new session with fresh database
    try:
        # Create a fresh session file
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
                try:
                    await client.send_message(BOT_USERNAME, "/start")
                    print(f"{G}[✓] Test message sent to @{BOT_USERNAME}{D}")
                except Exception as e:
                    print(f"{Y}[!] Could not send test message: {e}{D}")
            
            # Force save session
            await client.disconnect()
            
        except Exception as e:
            print(f"\n{R}[✗] Failed to create session: {e}{D}")
            cleanup_corrupted_session(session_path)
            raise
        
    except Exception as e:
        print(f"\n{R}[✗] Error: {e}{D}")
        cleanup_corrupted_session(session_path)

async def list_sessions():
    sessions = get_all_sessions()
    if not sessions:
        print(f"{Y}[!] No sessions found{D}")
    else:
        print(f"\n{G}[✓] Total sessions: {len(sessions)}{D}")
        for idx, session in enumerate(sessions, 1):
            # Check file size
            session_path = os.path.join(SESSIONS_DIR, session)
            size = os.path.getsize(session_path)
            size_kb = size / 1024
            status = f"{G}✓{D}" if size > 0 else f"{R}✗{D}"
            print(f"    {idx}. {session} ({size_kb:.1f} KB) [{status}]")

async def delete_session():
    sessions = get_all_sessions()
    if not sessions:
        print(f"{Y}[!] No sessions found to delete{D}")
        return
    
    print(f"\n{G}[✓] Available sessions:{D}")
    for idx, session in enumerate(sessions, 1):
        print(f"    {idx}. {session}")
    
    try:
        choice = input(f"\n{Y}[?] Enter session number to delete (or 'all' for all): {D}").strip()
        
        if choice.lower() == 'all':
            confirm = input(f"{Y}[!] Delete ALL sessions? (y/n): {D}").lower()
            if confirm == 'y':
                for session in sessions:
                    session_path = os.path.join(SESSIONS_DIR, session)
                    cleanup_corrupted_session(session_path)
                print(f"{G}[✓] All sessions deleted successfully!{D}")
            else:
                print(f"{Y}[!] Cancelled{D}")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                session = sessions[idx]
                confirm = input(f"{Y}[!] Delete session {session}? (y/n): {D}").lower()
                if confirm == 'y':
                    session_path = os.path.join(SESSIONS_DIR, session)
                    cleanup_corrupted_session(session_path)
                    print(f"{G}[✓] Session deleted successfully!{D}")
                else:
                    print(f"{Y}[!] Cancelled{D}")
            else:
                print(f"{R}[✗] Invalid session number{D}")
    except (ValueError, IndexError):
        print(f"{R}[✗] Invalid input{D}")

async def fix_sessions():
    """Fix corrupted sessions"""
    sessions = get_all_sessions()
    if not sessions:
        print(f"{Y}[!] No sessions found to fix{D}")
        return
    
    print(f"\n{G}[✓] Checking sessions...{D}")
    fixed = 0
    for session in sessions:
        session_path = os.path.join(SESSIONS_DIR, session)
        size = os.path.getsize(session_path)
        if size < 1024:  # Less than 1KB likely corrupted
            print(f"{Y}[!] Found corrupted session: {session} (size: {size} bytes){D}")
            cleanup_corrupted_session(session_path)
            fixed += 1
    
    print(f"{G}[✓] Fixed {fixed} corrupted sessions{D}")

async def main():
    print(f"{C}\n╔══════════════════════════════════════════╗")
    print(f"║       Paidz SESSION MANAGER          ║")
    print(f"╚══════════════════════════════════════════╝{D}\n")
    
    if not ensure_session_dir():
        print(f"{R}[✗] Cannot proceed without proper permissions{D}")
        return
    
    while True:
        print(f"\n{C}════════════════════════════════════════{D}")
        print(f"{Y}[1] Create new session{D}")
        print(f"{Y}[2] List all sessions{D}")
        print(f"{Y}[3] Delete session{D}")
        print(f"{Y}[4] Fix corrupted sessions{D}")
        print(f"{Y}[5] Exit{D}")
        print(f"{C}════════════════════════════════════════{D}")
        
        choice = input(f"\n{Y}[?] Select option: {D}").strip()
        
        if choice == '1':
            await create_session()
        elif choice == '2':
            await list_sessions()
        elif choice == '3':
            await delete_session()
        elif choice == '4':
            await fix_sessions()
        elif choice == '5':
            print(f"{G}[✓] Goodbye!{D}")
            break
        else:
            print(f"{R}[✗] Invalid option{D}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Cancelled{D}")
    except Exception as e:
        print(f"\n{R}[✗] Fatal error: {e}{D}")
