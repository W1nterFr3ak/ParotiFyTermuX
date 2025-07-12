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
    """Get list of available toilet fonts with minimal testing to prevent hanging"""
    font_dir = "/data/data/com.termux/files/usr/share/figlet/"
    available_fonts = []
    
    if not os.path.exists(font_dir):
        print(f"\033[1;31mError: Font directory {font_dir} not found\033[0m")
        print("\033[1;33mPlease reinstall the 'toilet' package: pkg install toilet\033[0m")
        return []
    
    print("\033[1;36mScanning fonts in {}\033[0m".format(font_dir))
    try:
        for file in os.listdir(font_dir):
            if file.endswith(('.flf', '.tlf')) and 'ascii2' not in file.lower():  # Skip problematic fonts
                font_name = file.replace('.flf', '').replace('.tlf', '')
                print(f"\033[1;36mTesting font: {font_name}\033[0m")
                try:
                    result = subprocess.run(
                        ['toilet', '-f', font_name, 'test'],
                        capture_output=True, text=True, timeout=0.5
                    )
                    if result.returncode == 0:
                        available_fonts.append(font_name)
                        print(f"\033[1;32mFont {font_name} OK\033[0m")
                    else:
                        print(f"\033[1;33mFont {font_name} failed to load\033[0m")
                except subprocess.TimeoutExpired:
                    print(f"\033[1;33mFont {font_name} timed out\033[0m")
                except subprocess.SubprocessError as e:
                    print(f"\033[1;33mError testing font {font_name}: {e}\033[0m")
    except Exception as e:
        print(f"\033[1;31mError accessing font directory: {e}\033[0m")
    
    if not available_fonts:
        print("\033[1;31mError: No valid toilet fonts found\033[0m")
        print("\033[1;33mPlease reinstall the 'toilet' package: pkg install toilet\033[0m")
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
    """Apply terminal customization"""
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
            print("\033[1;32mBacked up MOTD to {}\033[0m".format(motd_backup))
        else:
            print("\033[1;36mMOTD already set or backup exists\033[0m")
    except Exception as e:
        print(f"\033[1;33mCould not handle MOTD: {e}\033[0m")
    
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    
    try:
        if os.path.exists(filename):
            os.system(f"cp {filename} {backup_file}")
            print(f"\033[1;32mBacked up .bashrc to {backup_file}\033[0m")
        
        with open(filename, "w") as new:
            selected_font = random.choice(available_fonts)
            print(f"\033[1;32mUsing font: {selected_font}\033[0m")
            
            try:
                test_result = subprocess.run(
                    ['toilet', '-f', selected_font, f'--{filt}', name, '-t'],
                    capture_output=True, text=True, timeout=0.5
                )
                if test_result.returncode != 0:
                    print(f"\033[1;33mWarning: Font {selected_font} with filter {filt} failed: {test_result.stderr}\033[0m")
                    sys.exit(1)
            except subprocess.TimeoutExpired:
                print(f"\033[1;33mWarning: Font {selected_font} timed out\033[0m")
                sys.exit(1)
            except subprocess.SubprocessError as e:
                print(f"\033[1;33mWarning: Error testing font {selected_font}: {e}\033[0m")
                sys.exit(1)
            
            username = os.getenv("USER", "user")
            new.write(f"""toilet -f {selected_font} --{filt} {name} -t | lolcat
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]{username}\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]#\\[\\033[01;32m\\]'
""")
        print("\n")
        print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
        print("\033[1;32m[-] Parrotify was successful! Run 'source ~/.bashrc' or restart your terminal to apply changes.\033[0m")
        
    except IOError as e:
        print(f"\033[1;31mError writing to .bashrc: {e}\033[0m")
        sys.exit(1)

def choose_filter():
    print("\n")
    print("\033[1;34m  1) gay: add a rainbow colour effect\033[0m")
    print("\033[1;34m  2) metal: add a metallic colour effect\033[0m")
    print("\n")
    
    form = input("Enter filter number (default: 1): ").strip()
    return form

