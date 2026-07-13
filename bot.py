import os
import sys
import time
import random
import subprocess
import platform
import pyfiglet
from termcolor import colored
import shutil

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

# ========== HACKER ANIMATION ==========
class HackerAnimation:
    def __init__(self):
        self.symbols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                        'A', 'B', 'C', 'D', 'E', 'F']

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def full_screen_animation(self, duration=8):
        """Full screen hacker animation with matrix rain"""
        self.clear_screen()
        start_time = time.time()
        
        try:
            cols = os.get_terminal_size().columns
            lines = os.get_terminal_size().lines
        except:
            cols = 80
            lines = 24
        
        drops = []
        for _ in range(int(cols * 0.4)):
            drops.append({
                'x': random.randint(0, cols - 1),
                'y': random.randint(-lines, 0),
                'speed': random.randint(1, 3),
                'length': random.randint(5, 15)
            })
        
        while time.time() - start_time < duration:
            sys.stdout.write('\033[2J\033[H')
            
            for y in range(lines):
                line_chars = []
                for x in range(cols):
                    char = ' '
                    for drop in drops:
                        if drop['x'] == x and drop['y'] <= y < drop['y'] + drop['length']:
                            if y == drop['y'] + drop['length'] - 1:
                                char = colored(random.choice(self.symbols), 'white', attrs=['bold'])
                            else:
                                char = colored(random.choice(self.symbols), 'green')
                            break
                    line_chars.append(char)
                print(''.join(line_chars))
            
            for drop in drops:
                drop['y'] += drop['speed']
                if drop['y'] > lines:
                    drop['y'] = random.randint(-20, -5)
                    drop['x'] = random.randint(0, cols - 1)
                    drop['length'] = random.randint(5, 15)
                    drop['speed'] = random.randint(1, 3)
            
            time.sleep(0.05)

# ========== SCRIPTIFY BROWSER ==========
class ScriptifyBrowser:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
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
                
                # Run completely independent - let it take over the terminal
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
                    self.history.append(self.current_path)
                    os.chdir(item['path'])
                    self.current_path = os.getcwd()
                    return True
                except Exception as e:
                    print(colored(f"\n  ❌ Error: {e}", "red", attrs=["bold"]))
                    time.sleep(1)
                    return False
            else:
                return self.execute_file(item['path'], item['extension'], item['name'])
        return False

    def go_back(self):
        """Go to parent directory"""
        if self.history:
            parent = self.history.pop()
            try:
                os.chdir(parent)
                self.current_path = os.getcwd()
                return True
            except:
                pass
        else:
            parent = os.path.dirname(self.current_path)
            if parent != self.current_path:
                try:
                    os.chdir(parent)
                    self.current_path = os.getcwd()
                    return True
                except:
                    pass
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
                        print(colored("\n  ❌ Already at root", "red", attrs=["bold"]))
                        time.sleep(1)
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
                        print(colored("\n  ❌ Invalid!", "red", attrs=["bold"]))
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
    # Run animation only once at start
    animation = HackerAnimation()
    animation.full_screen_animation(duration=8)
    
    # Run browser
    browser = ScriptifyBrowser()
    browser.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\n👋 Goodbye!", "green", attrs=["bold"]))
        sys.exit(0)