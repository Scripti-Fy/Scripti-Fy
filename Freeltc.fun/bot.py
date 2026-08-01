import ssl
import certifi
import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from datetime import datetime
import os
import sys
import getpass
import json
import random

# ========== TERMUX FIX ==========
# Disable SSL verification for Termux
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class FreeLTCFaucet:
    def __init__(self):
        self.base_url = "https://freeltc.fun"
        self.email = None
        self.password = None
        self.session = None
        self.csrf_token = None
        self.is_logged_in = False
        self.claim_count = 0
        self.max_claims = 1000
        self.failed_attempts = 0
        self.max_failed_attempts = 3
        self.config_file = "config.json"
        self.min_delay = 10
        self.max_delay = 15
        self.claim_failed = False
        self.manual_claim_required = False
        
    def load_config(self):
        """Load configuration from config.json"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'email' in config and 'password' in config:
                        self.email = config['email']
                        self.password = config['password']
                        print(f"{Colors.GREEN}📁 Loaded account: {self.email}{Colors.END}")
                        return True
            except Exception as e:
                print(f"{Colors.RED}Failed to load config: {e}{Colors.END}")
        return False
    
    def save_config(self, email, password):
        """Save configuration to config.json"""
        try:
            config = {
                'email': email,
                'password': password,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"{Colors.GREEN}💾 Config saved successfully{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}Failed to save config: {e}{Colors.END}")
            return False
    
    def get_credentials(self):
        """Get credentials from config or user input"""
        if self.load_config():
            return True
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🔑 No saved account found. Please enter your credentials:{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.END}")
        
        email = input(f"{Colors.BLUE}📧 Email: {Colors.END}").strip()
        password = getpass.getpass(f"{Colors.BLUE}🔒 Password: {Colors.END}").strip()
        
        if not email or not password:
            print(f"{Colors.RED}❌ Email and password are required!{Colors.END}")
            return False
        
        self.email = email
        self.password = password
        self.save_config(email, password)
        return True
    
    def create_session(self):
        """Create a new session with SSL verification disabled for Termux"""
        self.session = requests.Session()
        
        # ========== TERMUX FIX ==========
        # Disable SSL verification
        self.session.verify = False
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8,pt;q=0.7,zh-CN;q=0.6,zh;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        self.csrf_token = None
        self.is_logged_in = False
    
    def get_random_delay(self):
        """Get random delay between 10-15 seconds"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_csrf_token(self, html_content):
        """Extract CSRF token from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try hidden input - FIXED: Use common token names
        token_names = ['_token', 'csrf_token', 'csrf_token_name', 'csrf-token']
        for name in token_names:
            csrf_input = soup.find('input', {'name': name})
            if csrf_input and csrf_input.get('value'):
                return csrf_input.get('value')
        
        # Try meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta and csrf_meta.get('content'):
            return csrf_meta.get('content')
        
        # Try JavaScript
        script_pattern = re.compile(r'csrf_token_name\s*=\s*["\']([^"\']+)["\']')
        match = script_pattern.search(html_content)
        if match:
            return match.group(1)
        
        # Try form
        form_pattern = re.compile(r'name="([^"]+)"\s+value="([^"]+)"')
        matches = form_pattern.findall(html_content)
        for name, value in matches:
            if 'token' in name.lower():
                return value
        
        return None
    
    def login(self):
        """Perform fresh login - FIXED for Termux"""
        self.create_session()
        
        print(f"{Colors.BLUE}🔑 Logging in: {self.email}{Colors.END}")
        
        try:
            # Get login page for CSRF token
            login_page = self.session.get(
                urljoin(self.base_url, '/login'),
                timeout=15,
                allow_redirects=True
            )
            
            if login_page.status_code != 200:
                print(f"{Colors.RED}Failed to get login page: {login_page.status_code}{Colors.END}")
                return False
            
            csrf_token = self.get_csrf_token(login_page.text)
            if not csrf_token:
                print(f"{Colors.RED}Failed to extract CSRF token{Colors.END}")
                # Try to get token from cookies
                for cookie in self.session.cookies:
                    if 'token' in cookie.name.lower() or 'csrf' in cookie.name.lower():
                        self.csrf_token = cookie.value
                        print(f"{Colors.CYAN}Using CSRF from cookie: {cookie.name}={cookie.value[:20]}...{Colors.END}")
                        break
                if not self.csrf_token:
                    return False
            else:
                self.csrf_token = csrf_token
                print(f"{Colors.CYAN}CSRF token found: {csrf_token[:30]}...{Colors.END}")
            
            # Login data - FIXED: Use _token
            login_data = {
                '_token': self.csrf_token,
                'email': self.email,
                'password': self.password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'Referer': urljoin(self.base_url, '/login')
            }
            
            # Perform login - FIXED: Post to /login
            login_response = self.session.post(
                urljoin(self.base_url, '/login'),
                data=login_data,
                headers=headers,
                allow_redirects=True,
                timeout=15
            )
            
            # Check if login successful
            if 'dashboard' in login_response.url.lower() or 'logout' in login_response.text.lower() or 'Welcome' in login_response.text:
                self.is_logged_in = True
                self.failed_attempts = 0
                print(f"{Colors.GREEN}✅ Login successful!{Colors.END}")
                
                # Update CSRF token
                for cookie in self.session.cookies:
                    if 'csrf' in cookie.name.lower() or 'token' in cookie.name.lower():
                        self.csrf_token = cookie.value
                        break
                
                return True
            else:
                print(f"{Colors.RED}Login failed - redirect to: {login_response.url}{Colors.END}")
                return False
                
        except requests.RequestException as e:
            print(f"{Colors.RED}Login failed: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Unexpected login error: {e}{Colors.END}")
            return False
    
    def get_faucet_page(self):
        """Get faucet page"""
        if not self.is_logged_in:
            return None
        
        try:
            response = self.session.get(
                urljoin(self.base_url, '/faucet'),
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"{Colors.RED}Failed to get faucet: {response.status_code}{Colors.END}")
                return None
            
            if 'Login' in response.text and 'Log In' in response.text:
                print(f"{Colors.YELLOW}⚠️ Redirected to login page{Colors.END}")
                self.is_logged_in = False
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Update CSRF token
            csrf_token = self.get_csrf_token(response.text)
            if csrf_token:
                self.csrf_token = csrf_token
            
            # Check if claim already made
            success_msg = soup.find('div', {'class': 'alert-success'})
            if success_msg:
                print(f"{Colors.GREEN}✅ {success_msg.text.strip()}{Colors.END}")
                return {'success': True, 'message': success_msg.text.strip()}
            
            # Check for captcha or error message
            error_msg = soup.find('div', {'class': 'alert-danger'})
            if error_msg:
                error_text = error_msg.text.strip()
                if 'captcha' in error_text.lower() or 'verify' in error_text.lower():
                    print(f"{Colors.RED}❌ CAPTCHA Required: {error_text}{Colors.END}")
                    return {'captcha_required': True, 'message': error_text}
                else:
                    print(f"{Colors.YELLOW}⚠️ Error: {error_text}{Colors.END}")
                    return {'error': True, 'message': error_text}
            
            details = {}
            
            # Claims left
            claims_left = soup.find('strong', string=re.compile(r'\d+\s*/\s*\d+'))
            if claims_left:
                details['claims_left'] = claims_left.text.strip()
                numbers = re.findall(r'\d+', claims_left.text)
                if len(numbers) >= 2:
                    current, total = map(int, numbers[:2])
                    if current <= 0:
                        print(f"{Colors.YELLOW}⚠️ Daily limit reached!{Colors.END}")
                        return {'limit_reached': True}
            
            return details
            
        except requests.RequestException as e:
            print(f"{Colors.RED}Failed to get faucet: {e}{Colors.END}")
            return None
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.END}")
            return None
    
    def claim_faucet(self):
        """Perform faucet claim"""
        if not self.is_logged_in:
            return False
        
        try:
            # First get faucet page
            faucet_data = self.get_faucet_page()
            if not faucet_data:
                return False
            
            if faucet_data.get('limit_reached'):
                self.max_claims = 0
                return False
            
            if faucet_data.get('success'):
                return True
            
            if faucet_data.get('captcha_required'):
                self.manual_claim_required = True
                self.show_captcha_instructions()
                return False
            
            if faucet_data.get('error'):
                print(f"{Colors.RED}❌ Error on faucet page: {faucet_data.get('message')}{Colors.END}")
                return False
            
            # Prepare claim - FIXED: Use _token
            claim_data = {
                '_token': self.csrf_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'Referer': urljoin(self.base_url, '/faucet')
            }
            
            # Perform claim
            claim_response = self.session.post(
                urljoin(self.base_url, '/faucet/verify'),
                data=claim_data,
                headers=headers,
                allow_redirects=True,
                timeout=15
            )
            
            if claim_response.status_code == 200:
                soup = BeautifulSoup(claim_response.text, 'html.parser')
                
                # Check for error/captcha
                error_msg = soup.find('div', {'class': 'alert-danger'})
                if error_msg:
                    error_text = error_msg.text.strip()
                    if 'captcha' in error_text.lower() or 'verify' in error_text.lower():
                        print(f"{Colors.RED}❌ CAPTCHA Required: {error_text}{Colors.END}")
                        self.manual_claim_required = True
                        self.show_captcha_instructions()
                        return False
                    else:
                        print(f"{Colors.RED}❌ Claim error: {error_text}{Colors.END}")
                        return False
                
                success_msg = soup.find('div', {'class': 'alert-success'})
                if success_msg:
                    self.claim_count += 1
                    self.failed_attempts = 0
                    print(f"{Colors.GREEN}✅ Claim #{self.claim_count}: {success_msg.text.strip()}{Colors.END}")
                    
                    # Update CSRF token
                    new_token = self.get_csrf_token(claim_response.text)
                    if new_token:
                        self.csrf_token = new_token
                    
                    return True
                else:
                    print(f"{Colors.YELLOW}⚠️ No success message found{Colors.END}")
                    return False
            else:
                print(f"{Colors.RED}Claim failed: {claim_response.status_code}{Colors.END}")
                return False
                
        except requests.RequestException as e:
            print(f"{Colors.RED}Claim failed: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Unexpected claim error: {e}{Colors.END}")
            return False
    
    def show_captcha_instructions(self):
        """Show instructions for manual captcha solving"""
        print(f"\n{Colors.BOLD}{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}🔐 CAPTCHA DETECTED!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'='*60}{Colors.END}")
        print(f"\n{Colors.YELLOW}⚠️  The bot has detected a CAPTCHA verification.{Colors.END}")
        print(f"{Colors.CYAN}📌 Please complete the following steps manually:{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}1️⃣{Colors.END} {Colors.BLUE}Go to the website in your browser:{Colors.END}")
        print(f"   {Colors.CYAN}{self.base_url}/faucet{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}2️⃣{Colors.END} {Colors.BLUE}Complete the CAPTCHA verification{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}3️⃣{Colors.END} {Colors.BLUE}Claim the faucet {Colors.BOLD}{Colors.RED}TWO{Colors.END} {Colors.BLUE}times manually{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}4️⃣{Colors.END} {Colors.BLUE}Press {Colors.BOLD}{Colors.YELLOW}ENTER{Colors.END} {Colors.BLUE}after completing both claims{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.RED}{'='*60}{Colors.END}")
        
        input(f"\n{Colors.GREEN}✅ Press ENTER after completing CAPTCHA and 2 manual claims...{Colors.END}")
        
        self.manual_claim_required = False
        self.failed_attempts = 0
        
        print(f"{Colors.BLUE}🔄 Re-logging after manual claims...{Colors.END}")
        time.sleep(3)
    
    def run_infinite_loop(self):
        """Main loop with auto-relogin on failure"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🚀 Starting infinite faucet claim loop{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}📊 Daily limit: {self.max_claims} claims{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}⏱️  Random delays: {self.min_delay}-{self.max_delay}s between claims{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}⏹️  Press Ctrl+C to stop{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        while True:
            try:
                if self.manual_claim_required:
                    self.show_captcha_instructions()
                    continue
                
                if not self.login():
                    print(f"{Colors.RED}❌ Login failed, retrying in 10s...{Colors.END}")
                    time.sleep(10)
                    continue
                
                while True:
                    try:
                        if self.manual_claim_required:
                            break
                        
                        faucet_data = self.get_faucet_page()
                        if not faucet_data:
                            print(f"{Colors.YELLOW}⚠️ Failed to get faucet page{Colors.END}")
                            time.sleep(self.get_random_delay())
                            continue
                        
                        if faucet_data.get('limit_reached'):
                            print(f"{Colors.YELLOW}🎯 Daily limit reached! Waiting 6 hours...{Colors.END}")
                            time.sleep(6 * 60 * 60)
                            continue
                        
                        if faucet_data.get('captcha_required'):
                            self.manual_claim_required = True
                            break
                        
                        if self.claim_faucet():
                            wait_time = self.get_random_delay()
                            print(f"{Colors.CYAN}⏳ Waiting {wait_time:.2f}s for next claim...{Colors.END}")
                            time.sleep(wait_time)
                        else:
                            print(f"{Colors.YELLOW}⚠️ Claim failed, waiting before retry...{Colors.END}")
                            wait_time = self.get_random_delay()
                            time.sleep(wait_time)
                            
                    except Exception as e:
                        print(f"{Colors.RED}❌ Claim loop error: {e}{Colors.END}")
                        time.sleep(self.get_random_delay())
                
                if self.manual_claim_required:
                    self.show_captcha_instructions()
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.RED}🛑 Stopped by user{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}📊 Total claims: {self.claim_count}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Fatal error: {e}{Colors.END}")
                time.sleep(10)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FreeLTC Faucet Automation')
    parser.add_argument('--once', '-o', action='store_true', help='Run once')
    parser.add_argument('--claims', '-c', type=int, default=1000, help='Daily claim limit')
    parser.add_argument('--min-delay', type=int, default=10, help='Minimum delay between claims (seconds)')
    parser.add_argument('--max-delay', type=int, default=15, help='Maximum delay between claims (seconds)')
    
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}🪙  FreeLTC Faucet Automation Bot{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    faucet = FreeLTCFaucet()
    faucet.max_claims = args.claims
    faucet.min_delay = args.min_delay
    faucet.max_delay = args.max_delay
    
    if not faucet.get_credentials():
        sys.exit(1)
    
    try:
        if args.once:
            if faucet.login():
                faucet.get_faucet_page()
                print(f"\n{Colors.GREEN}✅ Login successful. Use without --once for continuous claiming.{Colors.END}")
        else:
            faucet.run_infinite_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        raise

if __name__ == "__main__":
    main()
