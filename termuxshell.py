#!/usr/bin/python3
import os
import sys
import time
import argparse
from pathlib import Path
import re
import random
import subprocess
import json

def get_parser():
    parser = argparse.ArgumentParser(description='Parrotify Terminal - Make your terminal look like Parrot OS')
    pars = parser.add_argument_group('Parrotify options')
    pars.add_argument('--parrotify', '-p', help='Make terminal look like Parrot OS', action="store_true")
    pars.add_argument('--revert', '-r', help='Revert to normal look', action="store_true")
    return parser

def is_parrotified():
    """Check if .bashrc is already parrotified"""
    filename = str(Path.home()) + "/.bashrc"
    if not os.path.exists(filename):
        return False
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        # Check for Parrotify-specific toilet command and PS1 prompt
        if 'toilet -f' in content and "PS1='[\\033[01;34m]┌──[\\033[01;32m]" in content:
            return True
    except IOError:
        print("\033[1;33mWarning: Could not read .bashrc to check parrotification\033[0m")
    return False

def get_available_fonts():
    """Get list of available toilet fonts, using cache if available"""
    font_cache = str(Path.home()) + "/.parrotifyfonts"
    font_dir = "/data/data/com.termux/files/usr/share/figlet/"
    
    # Check for cached fonts
    if os.path.exists(font_cache):
        try:
            with open(font_cache, 'r') as f:
                available_fonts = json.load(f)
            print("\033[1;36mLoaded fonts from cache: {}\033[0m".format(", ".join(available_fonts)))
            # Verify cached fonts are still valid
            valid_fonts = []
            for font in available_fonts:
                try:
                    result = subprocess.run(
                        ['toilet', '-f', font, 'test'],
                        capture_output=True, text=True, timeout=0.5
                    )
                    if result.returncode == 0:
                        valid_fonts.append(font)
                    else:
                        print(f"\033[1;33mCached font {font} no longer valid\033[0m")
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    print(f"\033[1;33mCached font {font} failed validation\033[0m")
            if valid_fonts:
                return valid_fonts
            print("\033[1;33mNo valid cached fonts; re-testing fonts\033[0m")
        except (json.JSONDecodeError, IOError):
            print("\033[1;33mInvalid font cache; re-testing fonts\033[0m")
    
    # Test fonts if no valid cache
    available_fonts = []
    if not os.path.exists(font_dir):
        print(f"\033[1;31mError: Font directory {font_dir} not found\033[0m")
        print("\033[1;33mPlease reinstall the 'toilet' package: pkg install toilet\033[0m")
        return []
    
    print("\033[1;36mScanning fonts in {}\033[0m".format(font_dir))
    try:
        for file in os.listdir(font_dir):
            if file.endswith(('.flf', '.tlf')) and 'ascii2' not in file.lower():
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
    
    # Cache valid fonts
    try:
        with open(font_cache, 'w') as f:
            json.dump(available_fonts, f)
        print(f"\033[1;32mCached fonts to {font_cache}\033[0m")
    except IOError as e:
        print(f"\033[1;33mWarning: Could not cache fonts to {font_cache}: {e}\033[0m")
    
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

def choose_font(available_fonts):
    """Prompt user to select a font or random option"""
    print("\n")
    print("\033[1;34mSelect a font or choose random:\033[0m")
    print("\033[1;34m  0) Random (select a random font each time)\033[0m")
    for i, font in enumerate(available_fonts, 1):
        print(f"\033[1;34m  {i}) {font}\033[0m")
    print("\n")
    
    while True:
        choice = input("Enter font number (default: 0): ").strip()
        if choice == '' or choice == '0':
            return None  # None indicates random font selection
        try:
            choice = int(choice)
            if 1 <= choice <= len(available_fonts):
                return available_fonts[choice - 1]
            else:
                print(f"\033[1;33mPlease enter a number between 0 and {len(available_fonts)}\033[0m")
        except ValueError:
            print("\033[1;33mPlease enter a valid number\033[0m")

