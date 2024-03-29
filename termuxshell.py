#!/usr/bin/python3
import os
import sys
import time
import signal
import random
import argparse
from pathlib import Path



def get_parser():
	parser = argparse.ArgumentParser()
	pars   = parser.add_argument_group('Parrotify options')
	pars.add_argument('--parotify', '-p', help='Make terminal look like parrot os',
					action="store_true")
	pars.add_argument('--revert', '-r', help='Revert to normal look',
					action="store_true")
	return parser
	
def TermColor(name, filt):
	fonts = ["banner","big","block","bubble","digital","ivrit","mini","script","shadow","slant","small","smscript","smshadow","smslant","standard"]
	random.shuffle(fonts)
	try:
		open("/data/data/com.termux/files/usr/etc/motd")
		os.system("cd $HOME && cd .. && mv usr/etc/motd usr/etc/motdback ")
	except FileNotFoundError as e:
		print("Clear  Screen already set")
	filename = str(Path.home()) + "/.bashrc"
	
	new = open(filename, "w+")
	new.write(f"""toilet -f {fonts[random.randint(0, len(fonts)-1)]} --{filt} {name} -t | lolcat
PS1='\033[01;34m\]┌──\[\033[01;32m\]root\[\033[01;34m\]@\[\033[01;31m\]\h\[\033[00;34m\]\[\033[01;34m\]\w\[\033[00;34m\]\[\033[01;32m\]:
\[\033[01;34m\]└╼\[\033[01;31m\]#\[\033[01;32m\]'
""")
	print("\n\n")
	os.system('echo "\\e[1;32m Please sip your coffee as winter works his magic -*-*- \\e[0m"')
	try:
		os.system('echo "\\e[1;32m[-] Parrotify was succesfull, closing terminal  ctrl + c  to abort  \\e[0m"')
		time.sleep(10)
		try:
			os.kill(os.getppid(), signal.SIGHUP)
		except KeyboardInterrupt as e:
			print("\nQuiting_*_*_*_*_*_")
			time.sleep(3)

	except KeyboardInterrupt as e:
		print("\nQuiting_*_*_*_*_*_")
		time.sleep(3)
	
	
def choose_filter():
	print("\n\n")
	os.system('echo "\\e[1;34m  1) gay: add a rainbow colour effect\\e[0m"')
	os.system('echo "\\e[1;34m  2) metal: add a metallic colour effect\\e[0m"')
	print("\n\n")
	form = name = input("Enter filter number default(1) :")
	
	return form
	
def reversify():
	filename = str(Path.home()) + "/.bashrc"
	os.system("cd $HOME && cd .. && mv usr/etc/motdback usr/etc/motd ")
	try:
		os.remove(filename)
	except FileNotFoundError as e:
		os.system('echo "\\e[1;32m !!! Your termux is completely normal!!! \\e[0m"')
	print("\n\n")
	os.system('echo "\\e[1;32m Please sip your coffee as winter works his magic -*-*- \\e[0m"')
	
	print('\n\n')
	try:
		os.system('echo "\\e[1;32m[-] Reversing Parrotify was succesful, closing terminl  ctrl + c  to abort  \\e[0m"')
		time.sleep(10)
		try:
			os.kill(os.getppid(), signal.SIGHUP)
		except KeyboardInterrupt as e:
			print("\nQuiting_*_*_*_*_*_")
			time.sleep(3)

	except KeyboardInterrupt as e:
		print("\nExiting_*_*_*_*_*_")
		time.sleep(3)
	
	
def main():
	fonts = ["block","bubble","digital","ivrit","mini","script","shadow","slant","small","smscript","smshadow","smslant","standard"]
	random.shuffle(fonts)
	os.system("clear")
	os.system('echo  "\\e[1;31m\"')
	os.system(f"toilet -t -f {fonts[random.randint(0, len(fonts)-1)]} --gay  PAR0tifyTerm   ")
	os.system('echo "\\e[1;32m\"')
	os.system('echo "\\e[1;32m\"')
	os.system('echo "\\e[1;34m          Created By W1nterFr3ak\\e[0m"')
	os.system('echo "\\e[2;32m     Winter says Parrot is awesome \\e[0m"')
	os.system('echo "\\e[1;32m   Mail: WinterFreak@protonmaail.comm \\e[0m"')
	print()
	parser = get_parser()
	args   = vars(parser.parse_args())
	parrot = args['parotify']
	rev    = args['revert']
	
	if rev and parrot:
		os.system('echo "\\e[1;32m              !!! CHOOSE ONE OPTION !!! \\e[0m"')
		print("\n\n")
		parser.print_help()
		
	elif parrot:
		
		name = input("Enter name to be displayed in termux :")
		
		
		if len(name) > 0:
			form = choose_filter()
			
			if form == '1':
				form = 'gay'
				TermColor(name, form)
			elif form == '2':
				form = 'metal'
				TermColor(name, form)
			elif form.lower == "q":
				sys.exit()
			else:
				print("Using option one")
				form =  "gay"
				TermColor(name,  form)		
		else:
			os.system('echo "\\e[1;32m !!! Please rerun the  script and input the name to be displayed!!! \\e[0m"')
			sys.exit(1)
			
	elif rev:
		reversify()
	else:
		parser.print_help()

if __name__ == "__main__":
	main()

