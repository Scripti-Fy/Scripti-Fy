#!/usr/bin/env python3
"""
Session Creator for reward bots Bot
Creates only .session files without any claiming logic
"""

import os
import asyncio
import re
import sys

try:
    from telethon import TelegramClient
except ImportError:
    print("\033[1;31m[!] Telethon not found. Run: pip install telethon\033[0m")
    exit(1)

# Configuration
API_ID = 21518358
API_HASH = "3c9576476fb4d4456b98d5619c9c0f3d"
BOT_USERNAME = "reward bots_faucet_bot"

# Colors
G = "\033[1;92m"
C = "\033[1;96m"
Y = "\033[1;93m"
R = "\033[1;91m"
D = "\033[0m"

def get_next_session_number():
    """Find the next available session number"""
    try:
        session_files = [f for f in os.listdir('.') if f.startswith('session') and f.endswith('.session')]
    except:
        return 1
    
    if not session_files:
        return 1
    
    numbers = []
    for f in session_files:
        match = re.match(r'session(\d+)\.session', f)
        if match:
            numbers.append(int(match.group(1)))
    
    if not numbers:
        return 1
    
    numbers.sort()
    next_num = 1
    for num in numbers:
        if num == next_num:
            next_num += 1
        else:
            break
    
    return next_num

