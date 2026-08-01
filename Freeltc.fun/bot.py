import ssl
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

# ========== TERMUX FIX - MUST BE AT TOP ==========
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

# Force requests to ignore SSL
requests.packages.urllib3.disable_warnings()

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
        """Create a new session with SSL disabled for Termux"""
        self.session = requests.Session()
        
        # CRITICAL FIX FOR TERMUX
        self.session.verify = False
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8,pt;q=0.7,zh-CN;q=0.6,zh;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Ch-Ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        })
        self.csrf_token = None
        self.is_logged_in = False
    
    def get_random_delay(self):
        """Get random delay between 10-15 seconds"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_csrf_token(self, html_content):
        """Extract CSRF token from HTML - FIXED for Laravel"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try Laravel's _token first
        csrf_input = soup.find('input', {'name': '_token'})
        if csrf_input and csrf_input.get('value'):
            return csrf_input.get('value')
        
        # Try other common names
        token_names = ['csrf_token', 'csrf-token', 'token', 'csrf_token_name']
        for name in token_names:
            csrf_input = soup.find('input', {'name': name})
            if csrf_input and csrf_input.get('value'):
                return csrf_input.get('value')
        
        # Try meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta and csrf_meta.get('content'):
            return csrf_meta.get('content')
        
        # Try JavaScript
        script_patterns = [
            r'_token\s*[:=]\s*["\']([^"\']+)["\']',
            r'csrf_token\s*[:=]\s*["\']([^"\']+)["\']',
            r'token\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        for pattern in script_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Try form action
        form_pattern = re.compile(r'<form[^>]*>.*?name="([^"]+)"\s+value="([^"]+)"', re.DOTALL)
        matches = form_pattern.findall(html_content)
        for name, value in matches:
            if 'token' in name.lower():
                return value
        
        return None
    
    def login(self):
        """Perform fresh login - TERMUX OPTIMIZED"""
        self.create_session()
        
        print(f"{Colors.BLUE}🔑 Logging in: {self.email}{Colors.END}")
        
        try:
            # STEP 1: Get login page
            login_page = self.session.get(
                self.base_url + '/login',
                timeout=20,
                allow_redirects=True
            )
            
            if login_page.status_code != 200:
                print(f"{Colors.RED}Failed to get login page: {login_page.status_code}{Colors.END}")
                return False
            
            # STEP 2: Extract CSRF token
            self.csrf_token = self.get_csrf_token(login_page.text)
            
            if not self.csrf_token:
                print(f"{Colors.RED}❌ Failed to extract CSRF token{Colors.END}")
                # Try from cookies
                for cookie in self.session.cookies:
                    if 'XSRF-TOKEN' in cookie.name:
                        self.csrf_token = cookie.value
                        print(f"{Colors.GREEN}✅ Using XSRF-TOKEN from cookie{Colors.END}")
                        break
                    elif 'csrf' in cookie.name.lower():
                        self.csrf_token = cookie.value
                        print(f"{Colors.GREEN}✅ Using CSRF from cookie: {cookie.name}{Colors.END}")
                        break
                
                if not self.csrf_token:
                    return False
            else:
                print(f"{Colors.GREEN}✅ CSRF token extracted{Colors.END}")
            
            # STEP 3: Prepare login data
            login_data = {
                '_token': self.csrf_token,
                'email': self.email,
                'password': self.password
            }
            
            # STEP 4: Perform login
            login_response = self.session.post(
                self.base_url + '/login',
                data=login_data,
                allow_redirects=True,
                timeout=20
            )
            
            # STEP 5: Check if login successful
            if 'logout' in login_response.text.lower() or 'dashboard' in login_response.url.lower():
                self.is_logged_in = True
                self.failed_attempts = 0
                print(f"{Colors.GREEN}✅ Login successful!{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Login failed{Colors.END}")
                return False
                
        except requests.RequestException as e:
            print(f"{Colors.RED}Login error: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.END}")
            return False
    
    def get_faucet_page(self):
        """Get faucet page"""
        if not self.is_logged_in:
            return None
        
        try:
            response = self.session.get(
                self.base_url + '/faucet',
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"{Colors.RED}Failed to get faucet: {response.status_code}{Colors.END}")
                return None
            
            # Check if redirected to login
            if 'login' in response.url.lower():
                print(f"{Colors.YELLOW}⚠️ Redirected to login page{Colors.END}")
                self.is_logged_in = False
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Update CSRF token
            new_token = self.get_csrf_token(response.text)
            if new_token:
                self.csrf_token = new_token
            
            # Check for success message
            success_msg = soup.find('div', {'class': 'alert-success'})
            if success_msg:
                print(f"{Colors.GREEN}✅ {success_msg.text.strip()}{Colors.END}")
                return {'success': True, 'message': success_msg.text.strip()}
            
            # Check for error/captcha
            error_msg = soup.find('div', {'class': 'alert-danger'})
            if error_msg:
                error_text = error_msg.text.strip()
                if 'captcha' in error_text.lower() or 'verify' in error_text.lower():
                    print(f"{Colors.RED}❌ CAPTCHA Required{Colors.END}")
                    return {'captcha_required': True}
                else:
                    print(f"{Colors.YELLOW}⚠️ {error_text}{Colors.END}")
                    return {'error': True, 'message': error_text}
            
            # Check claims left
            claims_text = soup.find('strong', string=re.compile(r'\d+\s*/\s*\d+'))
            if claims_text:
                numbers = re.findall(r'\d+', claims_text.text)
                if len(numbers) >= 2:
                    current = int(numbers[0])
                    if current <= 0:
                        print(f"{Colors.YELLOW}⚠️ Daily limit reached!{Colors.END}")
                        return {'limit_reached': True}
            
            return {'ready': True}
            
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.END}")
            return None
    
    def claim_faucet(self):
        """Perform faucet claim"""
        if not self.is_logged_in:
            return False
        
        try:
            # Check faucet page first
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
                return False
            
            # Prepare claim data
            claim_data = {
                '_token': self.csrf_token
            }
            
            # Perform claim
            claim_response = self.session.post(
                self.base_url + '/faucet/verify',
                data=claim_data,
                allow_redirects=True,
                timeout=15
            )
            
            if claim_response.status_code == 200:
                soup = BeautifulSoup(claim_response.text, 'html.parser')
                
                # Check for success
                success_msg = soup.find('div', {'class': 'alert-success'})
                if success_msg:
                    self.claim_count += 1
                    print(f"{Colors.GREEN}✅ Claim #{self.claim_count}: {success_msg.text.strip()}{Colors.END}")
                    return True
                
                # Check for error
                error_msg = soup.find('div', {'class': 'alert-danger'})
                if error_msg:
                    error_text = error_msg.text.strip()
                    if 'captcha' in error_text.lower():
                        self.manual_claim_required = True
                        self.show_captcha_instructions()
                    else:
                        print(f"{Colors.RED}❌ {error_text}{Colors.END}")
                    return False
            
            return False
                
        except Exception as e:
            print(f"{Colors.RED}Claim error: {e}{Colors.END}")
            return False
    
    def show_captcha_instructions(self):
        """Show instructions for manual captcha solving"""
        print(f"\n{Colors.BOLD}{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}🔐 CAPTCHA DETECTED!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'='*60}{Colors.END}")
        print(f"\n{Colors.YELLOW}⚠️  Complete CAPTCHA manually in browser{Colors.END}")
        print(f"{Colors.CYAN}📌 Go to: {self.base_url}/faucet{Colors.END}")
        print(f"\n{Colors.BOLD}{Colors.GREEN}Press ENTER after completing CAPTCHA...{Colors.END}")
        
        input()
        self.manual_claim_required = False
        self.is_logged_in = False
        print(f"{Colors.BLUE}🔄 Re-logging...{Colors.END}")
        time.sleep(3)
    
    def run_infinite_loop(self):
        """Main loop"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}🚀 Starting infinite faucet claim loop{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}📊 Daily limit: {self.max_claims} claims{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}⏱️  Random delays: {self.min_delay}-{self.max_delay}s{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}⏹️  Press Ctrl+C to stop{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        while True:
            try:
                if self.manual_claim_required:
                    self.show_captcha_instructions()
                    continue
                
                if not self.is_logged_in:
                    if not self.login():
                        print(f"{Colors.RED}❌ Login failed, retrying in 10s...{Colors.END}")
                        time.sleep(10)
                        continue
                
                # Try to claim
                if self.claim_faucet():
                    wait_time = self.get_random_delay()
                    print(f"{Colors.CYAN}⏳ Waiting {wait_time:.2f}s...{Colors.END}")
                    time.sleep(wait_time)
                else:
                    print(f"{Colors.YELLOW}⚠️ Claim failed, retrying...{Colors.END}")
                    time.sleep(5)
                    self.is_logged_in = False
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.BOLD}{Colors.RED}🛑 Stopped{Colors.END}")
                print(f"{Colors.GREEN}📊 Total claims: {self.claim_count}{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
                time.sleep(10)

def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}🪙  FreeLTC Faucet Automation Bot{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    faucet = FreeLTCFaucet()
    
    if not faucet.get_credentials():
        sys.exit(1)
    
    try:
        faucet.run_infinite_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.END}")

if __name__ == "__main__":
    main()