def TermColor(name, filt):
    """Apply terminal customization with centered text and user-selected or random font"""
    if is_parrotified():
        print("\033[1;33mWarning: Terminal is already parrotified!\033[0m")
        response = input("\033[1;36mOverwrite existing .bashrc and its backup? (y/N): \033[0m").strip().lower()
        if response not in ['y', 'yes']:
            print("\033[1;32mExiting without changes.\033[0m")
            sys.exit(0)
    
    available_fonts = get_available_fonts()
    
    if not available_fonts:
        print("\033[1;31mError: No valid fonts available. Aborting.\033[0m")
        sys.exit(1)
    
    print(f"\033[1;36mAvailable fonts: {', '.join(available_fonts)}\033[0m")
    
    # Prompt for font selection
    selected_font = choose_font(available_fonts)
    
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
    font_cache = str(Path.home()) + "/.parrotifyfonts"
    
    try:
        if os.path.exists(filename):
            os.system(f"cp {filename} {backup_file}")
            print(f"\033[1;32mBacked up .bashrc to {backup_file}\033[0m")
        
        # Test the selected font (or a random one if random option chosen)
        test_font = selected_font if selected_font else random.choice(available_fonts)
        print(f"\033[1;32mTesting font: {test_font}\033[0m")
        try:
            test_result = subprocess.run(
                ['toilet', '-f', test_font, f'--{filt}', name, '-t'],
                capture_output=True, text=True, timeout=0.5
            )
            if test_result.returncode != 0:
                print(f"\033[1;33mWarning: Font {test_font} with filter {filt} failed: {test_result.stderr}\033[0m")
                sys.exit(1)
            else:
                print(f"\033[1;32mFont {test_font} test passed\033[0m")
        except subprocess.TimeoutExpired:
            print(f"\033[1;33mWarning: Font {test_font} timed out\033[0m")
            sys.exit(1)
        except subprocess.SubprocessError as e:
            print(f"\033[1;33mWarning: Error testing font {test_font}: {e}\033[0m")
            sys.exit(1)
        
        # Write .bashrc based on font choice
        with open(filename, "w") as new:
            username = name #os.getenv("USER", "user")
            if selected_font:
                # Use specific font
                new.write(f"""#!/bin/bash
toilet -f "{selected_font}" --{filt} "{username}" -t | lolcat
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]{username}\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]#\\[\\033[01;32m\\]'
""")
            else:
                # Use random font selection
                new.write(f"""#!/bin/bash
# Load fonts from cache
FONT_CACHE="{font_cache}"
if [ -f "$FONT_CACHE" ]; then
    FONTS=($(cat "$FONT_CACHE" | jq -r '.[]'))
    FONT_COUNT=${{#FONTS[@]}}
    if [ $FONT_COUNT -gt 0 ]; then
        RANDOM_FONT=${{FONTS[$RANDOM % $FONT_COUNT]}}
        toilet -f "$RANDOM_FONT" --{filt} "{name}" -t | lolcat
    else
        echo "No fonts available in $FONT_CACHE"
    fi
else
    echo "Font cache not found: $FONT_CACHE"
fi
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]{username}\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]#\\[\\033[01;32m\\]'
""")
        print("\n")
        print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
        print("\033[1;32m[-] Parrotify was successful! restart your terminal to apply changes.\033[0m")
        
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
    font_cache = str(Path.home()) + "/.parrotifyfonts"
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
            #print("\033[1;32mRestored .bashrc from {}\033[0m".format(backup_file))
        elif os.path.exists(filename):
            os.remove(filename)
            #print("\033[1;32mRemoved custom .bashrc\033[0m")
        else:
            #print("\033[1;32mNo custom .bashrc found\033[0m")
        print("\033[1;32mParrotify Removed Terminal Restored\033[0m")
    except OSError as e:
        print(f"\033[1;33mError handling .bashrc: {e}\033[0m")
    
    try:
        if os.path.exists(font_cache):
            os.remove(font_cache)
            # print("\033[1;32mRemoved font cache {}\033[0m".format(font_cache))
        else:
            # print("\033[1;36mNo font cache found\033[0m")
    except OSError as e:
        print(f"\033[1;33mError removing font cache: {e}\033[0m")
    
    print("\n")
    print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
    print("\033[1;32m[-] Revert was successful!restart your terminal.\033[0m")

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
    print("\033[1;34m          Created By Winter and Fixed by Tricetech\033[0m")
    print("\033[2;32m     Winter says Parrot is awesome ..  enjoy\033[0m")
    print("\033[1;32m   Mail: winterfreak@protonmail.com\033[0m")
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
    jq_path = "/data/data/com.termux/files/usr/bin/jq"
    
    if not os.path.exists(toilet_path):
        missing_deps.append("toilet")
    else:
        # print("\033[1;32mFound toilet at {}\033[0m".format(toilet_path))
    
    if not os.path.exists(lolcat_path):
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
        # print("\033[1;32mFound lolcat at {}\033[0m".format(lolcat_path))
    
    if not os.path.exists(jq_path):
        missing_deps.append("jq")
    else:
        # print("\033[1;32mFound jq at {}\033[0m".format(jq_path))
    
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
        #if available_fonts:
        #    print("\033[1;36mAvailable fonts:\033[0m")
        #    for font in available_fonts[:5]:
        #        print(f"  ✓ {font}")
    
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
