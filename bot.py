import os
import sys
import time
import random
import subprocess
import platform
import pyfiglet
from termcolor import colored
import shutil

# ========== AUTO UPDATE FUNCTION (SILENT) ==========
def auto_update():
    """Silent git pull in background - no output shown"""
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if .git exists
        git_path = os.path.join(current_dir, '.git')
        if not os.path.exists(git_path):
            return  # Not a git repo, skip
        
        # Silent git pull - hide all output
        subprocess.run(
            ['git', 'pull'],
            cwd=current_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5  # Timeout after 5 seconds to avoid hanging
        )
    except:
        pass  # Silently ignore any errors

# ========== GLOBAL BANNER FUNCTION ==========
def show_scriptify_banner():
    """Display Scriptify banner - same everywhere"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    ascii_art = pyfiglet.figlet_format("Scriptify", font="slant")
    lines = ascii_art.split('\n')
    colours = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    
    print("\n" + colored("="*60, "cyan", attrs=["bold"]))
    print(colored("🌟 WELCOME TO SCRIPTIFY 🌟", "cyan", attrs=["bold"]))
    print(colored("="*60, "cyan", attrs=["bold"]) + "\n")
    
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
            time.sleep(0.01)
    
    print("\n" + colored("="*60, "cyan", attrs=["bold"]))
    print(colored("📢 JOIN US: https://t.me/Scriptify1", "yellow", attrs=["bold"]))
    print(colored("="*60, "cyan", attrs=["bold"]) + "\n")

# ========== LOADING ANIMATION (From CommingSoon.py) ==========
class LoadingAnimation:
    def __init__(self):
        self.symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def full_screen_loading(self, duration=2):
        """Full screen loading animation with matrix rain"""
        # 🔥 Strong initial clear
        sys.stdout.write("\033[2J\033[H")  # Clear screen, move cursor home
        sys.stdout.write("\033[?25l")       # Hide cursor
        sys.stdout.flush()
        
        try:
            size = os.get_terminal_size()
            WIDTH, HEIGHT = size.columns, size.lines
        except OSError:
            WIDTH, HEIGHT = 80, 24

        # ANSI Colors
        GREEN = "\033[32m"
        BOLD_GREEN = "\033[1;32m"
        DARK_GREEN = "\033[2;32m"
        WHITE = "\033[1;37m"
        BOLD_RED = "\033[1;31m"
        RESET = "\033[0m"

        # LOADING Text
        LOADING_TEXT = [
    r"  _     ___    ___    ___   _   _   ___ ",
    r" | |   / _ \  / \  |_ _| | \ | | |_ _|",
    r" | |  | | | |/ _ \  | |  |  \| |  | | ",
    r" | |__| |_| / ___ \ | |  | |\  |  | | ",
    r" |____|\___/_/   \_\___| |_| \_|  |___|"
]

        class MatrixColumn:
            def __init__(self, x, symbols_set):
                self.x = x
                self.y = random.randint(-HEIGHT, 0)
                self.speed = random.randint(2, 5)
                self.length = random.randint(8, 20)
                self.symbols = [random.choice(symbols_set) for _ in range(self.length)]
                self.symbols_set = symbols_set

            def update(self):
                self.y += self.speed
                if self.y > HEIGHT + 10:
                    self.y = random.randint(-HEIGHT, -10)
                    self.symbols = [random.choice(self.symbols_set) for _ in range(self.length)]
                    self.speed = random.randint(2, 5)

            def draw(self):
                for i, char in enumerate(self.symbols):
                    y_pos = int(self.y) + i
                    if 0 < y_pos < HEIGHT:
                        if i == 0:
                            color = WHITE
                        elif i < 3:
                            color = BOLD_GREEN
                        elif i < self.length - 3:
                            if random.random() > 0.7:
                                color = GREEN
                            else:
                                color = DARK_GREEN
                        else:
                            color = DARK_GREEN
                        
                        if random.random() > 0.95:
                            color = WHITE
                        
                        sys.stdout.write(f"\033[{y_pos};{self.x}H{color}{char}{RESET}")

        def draw_center_text(art_lines, visible=True):
            if not visible:
                return
            
            art_height = len(art_lines)
            if art_height == 0:
                return
            art_width = max(len(line) for line in art_lines)
            
            center_y = (HEIGHT - art_height) // 2
            center_x = (WIDTH - art_width) // 2
            
            for i, line in enumerate(art_lines):
                y_pos = center_y + i
                if 0 < y_pos < HEIGHT:
                    sys.stdout.write(f"\033[{y_pos};{center_x}H{BOLD_RED}{line}{RESET}")

        def draw_status_bar():
            status_texts = [
                "> LOADING...",
                "> PLEASE_WAIT...",
                "> SYSTEM_INITIALIZING...",
                "> SCRIPTIFY"
            ]
            
            for i, text in enumerate(status_texts):
                y_pos = HEIGHT - len(status_texts) + i - 1
                if 0 < y_pos < HEIGHT:
                    if random.random() > 0.9:
                        text = text.replace(" ", "█")
                        color = WHITE
                    elif random.random() > 0.8:
                        color = BOLD_GREEN
                    else:
                        color = GREEN
                    sys.stdout.write(f"\033[{y_pos};3H{color}{text}{RESET}")

        # Create columns
        columns = []
        col_spacing = 1
        for x in range(1, WIDTH, col_spacing):
            columns.append(MatrixColumn(x, self.symbols))

        start_time = time.time()
        show_text = False
        text_visible = True
        frame_count = 0

        try:
            while time.time() - start_time < duration:
                # Clear screen completely each frame
                sys.stdout.write("\033[2J\033[H")

                elapsed = time.time() - start_time
                if elapsed > 0.5:
                    show_text = True

                # Draw matrix columns
                for col in columns:
                    col.update()
                    col.draw()

                # Status bar
                draw_status_bar()

                # LOADING text with blink
                if show_text:
                    frame_count += 1
                    if frame_count % 5 == 0:
                        text_visible = not text_visible
                    draw_center_text(LOADING_TEXT, visible=text_visible)

                sys.stdout.flush()
                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        
        # Clean up: show cursor and clear screen
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        sys.stdout.flush()
        time.sleep(0.1)
        self.clear_screen()

# ========== SCRIPTIFY BROWSER ==========
class ScriptifyBrowser:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.base_path = self.current_path  # 🔥 Store base path - never go back from here
        self.items = []
        self.history = []
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def get_items(self):
        """Get all items in current directory"""
        self.items = []
        try:
            items = os.listdir(self.current_path)
            for item in items:
                if not item.startswith('.'):
                    item_path = os.path.join(self.current_path, item)
                    is_dir = os.path.isdir(item_path)
                    self.items.append({
                        'name': item,
                        'path': item_path,
                        'is_dir': is_dir,
                        'extension': os.path.splitext(item)[1].lower() if not is_dir else ''
                    })
            self.items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        except Exception as e:
            pass

    def display_items(self):
        """Display items with colorful formatting - clean display"""
        self.clear_screen()
        show_scriptify_banner()
        
        # 🔥 Show current location
        print(colored(f"  📂 Current: {self.current_path}", "cyan", attrs=["bold"]))
        print(colored("  " + "─"*50, "cyan"))
        print()
        
        if not self.items:
            print(colored("  ❌ No items found", "red", attrs=["bold"]))
            return
        
        for i, item in enumerate(self.items, 1):
            colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
            color = colors[i % len(colors)]
            name = item['name']
            
            if item['is_dir']:
                icon = colored("📁", color)
            else:
                icon = colored("📄", color)
            
            name_display = colored(f"{icon} {name}", color, attrs=["bold"])
            num_color = ['green', 'cyan', 'yellow', 'magenta'][i % 4]
            print(f"  {colored(str(i).zfill(2), num_color, attrs=['bold'])}. {name_display}")
            time.sleep(0.02)
        
        print("\n" + colored("─"*50, "cyan"))
        print(colored("  [0] Back  [q] Quit", "yellow", attrs=["bold"]))

    def execute_file(self, file_path, extension, filename):
        """Execute file based on extension - completely independent"""
        try:
            if extension == '.py':
                print(colored(f"\n  🚀 Executing: ", "cyan", attrs=["bold"]) + 
                      colored(f"python {filename}", "green", attrs=["bold"]))
                print(colored("  " + "─"*40, "cyan"))
                python_cmd = 'python3' if shutil.which('python3') else 'python'
                
                subprocess.call([python_cmd, file_path])
                return True
                
            elif extension == '.php':
                print(colored(f"\n  🚀 Executing: ", "cyan", attrs=["bold"]) + 
                      colored(f"php {filename}", "magenta", attrs=["bold"]))
                print(colored("  " + "─"*40, "cyan"))
                if shutil.which('php'):
                    subprocess.call(['php', file_path])
                    return True
                else:
                    print(colored("\n  ⚠️ PHP is not installed!", "yellow", attrs=["bold"]))
                    return False
                    
            elif extension in ['.sh', '.bash']:
                print(colored(f"\n  🚀 Executing: ", "cyan", attrs=["bold"]) + 
                      colored(f"bash {filename}", "red", attrs=["bold"]))
                print(colored("  " + "─"*40, "cyan"))
                subprocess.call(['bash', file_path])
                return True
                
            elif extension in ['.html', '.htm']:
                print(colored(f"\n  🌐 Opening: ", "cyan", attrs=["bold"]) + 
                      colored(f"{filename}", "blue", attrs=["bold"]))
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
                return True
                
            else:
                print(colored(f"\n  📂 Opening: ", "cyan", attrs=["bold"]) + 
                      colored(f"{filename}", "white", attrs=["bold"]))
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
                return True
                
        except Exception as e:
            print(colored(f"\n  ❌ Error: {e}", "red", attrs=["bold"]))
            return False

    def navigate_to_item(self, index):
        """Navigate to or execute selected item"""
        if 1 <= index <= len(self.items):
            item = self.items[index - 1]
            if item['is_dir']:
                try:
                    # 🔥 Check if this directory is inside base path
                    new_path = item['path']
                    # Resolve both paths to compare
                    resolved_new = os.path.realpath(new_path)
                    resolved_base = os.path.realpath(self.base_path)
                    
                    # 🔥 Only allow navigation if new path starts with base path
                    if resolved_new.startswith(resolved_base):
                        self.history.append(self.current_path)
                        os.chdir(item['path'])
                        self.current_path = os.getcwd()
                        return True
                    else:
                        print(colored(f"\n  ❌ Cannot go outside base directory!", "red", attrs=["bold"]))
                        time.sleep(1)
                        return False
                except Exception as e:
                    print(colored(f"\n  ❌ Error: {e}", "red", attrs=["bold"]))
                    time.sleep(1)
                    return False
            else:
                return self.execute_file(item['path'], item['extension'], item['name'])
        return False

    def go_back(self):
        """Go to parent directory - but never above base path"""
        # 🔥 Check if current path is already base path
        if os.path.realpath(self.current_path) == os.path.realpath(self.base_path):
            print(colored("\n  ❌ Already at base directory!", "red", attrs=["bold"]))
            time.sleep(1)
            return False
        
        # Try to go to parent
        parent = os.path.dirname(self.current_path)
        # 🔥 Check if parent is inside base path
        if os.path.realpath(parent).startswith(os.path.realpath(self.base_path)):
            try:
                os.chdir(parent)
                self.current_path = os.getcwd()
                return True
            except:
                return False
        else:
            print(colored("\n  ❌ Cannot go above base directory!", "red", attrs=["bold"]))
            time.sleep(1)
            return False

    def run(self):
        """Main loop"""
        try:
            while True:
                self.get_items()
                self.display_items()
                
                print()
                print(colored("  ╔═══ Enter selection ═══╗", "yellow", attrs=["bold"]))
                print(colored("  ║ → ", "yellow", attrs=["bold"]), end='')
                
                choice = input().strip()
                
                if choice.lower() == 'q':
                    print(colored("\n  👋 Goodbye!", "green", attrs=["bold"]))
                    break
                
                if choice == '0':
                    if self.go_back():
                        continue
                    else:
                        # Error message already shown in go_back()
                        continue
                
                try:
                    index = int(choice)
                    if self.navigate_to_item(index):
                        if self.items[index-1]['is_dir']:
                            continue
                        else:
                            print()
                            input(colored("  Press Enter to continue...", "yellow", attrs=["bold"]))
                            continue
                    else:
                        # Error already shown
                        time.sleep(1)
                except ValueError:
                    if choice:
                        print(colored("\n  ❌ Enter number, 0 back, q quit", "red", attrs=["bold"]))
                        time.sleep(1)
                
        except KeyboardInterrupt:
            print(colored("\n\n  👋 Goodbye!", "green", attrs=["bold"]))
            sys.exit(0)

# ========== MAIN ==========
def main():
    # 🔥 Auto update in background - SILENT
    auto_update()
    
    # 🔥 Force clear before anything else
    os.system('clear' if os.name == 'posix' else 'cls')
    time.sleep(0.1)
    
    # Run loading animation with 2 seconds duration
    loading = LoadingAnimation()
    loading.full_screen_loading(duration=2)  # ⏱️ 2 seconds
    
    # Extra clear to ensure no garbage characters
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Run browser
    browser = ScriptifyBrowser()
    browser.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\n👋 Goodbye!", "green", attrs=["bold"]))
        sys.exit(0)
