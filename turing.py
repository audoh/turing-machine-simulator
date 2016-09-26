from time import sleep
from re import match
from argparse import ArgumentParser
from sys import stdout, stdin
from keypress import keypress

class RuleNotFound(Exception):
	def __init__(self, state, char):
		self.value = (state, char)
	def __str__(self):
		return repr("No rule found from state {0[0]} with char {0[1]}.".format(self.value))

class TapeRunoff(Exception):
	def __str__(self):
		return repr("Attempted to run off the left-side of the tape.")

# Half-tape Turing Machine

class TuringMachine:

	# Configuration

	display_rules = False
	display_path = True
	step_time = 0.25

	silent = False

	live = False

	# State variables

	state = 1
	head = 0
	rule = None
	string = ''

	# Tracking

	stepc = 0
	head_moves = 0
	path = []

	def __init__(self, rules):
		self.rules = rules

	def reset(self):
		# Reset state variables

		self.state = 1
		self.head = 0
		self.rule = None

		# Reset tracking variables

		self.stepc = 0
		self.head_moves = 0
		self.path = [1]

		self.print_state()

	def find_rule(self, state, scan):
		for r in self.rules:
			if int(r[0]) == state and (str(r[1]) == scan or str(r[1]) == '*'):
				return r

		raise RuleNotFound(state, scan)

	def input(self, input):
		self.string = list(input)

		self.reset()

	def step(self):
		self.stepc += 1

		# Add empty spaces to array when
		# pointer moves beyond right edge

		if self.head == len(self.string):
			self.string.extend('_')

		scan = self.string[self.head]
		self.rule = self.find_rule(self.state, scan)

		# Replace character as per rule

		replace = [self.rule[3]] if self.rule[3] != '*' else scan
		self.string = self.string[:self.head] + replace + self.string[self.head + 1:]

		# Update Turing state

		self.state = int(self.rule[2])
		self.head += int(self.rule[4])
		self.path.append(self.state)

		if self.head:
			self.head_moves += 1

		# Check head is still within the tape

		if self.head < 0:
			raise TapeRunoff

		# Print state		

		self.step_print()

	def run(self):
		while self.state != 0:
			self.step()

			if not self.silent:
				sleep(self.step_time)
			
		return self.string

	# Print functions

	def step_print(self):
		if self.state == 0:
			self.print_state(False, True)

			if self.live:
				print()

			print('')

			self.print_stepc()
			self.print_head_moves()

			if self.display_path:
				self.print_path()
		else:
			self.print_state(True)

	def print_state(self, show_pointer = False, silent_override = False):
		if self.silent and not silent_override:
			return False

		overwrite = self.live

		string = ''.join(self.string)
		out = string if not show_pointer else string[:self.head] + '|' + string[self.head:]

		end = '\r' if overwrite else '\n'

		formatstr = "{stepc} ({state}): {out}"

		if self.display_rules:
			formatstr += " R: {rule}"

		formatstr += "{end}"

		stdout.write(formatstr.format(rule = self.rule, end = end, stepc = self.stepc, state = self.state, out=out))

	def print_stepc(self):
		stdout.write("Steps: {stepc}\n".format(stepc=self.stepc))

	def print_head_moves(self):
		stdout.write("Head moves: {moves}\n".format(moves=self.head_moves))

	def print_path(self):
		stdout.write("State path: {path}\n".format(path=self.path))

def read_rules(file):
	rules = []
	num_buf = []

	neg = '';

	for line in file:
		for char in line:
			if char == '-':
				neg = '-'
			elif match("[\w]", char):
				num_buf.append(neg + char)
				neg = ''

				if len(num_buf) == 5:
					rules.append(tuple(num_buf))
					num_buf = []

	return rules

def parse_args():
	parser = ArgumentParser(description='Simulates the action of a Turing Machine.')

	parser.add_argument('path', help="Path of a file containing rule quintuples.")
	parser.add_argument('input', help="Input string.")

	parser.add_argument('--rules', action='store_true', help="Displays the rules alongside the state.")

	parser.add_argument('--step_time', type=float, default=0.250, help="Sets the delay between steps (in seconds). Default is 0.25.")
	parser.add_argument('--fast', action='store_true', dest='fast', help="Removes the delay between steps (equivalent to --step_time=0).")
	parser.add_argument('--silent', action='store_true', help="Hides intermediate states.")

	parser.add_argument('--live', action='store_true', help="Displays a single, continuously changing state representation")

	parser.add_argument('-s', action='store_true', dest='stepping_mode', help="Enables stepping mode, in which you press a key to progress to each further step.")
	return parser.parse_args()

if __name__ == "__main__":
	argv = vars(parse_args())

	with open(argv['path'], 'r') as f:
		rules = read_rules(f)
		turing = TuringMachine(rules)

	turing.display_rules = argv['rules']
	turing.step_time = argv['step_time'] if not argv['fast'] else 0

	turing.silent = argv['silent']
	turing.live = argv['live']

	turing.input(argv['input'])

	if argv['stepping_mode'] and not argv['silent']:
		while(turing.state != 0):
			turing.step()
			keypress()
	else:
		output = turing.run()