def reversify():
    """Revert terminal to normal state and clean up backups"""
    filename = str(Path.home()) + "/.bashrc"
    backup_file = filename + ".backup"
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    try:
        if os.path.exists(motd_backup):
            os.system(f"mv {motd_backup} {motd_path}")
            print("\033[1;32mRestored MOTD from {}\033[0m".format(motd_backup))
        elif os.path.exists(motd_path):
            print("\033[1;32mMOTD already in place\033[0m")
        else:
            print("\033[1;36mNo MOTD backup found\033[0m")
    except Exception as e:
        print(f"\033[1;33mCould not restore MOTD: {e}\033[0m")
    
    try:
        if os.path.exists(backup_file):
            os.system(f"mv {backup_file} {filename}")
            print("\033[1;32mRestored .bashrc from {}\033[0m".format(backup_file))
        elif os.path.exists(filename):
            os.remove(filename)
            print("\033[1;32mRemoved custom .bashrc\033[0m")
        else:
            print("\033[1;32mNo custom .bashrc found\033[0m")
    except OSError as e:
        print(f"\033[1;33mError handling .bashrc: {e}\033[0m")
    
    print("\n")
    print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
    print("\033[1;32m[-] Revert was successful! Run 'source ~/.bashrc' or restart your terminal.\033[0m")

def display_banner():
    """Display the main banner"""
    available_fonts = get_available_fonts()
    
    os.system("clear")
    print("\033[1;31m")
    
    toilet_path = "/data/data/com.termux/files/usr/bin/toilet"
    if os.path.exists(toilet_path) and available_fonts:
        selected_font = random.choice(available_fonts)
        print(f"\033[1;36mDisplaying banner with font: {selected_font}\033[0m")
        try:
            result = subprocess.run(
                ['toilet', '-t', '-f', selected_font, '--gay', 'PAR0tifyTerm'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode != 0:
                print("\033[1;33mFallback banner (toilet command failed: {})\033[0m".format(result.stderr))
                print_ascii_banner()
            else:
                print(result.stdout)
        except subprocess.TimeoutExpired:
            print("\033[1;33mFallback banner (toilet command timed out)\033[0m")
            print_ascii_banner()
        except subprocess.SubprocessError as e:
            print(f"\033[1;33mFallback banner (toilet command error: {e})\033[0m")
            print_ascii_banner()
    else:
        print("\033[1;33mFallback banner (toilet not found or no fonts)\033[0m")
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
    toilet_path = "/data/data/com.termux/files/usr/bin/toilet"
    lolcat_path = "/data/data/com.termux/files/usr/bin/lolcat"
    
    # Check for native toilet
    if not os.path.exists(toilet_path):
        missing_deps.append("toilet")
    else:
        print("\033[1;32mFound toilet at {}\033[0m".format(toilet_path))
    
    # Check for native lolcat
    if not os.path.exists(lolcat_path):
        # Check if gem-installed lolcat exists
        try:
            gem_lolcat = subprocess.run(
                ['gem', 'list', 'lolcat', '--installed'],
                capture_output=True, text=True, timeout=1
            )
            if gem_lolcat.returncode == 0 and 'lolcat' in gem_lolcat.stdout:
                print("\033[1;33mWarning: Found gem-installed lolcat, which may be incompatible\033[0m")
                print("\033[1;36mPlease install native lolcat: pkg install lolcat\033[0m")
            missing_deps.append("lolcat")
        except subprocess.SubprocessError:
            missing_deps.append("lolcat")
    else:
        print("\033[1;32mFound lolcat at {}\033[0m".format(lolcat_path))
    
    if missing_deps:
        print("\033[1;33mWarning: Missing dependencies: {}\033[0m".format(", ".join(missing_deps)))
        print("\033[1;33mInstall them with: pkg install {}\033[0m".format(" ".join(missing_deps)))
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting...")
            sys.exit(1)
    else:
        available_fonts = check_toilet_fonts_package()
        print(f"\033[1;36mDetected {len(available_fonts)} available toilet fonts\033[0m")
        if available_fonts:
            print("\033[1;36mAvailable fonts:\033[0m")
            for font in available_fonts[:5]:
                print(f"  ✓ {font}")
    
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
        print("\n")
        parser.print_help()
        
    elif parrot:
        name = input("Enter name to be displayed in termux: ").strip()
        
        if len(name) > 0:
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
