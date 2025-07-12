#!/usr/bin/python3
import os
import sys
import time
import argparse
from pathlib import Path
import re
import random

def get_parser():
    parser = argparse.ArgumentParser(description='Parrotify Terminal - Make your terminal look like Parrot OS')
    pars = parser.add_argument_group('Parrotify options')
    pars.add_argument('--parrotify', '-p', help='Make terminal look like Parrot OS', action="store_true")
    pars.add_argument('--revert', '-r', help='Revert to normal look', action="store_true")
    return parser

def get_available_fonts():
    """Get list of available toilet fonts by checking the figlet font directory"""
    font_dir = "/data/data/com.termux/files/usr/share/figlet/" if os.path.exists("/data/data/com.termux/files/usr/share/figlet/") else "/usr/share/figlet/"
    available_fonts = []
    
    try:
        for file in os.listdir(font_dir):
            if file.endswith(('.flf', '.tlf')):
                font_name = file.replace('.flf', '').replace('.tlf', '')
                if os.system(f"toilet -f {font_name} 'test' > /dev/null 2>&1") == 0:
                    available_fonts.append(font_name)
    except FileNotFoundError:
        pass
    
    if not available_fonts:
        print("\033[1;31mError: No valid toilet fonts found in {}\033[0m".format(font_dir))
        print("\033[1;33mPlease ensure the 'toilet' package is installed correctly.\033[0m")
        print("\033[1;33mRun: pkg install toilet\033[0m")
        return []
    
    return available_fonts

def check_toilet_fonts_package():
    """Check available fonts and inform Termux users about limited font support"""
    available_fonts = get_available_fonts()
    
    if not available_fonts:
        print("\033[1;33m" + "="*60 + "\033[0m")
        print("\033[1;31mNo usable fonts detected. Cannot proceed.\033[0m")
        print("\033[1;36mPlease reinstall the 'toilet' package:\033[0m")
        print("\033[1;32mpkg install toilet\033[0m")
        print("\033[1;33m" + "="*60 + "\033[0m")
        sys.exit(1)
    
    print("\033[1;36mAvailable fonts: {}\033[0m".format(", ".join(available_fonts)))
    if len(available_fonts) <= 5:
        print("\033[1;33m" + "="*60 + "\033[0m")
        print("\033[1;33mLimited fonts detected in Termux.\033[0m")
        print("\033[1;36mUsing available fonts: {}\033[0m".format(", ".join(available_fonts)))
        print("\033[1;33m" + "="*60 + "\033[0m")
    
    return available_fonts

def TermColor(name, filt):
    available_fonts = get_available_fonts()
    
    if not available_fonts:
        print("\033[1;31mError: No valid fonts available. Aborting.\033[0m")
        sys.exit(1)
    
    print(f"\033[1;36mAvailable fonts: {', '.join(available_fonts)}\033[0m")
    
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    try:
        if os.path.exists(motd_path) and not os.path.exists(motd_backup):
            os.system(f"mv {motd_path} {motd_backup}")
        else:
            print("Clear screen already set or MOTD backup exists")
    except Exception as e:
        print(f"Could not handle MOTD: {e}")
    
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    
    try:
        if os.path.exists(filename):
            os.system(f"cp {filename} {backup_file}")
            print(f"\033[1;32mBacked up .bashrc to {backup_file}\033[0m")
        
        with open(filename, "w") as new:
            selected_font = random.choice(available_fonts)
            print(f"\033[1;32mUsing font: {selected_font}\033[0m")
            
            test_cmd = f"toilet -f {selected_font} --{filt} {name} -t"
            test_result = os.system(f"{test_cmd} > /dev/null 2>&1")
            
            if test_result != 0:
                print(f"\033[1;33mWarning: Font {selected_font} with filter {filt} failed.\033[0m")
                print("\033[1;33mPlease check toilet installation and fonts.\033[0m")
                sys.exit(1)
            
            username = os.getenv("USER", "user")
            new.write(f"""toilet -f {selected_font} --{filt} {name} -t | lolcat
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]{username}\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]#\\[\\033[01;32m\\]'
""")
        print("\n\n")
        print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
        print("\033[1;32m[-] Parrotify was successful! Run 'source ~/.bashrc' or restart your terminal to apply changes.\033[0m")
        
    except IOError as e:
        print(f"Error writing to .bashrc: {e}")
        sys.exit(1)

