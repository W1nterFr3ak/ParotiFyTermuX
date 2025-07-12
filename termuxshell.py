#!/usr/bin/python3
import os
import sys
import time
import signal
import random
import argparse
from pathlib import Path


def get_parser():
    parser = argparse.ArgumentParser(description='Parrotify Terminal - Make your terminal look like Parrot OS')
    pars = parser.add_argument_group('Parrotify options')
    pars.add_argument('--parrotify', '-p', help='Make terminal look like parrot os',
                      action="store_true")
    pars.add_argument('--revert', '-r', help='Revert to normal look',
                      action="store_true")
    return parser


def get_available_fonts():
    """Get list of available toilet fonts"""
    available_fonts = []
    
    # Common fonts that are usually available with basic toilet
    common_fonts = ["standard", "big", "small", "mini", "block", "bubble", 
                   "digital", "script", "shadow", "banner"]
    
    # Popular extended fonts from toilet-fonts package
    extended_fonts = ["slant", "3d", "doom", "starwars", "gothic", "cyberlarge", 
                     "isometric1", "colossal", "graffiti", "larry3d"]
    
    all_fonts = common_fonts + extended_fonts
    
    # Check which fonts are actually available
    for font in all_fonts:
        # Test if font exists by running toilet command
        test_result = os.system(f"toilet -f {font} test > /dev/null 2>&1")
        if test_result == 0:
            available_fonts.append(font)
    
    # If no fonts found, add standard as fallback
    if not available_fonts:
        available_fonts = ["standard"]
    
    return available_fonts


def check_toilet_fonts_package():
    """Check if toilet-fonts package is available and offer to install it"""
    # Get current available fonts
    available_fonts = get_available_fonts()
    
    # Check if we have extended fonts (indicates toilet-fonts is installed)
    extended_fonts = ["slant", "3d", "doom", "starwars", "gothic"]
    has_extended = any(font in available_fonts for font in extended_fonts)
    
    if not has_extended and len(available_fonts) <= 10:
        print("\033[1;33m" + "="*60 + "\033[0m")
        print("\033[1;33mLooks like you're missing the `toilet-fonts` package!\033[0m")
        print("\033[1;36mThis package includes popular fonts like:\033[0m")
        print("\033[1;32m  - slant, 3d, doom, starwars, gothic\033[0m")
        print()
        print("\033[1;36mCurrent available fonts:\033[0m", end=" ")
        print("\033[1;32m" + ", ".join(available_fonts) + "\033[0m")
        print()
        
        # Detect package manager and suggest installation
        if os.system("which apt > /dev/null 2>&1") == 0:
            install_cmd = "sudo apt install toilet-fonts"
        elif os.system("which pkg > /dev/null 2>&1") == 0:  # Termux
            install_cmd = "pkg install toilet-fonts"
        elif os.system("which pacman > /dev/null 2>&1") == 0:  # Arch
            install_cmd = "sudo pacman -S toilet-fonts"
        elif os.system("which yum > /dev/null 2>&1") == 0:  # Red Hat/CentOS
            install_cmd = "sudo yum install toilet-fonts"
        elif os.system("which dnf > /dev/null 2>&1") == 0:  # Fedora
            install_cmd = "sudo dnf install toilet-fonts"
        else:
            install_cmd = "# Check your package manager for toilet-fonts"
        
        print(f"\033[1;36mTo install more fonts, run:\033[0m")
        print(f"\033[1;32m{install_cmd}\033[0m")
        print()
        
        response = input("\033[1;33mWould you like to install toilet-fonts now? (y/N): \033[0m").strip().lower()
        
        if response in ['y', 'yes']:
            print("\033[1;32mInstalling toilet-fonts...\033[0m")
            result = os.system(install_cmd)
            
            if result == 0:
                print("\033[1;32m✓ toilet-fonts installed successfully!\033[0m")
                print("\033[1;36mRe-scanning available fonts...\033[0m")
                time.sleep(2)
                # Return updated font list
                return get_available_fonts()
            else:
                print("\033[1;31m✗ Installation failed. You may need to run manually:\033[0m")
                print(f"\033[1;31m{install_cmd}\033[0m")
                print("\033[1;33mContinuing with available fonts...\033[0m")
                time.sleep(2)
        else:
            print("\033[1;33mSkipping installation. Continuing with available fonts...\033[0m")
            time.sleep(1)
        
        print("\033[1;33m" + "="*60 + "\033[0m")
        print()
    
    return available_fonts


