from platform import system

def keypress_linux():
	import tty
	import sys
	import termios

	orig_settings = termios.tcgetattr(sys.stdin)
	tty.setraw(sys.stdin)

	x = 0	
	x = sys.stdin.read(1)[0]

	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

	return x

def keypress_windows():
	from msvcrt import getch

	x = getch()

	return x.decode("utf-8")

def keypress():
	p = system()

	if p == "Windows":
		return keypress_windows()
	elif p == "Linux":
		return keypress_linux()