def countdown(seconds):
    """Display a countdown with the ability to interrupt"""
    try:
        for i in range(seconds, 0, -1):
            print(f"\rClosing in {i} seconds... Press Ctrl+C to abort", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")
    except KeyboardInterrupt:
        print("\nAborted by user")
        raise

def choose_filter():
    print("\n\n")
    print("\033[1;34m  1) gay: add a rainbow colour effect\033[0m")
    print("\033[1;34m  2) metal: add a metallic colour effect\033[0m")
    print("\n\n")
    
    form = input("Enter filter number (default: 1): ").strip()
    return form

def reversify():
    """Revert terminal to normal state and clean up backups"""
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    # Restore MOTD if backup exists
    try:
        if os.path.exists(motd_backup):
            os.system(f"mv {motd_backup} {motd_path}")
            print("\033[1;32mRestored MOTD from backup\033[0m")
        elif os.path.exists(motd_path):
            print("\033[1;32mMOTD already in place\033[0m")
    except Exception as e:
        print(f"Could not restore MOTD: {e}")
    
    # Restore .bashrc from backup or remove custom .bashrc
    try:
        if os.path.exists(backup_file):
            os.system(f"mv {backup_file} {filename}")
            print("\033[1;32mRestored .bashrc from {backup_file}\033[0m")
        elif os.path.exists(filename):
            os.remove(filename)
            print("\033[1;32mRemoved custom .bashrc\033[0m")
        else:
            print("\033[1;32mNo custom .bashrc found\033[0m")
    except OSError as e:
        print(f"Error handling .bashrc: {e}")
    
    print("\n\n")
    print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
    print("\033[1;32m[-] Revert was successful! Run 'source ~/.bashrc' or restart your terminal.\033[0m")

def display_banner():
    """Display the main banner"""
    available_fonts = get_available_fonts()
    
    os.system("clear")
    print("\033[1;31m")
    
    if os.system("which toilet > /dev/null 2>&1") == 0 and available_fonts:
        selected_font = random.choice(available_fonts)
        banner_result = os.system(f"toilet -t -f {selected_font} --gay PAR0tifyTerm 2>/dev/null")
        
        if banner_result != 0:
            print("\033[1;33mFallback banner (toilet command failed):\033[0m")
            print_ascii_banner()
    else:
        print("\033[1;33mFallback banner (toilet not found or no fonts):\033[0m")
        print_ascii_banner()
    
    print("\033[1;32m")
    print("\033[1;34m          Created By W1nterFr3ak\033[0m")
    print("\033[2;32m     Winter says Parrot is awesome\033[0m")
    print("\033[1;32m   Mail: WinterFreak@protonmail.com\033[0m")
    print()

def print_ascii_banner():
    """Print ASCII art banner as fallback"""
    print("██████╗  █████╗ ██████╗  ██████╗ ████████╗██╗███████╗██╗   ██╗")
    print("██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝╚██╗ ██╔╝")
    print("██████╔╝███████║██████╔╝██║   ██║   ██║   ██║█████╗   ╚████╔╝ ")
    print("██╔═══╝ ██╔══██║██╔══██╗██║   ██║   ██║   ██║██╔══╝    ╚██╔╝  ")
    print("██║     ██║  ██║██║  ██║╚██████╔╝   ██║   ██║██║        ██║   ")
    print("╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝        ╚═╝   ")

def validate_dependencies():
    """Check if required commands are available"""
    missing_deps = []
    
    if os.system("which toilet > /dev/null 2>&1") != 0:
        missing_deps.append("toilet")
    if os.system("which lolcat > /dev/null 2>&1") != 0:
        missing_deps.append("lolcat")
    
    if missing_deps:
        print("\033[1;33mWarning: The following dependencies are missing:\033[0m")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\033[1;33mInstall them with: pkg install {}\033[0m".format(" ".join(missing_deps)))
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting...")
            sys.exit(1)
    else:
        available_fonts = check_toilet_fonts_package()
        print(f"\033[1;36mDetected {len(available_fonts)} available toilet fonts\033[0m")
        if available_fonts:
            print("\033[1;36mTesting font availability:\033[0m")
            for font in available_fonts[:5]:
                test_result = os.system(f"echo 'TEST' | toilet -f {font} > /dev/null 2>&1")
                status = "✓" if test_result == 0 else "✗"
                print(f"  {status} {font}")
    
    return available_fonts

def main():
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
        
    elif parrot:
        name = input("Enter name to be displayed in termux: ").strip()
        
        if len(name) > 0:
            # Validate name to prevent shell injection
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
                print("\033[1;31mError: Name should contain only alphanumeric characters, spaces, hyphens, and underscores\033[0m")
                sys.exit(1)
            name = name.replace('"', '\\"').replace('`', '\\`')
            
            form = choose_filter()
            
            if form == '1' or form == '':
                form = 'gay'
                TermColor(name, form)
            elif form == '2':
                form = 'metal'
                TermColor(name, form)
            elif form.lower() == "q":
                sys.exit()
            else:
                print("Using default option (rainbow)")
                form = "gay"
                TermColor(name, form)
        else:
            print("\033[1;32m!!! Please rerun the script and input the name to be displayed !!!\033[0m")
            sys.exit(1)
            
    elif rev:
        reversify()
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[1;33mScript interrupted by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[1;31mUnexpected error: {e}\033[0m")
        sys.exit(1)