def TermColor(name, filt):
    available_fonts = get_available_fonts()
    
    print(f"\033[1;36mAvailable fonts: {', '.join(available_fonts)}\033[0m")
    
    # Handle MOTD backup for Termux
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    try:
        if os.path.exists(motd_path) and not os.path.exists(motd_backup):
            os.system(f"mv {motd_path} {motd_backup}")
        else:
            print("Clear screen already set or MOTD backup exists")
    except Exception as e:
        print(f"Could not handle MOTD: {e}")
    
    # Update .bashrc
    filename = str(Path.home()) + "/.bashrc"
    
    try:
        with open(filename, "w") as new:
            selected_font = random.choice(available_fonts)
            print(f"\033[1;32mUsing font: {selected_font}\033[0m")
            
            # Test the command before writing to .bashrc
            test_cmd = f"toilet -f {selected_font} --{filt} {name} -t"
            test_result = os.system(f"{test_cmd} > /dev/null 2>&1")
            
            if test_result != 0:
                print(f"\033[1;33mWarning: Font {selected_font} with filter {filt} failed, using standard font\033[0m")
                selected_font = "standard"
            
            new.write(f"""toilet -f {selected_font} --{filt} {name} -t | lolcat
PS1='\\[\\033[01;34m\\]┌──\\[\\033[01;32m\\]root\\[\\033[01;34m\\]@\\[\\033[01;31m\\]\\h\\[\\033[00;34m\\]\\[\\033[01;34m\\]\\w\\[\\033[00;34m\\]\\[\\033[01;32m\\]:
\\[\\033[01;34m\\]└╼\\[\\033[01;31m\\]#\\[\\033[01;32m\\]'
""")
        print("\n\n")
        print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
        print("\033[1;32m[-] Parrotify was successful, closing terminal. Press Ctrl+C to abort\033[0m")
        
        countdown(10)
        
        try:
            os.kill(os.getppid(), signal.SIGHUP)
        except ProcessLookupError:
            print("\033[1;33mCould not close terminal automatically. Please restart your terminal manually.\033[0m")
        except KeyboardInterrupt:
            print("\nQuitting_*_*_*_*_*_")
            time.sleep(1)
            
    except IOError as e:
        print(f"Error writing to .bashrc: {e}")
        sys.exit(1)


def countdown(seconds):
    """Display a countdown with the ability to interrupt"""
    try:
        for i in range(seconds, 0, -1):
            print(f"\rClosing in {i} seconds... Press Ctrl+C to abort", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")  # Clear the line
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
    """Revert terminal to normal state"""
    filename = str(Path.home()) + "/.bashrc"
    motd_path = "/data/data/com.termux/files/usr/etc/motd"
    motd_backup = "/data/data/com.termux/files/usr/etc/motdback"
    
    # Restore MOTD if backup exists
    try:
        if os.path.exists(motd_backup):
            os.system(f"mv {motd_backup} {motd_path}")
    except Exception as e:
        print(f"Could not restore MOTD: {e}")
    
    # Remove custom .bashrc
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print("\033[1;32m!!! Custom .bashrc removed !!!\033[0m")
        else:
            print("\033[1;32m!!! Your termux is already normal !!!\033[0m")
    except OSError as e:
        print(f"Error removing .bashrc: {e}")
    
    print("\n\n")
    print("\033[1;32mPlease sip your coffee as winter works his magic -*-*-\033[0m")
    print("\n\n")
    
    try:
        print("\033[1;32m[-] Reversing Parrotify was successful, closing terminal. Press Ctrl+C to abort\033[0m")
        countdown(10)
        
        try:
            os.kill(os.getppid(), signal.SIGHUP)
        except ProcessLookupError:
            print("\033[1;33mCould not close terminal automatically. Please restart your terminal manually.\033[0m")
        except KeyboardInterrupt:
            print("\nQuitting_*_*_*_*_*_")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting_*_*_*_*_*_")
        time.sleep(1)


def display_banner():
    """Display the main banner"""
    available_fonts = get_available_fonts()
    
    os.system("clear")
    print("\033[1;31m")
    
    # Check if toilet command exists
    if os.system("which toilet > /dev/null 2>&1") == 0:
        selected_font = random.choice(available_fonts)
        banner_result = os.system(f"toilet -t -f {selected_font} --gay PAR0tifyTerm 2>/dev/null")
        
        # If banner failed, use ASCII fallback
        if banner_result != 0:
            print("\033[1;33mFallback banner (toilet command failed):\033[0m")
            print_ascii_banner()
    else:
        print("\033[1;33mFallback banner (toilet not found):\033[0m")
        print_ascii_banner()
    
    print("\033[1;32m")
    print("\033[1;32m")
    print("\033[1;34m          Created By Winter\033[0m")
     print("\033[1;34m         Fixed By Tricetech\033[0m")
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
    
    # Check for toilet command
    if os.system("which toilet > /dev/null 2>&1") != 0:
        missing_deps.append("toilet")
    
    # Check for lolcat command
    if os.system("which lolcat > /dev/null 2>&1") != 0:
        missing_deps.append("lolcat")
    
    if missing_deps:
        print("\033[1;33mWarning: The following dependencies are missing:\033[0m")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\033[1;33mInstall them with: pkg install toilet lolcat\033[0m")
        print()
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting...")
            sys.exit(1)
    else:
        # Check and potentially install toilet-fonts
        available_fonts = check_toilet_fonts_package()
        print(f"\033[1;36mDetected {len(available_fonts)} available toilet fonts\033[0m")
        return available_fonts
    
    return get_available_fonts()


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
            # Validate name (basic sanitization)
            if not name.replace(' ', '').replace('-', '').replace('_', '').isalnum():
                print("\033[1;31mError: Name should contain only alphanumeric characters, spaces, hyphens, and underscores\033[0m")
                sys.exit(1)
            
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
