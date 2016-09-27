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

class TuringMachine:
	'''
	A half-tape Turing machine.

	To set the rules for the machine,
	pass them as an array of 5-tuples
	to the `rules` attribute. The format
	of the 5-tuples is as follows:

		current_state, current_symbol, next_state, next_symbol, head_direction

	To execute the program, first set the
	input tape using the `input(string)`
	method. Then use `run()` for
	automatic execution, or `step()` to
	progress to the next step.

	The following attributes are
	available for configuration:

		display_rules   - display the current rule alongside the current state.
		display_path    - display the path of states at the end.
		step_time       - the time between automatic steps when using `run()`.

		silent       	- skip showing intermediate steps.
		verbose			- show extra information at each step.

		live            - show the state as a live display on a single line.
	'''

	# Configuration

	display_rules = False
	display_path = True
	step_time = 0.25

	silent = False
	verbose = False

	live = False

	# State

	state = 1
	head = 0
	rule = None
	_tape = ''

	@property
	def tape(self):
		return self._tape

	@tape.setter
	def tape(self, value):
		"""
		Feeds input tape to the Turing machine.
		"""

		self._tape = list(value)

		self.reset()

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

	def step(self):
		"""
		Progresses the Turing machine state.
		"""

		self.stepc += 1

		# Add empty spaces to array when
		# pointer moves beyond right edge

		if self.head == len(self._tape):
			self._tape.extend('_')

		scan = self._tape[self.head]
		self.rule = self.find_rule(self.state, scan)

		# Replace character as per rule

		replace = [self.rule[3]] if self.rule[3] != '*' else scan
		self._tape = self._tape[:self.head] + replace + self._tape[self.head + 1:]

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

		self.step_print(self.state == 0, self.state == 0)

	def run(self):
		"""
		Automatically progresses the Turing machine state
		every `step_time` seconds until program halt.
		"""

		while self.state != 0:
			self.step()

			if not self.silent:
				sleep(self.step_time)
			
		return self._tape

	# Print functions

	def step_print(self, end_mode = False, silent_override = False):
		"""
		Prints info about the current step.
		"""

		if end_mode:
			self.print_state(False, silent_override)

			print('')

			# Live mode needs an extra blank line

			if self.live:
				print('')

			self.print_tracking()
		else:
			self.print_state(True, silent_override)

	def print_tracking(self, nl = True):
		"""
		Prints tracking info so far.
		"""

		self.print_stepc(nl)
		self.print_head_moves(nl)

		if self.display_path:
			self.print_path(nl)

	def print_state(self, show_head = False, silent_override = False):
		"""
		Prints info about the current state.
		"""

		# Silence override provided for 'essential' info

		if self.silent and not silent_override:
			return False

		# Convert tape to string and insert head symbol

		tape_string = ''.join(self._tape).replace('_', ' ')
		out = tape_string + ' ' if not show_head else tape_string[:self.head] + '|' + tape_string[self.head:]

		# Uses carriage-return character for overwriting
		# the previous state when in live display mode

		end = '\r' if self.live else '\n'

		# Prepare format string

		formatstr = "{stepc} ({state}): >{out}<"

		if self.display_rules:
			formatstr += " R: {rule}"

		# Write

		stdout.write(formatstr.format(rule = self.rule, stepc = self.stepc, state = self.state, out=out))

		if self.verbose:
			stdout.write(' ')
			self.print_tracking(False)
		
		stdout.write(end)
		stdout.flush()

	def print_stepc(self, nl = True):
		"""
		Prints the step count so far.
		"""

		stdout.write("Steps: {stepc}{end}".format(stepc=self.stepc, end='\n' if nl else ' '))

	def print_head_moves(self, nl = True):
		"""
		Prints the number of head moves so far.
		"""

		stdout.write("Head moves: {moves}{end}".format(moves=self.head_moves, end='\n' if nl else ' '))

	def print_path(self, nl = True):
		"""
		Prints the state path so far.
		"""

		stdout.write("State path: {path}{end}".format(path=self.path, end='\n' if nl else ' '))

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
	For parsing args when run as __main__.
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

	turing.tape = argv['input']

	# Execute

	if argv['stepping_mode'] and not argv['silent']:
		while 1:
			if turing.state != 0:
				x = keypress()

				if ord(x) == 3:	# Interrupt on Ctrl+C
					raise KeyboardInterrupt
				elif x == 'i':	# Show current info so far
					turing.verbose = not turing.verbose

				turing.step()
			else:
				break
	else:
		output = turing.run()