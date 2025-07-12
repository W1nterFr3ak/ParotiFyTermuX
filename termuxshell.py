#!/usr/bin/python3
import os
import sys
import time
import argparse
from pathlib import Path
import re
import random
import subprocess

def get_parser():
    parser = argparse.ArgumentParser(description='Parrotify Terminal - Make your terminal look like Parrot OS')
    pars = parser.add_argument_group('Parrotify options')
    pars.add_argument('--parrotify', '-p', help='Make terminal look like Parrot OS', action="store_true")
    pars.add_argument('--revert', '-r', help='Revert to normal look', action="store_true")
    return parser

def get_available_fonts():
    """Get list of available toilet fonts by checking the figlet font directory"""
    print("\033[1;36m[DEBUG] Entering get_available_fonts...\033[0m")
    font_dir = "/data/data/com.termux/files/usr/share/figlet/" if os.path.exists("/data/data/com.termux/files/usr/share/figlet/") else "/usr/share/figlet/"
    available_fonts = []
    
    print(f"\033[1;36m[DEBUG] Checking font directory: {font_dir}\033[0m")
    try:
        if not os.path.exists(font_dir):
            print("\033[1;33m[DEBUG] Font directory does not exist\033[0m")
            return ["standard"]
        
        for file in os.listdir(font_dir):
            if file.endswith(('.flf', '.tlf')):
                font_name = file.replace('.flf', '').replace('.tlf', '')
                print(f"\033[1;36m[DEBUG] Found font: {font_name}\033[0m")
                # Skip font testing to avoid hangs; assume font is usable
                available_fonts.append(font_name)
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Error accessing font directory: {e}\033[0m")
    
    # Fallback to standard font if none found
    if not available_fonts:
        print("\033[1;33m[DEBUG] No fonts found, using fallback: standard\033[0m")
        available_fonts = ["standard"]
    
    print(f"\033[1;36m[DEBUG] Available fonts: {available_fonts}\033[0m")
    return available_fonts

def install_fonts():
    """Automatically download and install additional fonts from GitHub in Termux"""
    font_dir = "/data/data/com.termux/files/usr/share/figlet/"
    temp_dir = "/data/data/com.termux/files/usr/share/figlet_temp/"

    print("\033[1;33m" + "="*60 + "\033[0m")
    print("\033[1;33m[DEBUG] Installing additional fonts for Termux...\033[0m")

    # Ensure git is installed
    if os.system("which git > /dev/null 2>&1") != 0:
        print("\033[1;32m[DEBUG] Installing git...\033[0m")
        result = os.system("pkg install git -y")
        if result != 0:
            print("\033[1;31m[DEBUG] Failed to install git. Continuing with default fonts.\033[0m")
            return get_available_fonts()

    # Create temporary directory
    try:
        os.makedirs(temp_dir, exist_ok=True)
        print("\033[1;36m[DEBUG] Created temp directory\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Failed to create temp directory: {e}\033[0m")
        return get_available_fonts()

    # Download fonts from xero/figlet-fonts
    repo_url = "https://github.com/xero/figlet-fonts.git"
    print("\033[1;32m[DEBUG] Downloading fonts from xero/figlet-fonts...\033[0m")
    try:
        subprocess.run(f"git clone {repo_url} {temp_dir}", shell=True, timeout=30, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        print("\033[1;31m[DEBUG] Font download timed out. Continuing with default fonts.\033[0m")
        return get_available_fonts()
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m[DEBUG] Failed to download fonts: {e}. Continuing with default fonts.\033[0m")
        return get_available_fonts()

    # Move .flf and .tlf files to font directory
    try:
        os.makedirs(font_dir, exist_ok=True)
        os.system(f"mv {temp_dir}*.flf {font_dir} 2>/dev/null")
        os.system(f"mv {temp_dir}*.tlf {font_dir} 2>/dev/null")
        print("\033[1;32m[DEBUG] ✓ Fonts installed successfully!\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Failed to install fonts: {e}\033[0m")
        return get_available_fonts()
    finally:
        # Clean up temporary directory
        os.system(f"rm -rf {temp_dir}")
        print("\033[1;36m[DEBUG] Cleaned up temp directory\033[0m")

    print("\033[1;36m[DEBUG] Re-scanning available fonts...\033[0m")
    time.sleep(2)
    return get_available_fonts()

def check_toilet_fonts_package():
    """Check available fonts and install additional fonts if needed in Termux"""
    print("\033[1;36m[DEBUG] Entering check_toilet_fonts_package...\033[0m")
    available_fonts = get_available_fonts()
    extended_fonts = ["slant", "3d", "doom", "starwars", "gothic"]
    has_extended = any(font in available_fonts for font in extended_fonts)
    
    if not has_extended and len(available_fonts) <= 10 and os.path.exists("/data/data/com.termux/files/usr/"):
        print("\033[1;36m[DEBUG] No extended fonts found, installing...\033[0m")
        available_fonts = install_fonts()
    
    print("\033[1;33m" + "="*60 + "\033[0m")
    print("\033[1;36mCurrent available fonts:\033[0m", end=" ")
    print("\033[1;32m" + ", ".join(available_fonts) + "\033[0m")
    print("\033[1;33m" + "="*60 + "\033[0m")
    return available_fonts

def TermColor(name, filt):
    print("\033[1;36m[DEBUG] Entering TermColor...\033[0m")
    available_fonts = get_available_fonts()
    
    print(f"\033[1;36mAvailable fonts: {', '.join(available_fonts)}\033[0m")
    
    # Handle MOTD backup for Termux
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    try:
        if os.path.exists(motd_path) and not os.path.exists(motd_backup):
            os.system(f"mv {motd_path} {motd_backup}")
            print("\033[1;32m[DEBUG] Backed up MOTD\033[0m")
        else:
            print("\033[1;36m[DEBUG] MOTD already backed up or does not exist\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Could not handle MOTD: {e}\033[0m")
    
    # Backup .bashrc
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    try:
        if os.path.exists(filename):
            os.system(f"cp {filename} {backup_file}")
            print(f"\033[1;32m[DEBUG] Backed up .bashrc to {backup_file}\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Failed to backup .bashrc: {e}\033[0m")
    
    # Update .bashrc
    try:
        with open(filename, "w") as new:
            selected_font = random.choice(available_fonts)
            print(f"\033[1;32m[DEBUG] Using font: {selected_font}\033[0m")
            
            # Test the command with timeout
            test_cmd = f"toilet -f {selected_font} --{filt} {name} -t"
            try:
                subprocess.run(test_cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.TimeoutExpired:
                print(f"\033[1;33m[DEBUG] Font {selected_font} test timed out, using standard font\033[0m")
                selected_font = "standard"
            except subprocess.CalledProcessError:
                print(f"\033[1;33m[DEBUG] Font {selected_font} test failed, using standard font\033[0m")
                selected_font = "standard"
            
            # Use current username for PS1
            username = os.getenv("USER", "user")
            new.write(f"""toilet -f {selected_font} --{filt} {name} -t | lolcat
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]{username}\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]$\\[\\033[01;32m\\]'
""")
        print("\n\033[1;32mParrotify was successful!\033[0m")
        print("\033[1;32mPlease run 'source ~/.bashrc' or restart your terminal to apply changes.\033[0m")
    except IOError as e:
        print(f"\033[1;31m[DEBUG] Error writing to .bashrc: {e}\033[0m")
        sys.exit(1)

def countdown(seconds):
    """Display a countdown with the ability to interrupt"""
    print("\033[1;36m[DEBUG] Starting countdown...\033[0m")
    try:
        for i in range(seconds, 0, -1):
            print(f"\rClosing in {i} seconds... Press Ctrl+C to abort", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")
    except KeyboardInterrupt:
        print("\n\033[1;33m[DEBUG] Aborted by user\033[0m")
        raise

def choose_filter():
    print("\n\033[1;34m  1) gay: add a rainbow colour effect\033[0m")
    print("\033[1;34m  2) metal: add a metallic colour effect\033[0m")
    print()
    
    form = input("Enter filter number (default: 1): ").strip()
    print(f"\033[1;36m[DEBUG] Selected filter: {form}\033[0m")
    return form

def reversify():
    """Revert terminal to normal state and clean up"""
    print("\033[1;36m[DEBUG] Entering reversify...\033[0m")
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    font_dir = "/data/data/com.termux/files/usr/share/figlet/"
    
    # Restore MOTD if backup exists
    try:
        if os.path.exists(motd_backup):
            os.system(f"mv {motd_backup} {motd_path}")
            print("\033[1;32m[DEBUG] Restored MOTD\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Could not restore MOTD: {e}\033[0m")
    
    # Restore .bashrc from backup
    try:
        if os.path.exists(backup_file):
            os.system(f"mv {backup_file} {filename}")
            print("\033[1;32m[DEBUG] Restored .bashrc from backup\033[0m")
        elif os.path.exists(filename):
            os.remove(filename)
            print("\033[1;32m[DEBUG] Removed custom .bashrc\033[0m")
        else:
            print("\033[1;32m[DEBUG] No custom .bashrc found\033[0m")
    except OSError as e:
        print(f"\033[1;31m[DEBUG] Error during revert: {e}\033[0m")
    
    # Clean up downloaded fonts (excluding default ones)
    try:
        extended_fonts = ["slant", "3d", "doom", "starwars", "gothic"]
        default_fonts = ["standard", "big", "small", "mini", "block", "bubble", "digital", "script", "shadow", "banner"]
        for font in os.listdir(font_dir):
            font_name = font.replace('.flf', '').replace('.tlf', '')
            if font_name not in default_fonts and font.endswith(('.flf', '.tlf')):
                os.remove(os.path.join(font_dir, font))
                print(f"\033[1;32m[DEBUG] Removed downloaded font: {font}\033[0m")
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Could not clean up fonts: {e}\033[0m")
    
    print("\n\033[1;32mReversing Parrotify was successful!\033[0m")
    print("\033[1;32mPlease run 'source ~/.bashrc' or restart your terminal to apply changes.\033[0m")

def display_banner():
    """Display the main banner"""
    print("\033[1;36m[DEBUG] Entering display_banner...\033[0m")
    available_fonts = get_available_fonts()
    
    os.system("clear")
    print("\033[1;31m")
    
    if os.system("which toilet > /dev/null 2>&1") == 0:
        selected_font = random.choice(available_fonts)
        print(f"\033[1;36m[DEBUG] Using font for banner: {selected_font}\033[0m")
        try:
            # Use timeout to prevent hanging
            subprocess.run(f"toilet -t -f {selected_font} --gay PAR0tifyTerm", shell=True, timeout=5)
        except subprocess.TimeoutExpired:
            print("\033[1;33m[DEBUG] Toilet command timed out, using fallback banner\033[0m")
            print_ascii_banner()
        except subprocess.CalledProcessError:
            print("\033[1;33m[DEBUG] Toilet command failed, using fallback banner\033[0m")
            print_ascii_banner()
    else:
        print("\033[1;33m[DEBUG] Toilet not found, using fallback banner\033[0m")
        print_ascii_banner()
    
    print("\033[1;32m")
    print("\033[1;34m          Created By W1nterFr3ak\033[0m")
    print("\033[2;32m     Winter says Parrot is awesome\033[0m")
    print("\033[1;32m   Mail: WinterFreak@protonmail.com\033[0m")
    print()
    print("\033[1;36m[DEBUG] Banner display completed\033[0m")

def print_ascii_banner():
    """Print ASCII art banner as fallback"""
    print("\033[1;36m[DEBUG] Printing ASCII banner...\033[0m")
    print("██████╗  █████╗ ██████╗  ██████╗ ████████╗██╗███████╗██╗   ██╗")
    print("██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝╚██╗ ██╔╝")
    print("██████╔╝███████║██████╔╝██║   ██║   ██║   ██║█████╗   ╚████╔╝ ")
    print("██╔═══╝ ██╔══██║██╔══██╗██║   ██║   ██║   ██║██╔══╝    ╚██╔╝  ")
    print("██║     ██║  ██║██║  ██║╚██████╔╝   ██║   ██║██║        ██║   ")
    print("╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝   ")

def validate_dependencies():
    """Check if required commands are available"""
    print("\033[1;36m[DEBUG] Entering validate_dependencies...\033[0m")
    missing_deps = []
    
    if os.system("which toilet > /dev/null 2>&1") != 0:
        missing_deps.append("toilet")
    if os.system("which lolcat > /dev/null 2>&1") != 0:
        missing_deps.append("lolcat")
    
    if missing_deps:
        print("\033[1;33m[DEBUG] Missing dependencies: {', '.join(missing_deps)}\033[0m")
        print("\033[1;33mInstall them with: pkg install toilet lolcat\033[0m")
        response = input("Install now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            os.system("pkg install toilet lolcat -y")
        else:
            print("\033[1;33m[DEBUG] Exiting due to missing dependencies\033[0m")
            sys.exit(1)
    
    available_fonts = check_toilet_fonts_package()
    print(f"\033[1;36m[DEBUG] Detected {len(available_fonts)} available toilet fonts\033[0m")
    return available_fonts

def main():
    print("\033[1;36m[DEBUG] Starting main function...\033[0m")
    display_banner()
    available_fonts = validate_dependencies()
    
    parser = get_parser()
    args = vars(parser.parse_args())
    parrot = args['parrotify']
    rev = args['revert']
    
    if rev and parrot:
        print("\033[1;32m              !!! CHOOSE ONE OPTION !!!\033[0m")
        print("\n\n")
        parser.print_help()
        print("\033[1;36m[DEBUG] Exiting due to conflicting options\033[0m")
        sys.exit(1)
        
    elif parrot:
        print("\033[1;36m[DEBUG] Running parrotify mode...\033[0m")
        name = input("Enter name to be displayed in termux: ").strip()
        
        if len(name) > 0:
            # Validate name to prevent shell injection
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
                print("\033[1;31m[DEBUG] Error: Name should contain only alphanumeric characters, spaces, hyphens, and underscores\033[0m")
                sys.exit(1)
            # Escape name for shell safety
            name = name.replace('"', '\\"').replace('`', '\\`')
            print(f"\033[1;36m[DEBUG] Validated name: {name}\033[0m")
            
            form = choose_filter()
            
            if form == '1' or form == '':
                form = 'gay'
                TermColor(name, form)
            elif form == '2':
                form = 'metal'
                TermColor(name, form)
            elif form.lower() == "q":
                print("\033[1;36m[DEBUG] User quit during filter selection\033[0m")
                sys.exit(0)
            else:
                print("\033[1;36m[DEBUG] Using default filter (gay)\033[0m")
                form = "gay"
                TermColor(name, form)
        else:
            print("\033[1;32m[DEBUG] !!! Please rerun the script and input the name to be displayed !!!\033[0m")
            sys.exit(1)
            
    elif rev:
        print("\033[1;36m[DEBUG] Running revert mode...\033[0m")
        reversify()
    else:
        print("\033[1;36m[DEBUG] No options provided, displaying help...\033[0m")
        parser.print_help()
        print("\033[1;36m[DEBUG] Exiting after help display\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    try:
        print("\033[1;36m[DEBUG] Script started\033[0m")
        main()
        print("\033[1;36m[DEBUG] Script completed\033[0m")
    except KeyboardInterrupt:
        print("\n\033[1;33m[DEBUG] Script interrupted by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[1;31m[DEBUG] Unexpected error: {e}\033[0m")
        sys.exit(1)