def validate_phone(phone):
    """Validate phone number format"""
    # Remove any spaces or special characters
    phone = re.sub(r'[\s\+\-\(\)]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits)
    if not phone.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(phone) < 10 or len(phone) > 15:
        return False, "Phone number must be between 10-15 digits"
    
    # For Indian numbers, check if it starts with 91 and has 12 digits
    if phone.startswith('91') and len(phone) == 12:
        return True, phone
    
    # For other formats, allow
    return True, phone

async def create_session():
    print(f"{C}\n╔══════════════════════════════════════════╗")
    print(f"║       REWARD BOTS SESSION CREATOR      ║")
    print(f"╚══════════════════════════════════════════╝{D}\n")
    
    while True:
        phone = input(f"{Y}[?] Enter phone number (with country code): {D}").strip()
        
        # Validate phone number
        is_valid, phone_clean = validate_phone(phone)
        if not is_valid:
            print(f"{R}[✗] Invalid phone number: {phone_clean}{D}")
            retry = input(f"{Y}[?] Try again? (y/n): {D}").lower()
            if retry != 'y':
                return
            continue
        
        # For Indian numbers, suggest correction
        if len(phone_clean) == 10 and not phone_clean.startswith('91'):
            suggestion = f"91{phone_clean}"
            print(f"{Y}[!] Did you mean: {suggestion}?{D}")
            use_suggestion = input(f"{Y}[?] Use this instead? (y/n): {D}").lower()
            if use_suggestion == 'y':
                phone_clean = suggestion
        
        break
    
    # Get next available session number
    session_num = get_next_session_number()
    session_path = f"session{session_num}.session"
    
    print(f"{G}[✓] Will create: {session_path}{D}")
    print(f"{G}[✓] Phone: {phone_clean}{D}")
    
    # Check if file already exists
    if os.path.exists(session_path):
        overwrite = input(f"{Y}[!] Session exists. Overwrite? (y/n): {D}").lower()
        if overwrite != 'y':
            print(f"{Y}[!] Aborted{D}")
            return
    
    # Create client with proper session path
    try:
        client = TelegramClient(session_path, API_ID, API_HASH)
        
        # Start with phone
        await client.start(phone=phone_clean)
        me = await client.get_me()
        
        print(f"\n{G}[✓] Session created successfully!{D}")
        print(f"    Name: {me.first_name} {me.last_name or ''}")
        print(f"    Username: @{me.username or 'None'}")
        print(f"    User ID: {me.id}")
        print(f"    File: {session_path}")
        print(f"    Phone: {phone_clean}")
        
        # Save mapping
        mapping_file = "session_mapping.txt"
        try:
            with open(mapping_file, 'a') as f:
                f.write(f"{session_path} = {phone_clean}\n")
            print(f"{G}[✓] Session mapping saved to {mapping_file}{D}")
        except:
            print(f"{Y}[!] Could not save mapping file{D}")
        
        # Optional: Send test message
        send_test = input(f"\n{Y}[?] Send test message to bot? (y/n): {D}").lower()
        if send_test == 'y':
            try:
                await client.send_message(BOT_USERNAME, "/start")
                print(f"{G}[✓] Test message sent to @{BOT_USERNAME}{D}")
            except Exception as e:
                print(f"{Y}[!] Could not send test message: {e}{D}")
        
        # Disconnect properly
        await client.disconnect()
        
    except Exception as e:
        print(f"\n{R}[✗] Failed to create session: {e}{D}")
        print(f"{Y}[!] Make sure:")
        print(f"    1. Phone number is correct")
        print(f"    2. You have internet connection")
        print(f"    3. Telegram API is accessible{D}")
        
        # Clean up partial session file
        if os.path.exists(session_path):
            try:
                os.remove(session_path)
                print(f"{G}[✓] Removed incomplete session file{D}")
            except:
                pass
    finally:
        try:
            await client.disconnect()
        except:
            pass

async def list_sessions():
    try:
        session_files = [f for f in os.listdir('.') if f.startswith('session') and f.endswith('.session')]
    except:
        session_files = []
    
    if not session_files:
        print(f"{Y}[!] No session files found in current directory{D}")
        return
    
    print(f"\n{G}[✓] Existing sessions:{D}")
    session_files.sort(key=lambda x: int(re.search(r'session(\d+)', x).group(1)) if re.search(r'session(\d+)', x) else 0)
    
    # Load mapping
    mapping = {}
    try:
        with open("session_mapping.txt", 'r') as f:
            for line in f:
                if '=' in line:
                    parts = line.strip().split('=')
                    if len(parts) == 2:
                        mapping[parts[0].strip()] = parts[1].strip()
    except:
        pass
    
    for session in session_files:
        phone = mapping.get(session, "Unknown")
        # Check file size
        size = os.path.getsize(session) if os.path.exists(session) else 0
        status = "✅" if size > 100 else "⚠️"
        print(f"    {status} {session} (Phone: {phone}, Size: {size} bytes)")

def cleanup_temp_files():
    """Remove temporary and corrupted session files"""
    try:
        for f in os.listdir('.'):
            if f.endswith('.session') and f.startswith('session'):
                if os.path.getsize(f) < 50:  # Too small = corrupted
                    os.remove(f)
                    print(f"{G}[✓] Removed corrupted: {f}{D}")
    except:
        pass

async def main():
    print(f"{C}\n╔══════════════════════════════════════════╗")
    print(f"║       REWARD BOTS SESSION CREATOR      ║")
    print(f"║    (Sessions saved in current dir)     ║")
    print(f"╚══════════════════════════════════════════╝{D}\n")
    
    # Check permissions
    try:
        test_file = ".test_write"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"{G}[✓] Write permissions OK{D}")
    except:
        print(f"{R}[✗] No write permission in current directory!{D}")
        print(f"{Y}[!] Try running with proper permissions or change directory{D}")
        return
    
    # Cleanup
    cleanup_temp_files()
    
    while True:
        print(f"\n{C}════════════════════════════════════════{D}")
        print(f"{Y}[1] Create new session{D}")
        print(f"{Y}[2] List existing sessions{D}")
        print(f"{Y}[3] Exit{D}")
        print(f"{C}════════════════════════════════════════{D}")
        
        choice = input(f"\n{Y}[?] Select option: {D}").strip()
        
        if choice == '1':
            await create_session()
        elif choice == '2':
            await list_sessions()
        elif choice == '3':
            print(f"{G}[✓] Goodbye!{D}")
            break
        else:
            print(f"{R}[✗] Invalid option. Please enter 1, 2, or 3{D}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Cancelled by user{D}")
    except Exception as e:
        print(f"\n{R}[✗] Unexpected error: {e}{D}")
        print(f"{Y}[!] Please restart the script{D}")
