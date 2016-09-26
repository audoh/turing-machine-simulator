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

	# State

	state = 1
	head = 0
	rule = None
	tape = ''

	# Tracking

	stepc = 0
	head_moves = 0
	path = []

	def __init__(self, rules):
		self.rules = rules

	def reset(self):
		"""
		Resets the state of the Turing machine to the
		start.
		"""

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
		"""
		Given a state and scan, attempts to find a matching
		rule according to this Turing machine.
		"""

		for r in self.rules:
			if int(r[0]) == state and (str(r[1]) == scan or str(r[1]) == '*'):
				return r

		raise RuleNotFound(state, scan)

	def input(self, input):
		"""
		Feeds input tape to the Turing machine.
		"""

		self.tape = list(input)

		self.reset()

	def step(self):
		"""
		Progresses the Turing machine state.
		"""

		self.stepc += 1

		# Add empty spaces to array when
		# pointer moves beyond right edge

		if self.head == len(self.tape):
			self.tape.extend('_')

		scan = self.tape[self.head]
		self.rule = self.find_rule(self.state, scan)

		# Replace character as per rule

		replace = [self.rule[3]] if self.rule[3] != '*' else scan
		self.tape = self.tape[:self.head] + replace + self.tape[self.head + 1:]

		# Update Turing state

		head_direction = int(self.rule[4])

		self.state = int(self.rule[2])
		self.head += head_direction

		if head_direction:
			self.head_moves += 1

		self.path.append(self.state)

		# Check head is still within the tape

		if self.head < 0:
			raise TapeRunoff

		# Print state		

		self.step_print()

	def run(self):
		"""
		Automatically progresses the Turing machine state
		every `step_time` seconds until program halt.
		"""

		while self.state != 0:
			self.step()

			if not self.silent:
				sleep(self.step_time)
			
		return self.tape

	# Print functions

	def step_print(self):
		"""
		Prints info about the current step.
		"""

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
		"""
		Prints info about the current state.
		"""

		if self.silent and not silent_override:
			return False

		overwrite = self.live

		tape_string = ''.join(self.tape)
		out = tape_string if not show_pointer else tape_string[:self.head] + '|' + tape_string[self.head:]

		end = '\r' if overwrite else '\n'

		formatstr = "{stepc} ({state}): {out}"

		if self.display_rules:
			formatstr += " R: {rule}"

		formatstr += "{end}"

		stdout.write(formatstr.format(rule = self.rule, end = end, stepc = self.stepc, state = self.state, out=out))

	def print_stepc(self):
		"""
		Prints the step count so far.
		"""

		stdout.write("Steps: {stepc}\n".format(stepc=self.stepc))

	def print_head_moves(self):
		"""
		Prints the number of head moves so far.
		"""

		stdout.write("Head moves: {moves}\n".format(moves=self.head_moves))

	def print_path(self):
		"""
		Prints the state path so far.
		"""

		stdout.write("State path: {path}\n".format(path=self.path))

def _read_rules(file):
	"""
	Given an open file `file`, reads rules
	into 5-tuples separated by some
	non-word-character delineator.
	"""

	rules = []

	tup_buf = []
	sym_buf = ''

	for line in file:
		for char in line:
			if match("[-\w]", char):
				sym_buf += char
			elif sym_buf:
				tup_buf.append(sym_buf)
				sym_buf = ''

				if len(tup_buf) == 5:
					rules.append(tuple(tup_buf))
					tup_buf = []

	return rules

def _parse_args():
	"""
	Parses args when run as __main__.
	"""

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
	# Parse

	argv = vars(_parse_args())

	# Load

	with open(argv['path'], 'r') as f:
		rules = _read_rules(f)
		turing = TuringMachine(rules)

	# Configure

	turing.display_rules = argv['rules']
	turing.step_time = argv['step_time'] if not argv['fast'] else 0

	turing.silent = argv['silent']
	turing.live = argv['live']

	# Input

	turing.input(argv['input'])

	# Execute

	if argv['stepping_mode'] and not argv['silent']:
		while 1:
			turing.step()
			
			if turing.state != 0:
				x = keypress()

				# Interrupt on Ctrl+C

				if ord(x) == 3:
					raise KeyboardInterrupt
			else:
				break
	else:
		output = turing.run()