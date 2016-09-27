class HalfTape:
	'''
	Half of a tape for a Turing machine.
	'''

	def __init__(self, array = []):
		self._tape = list(array)

	def __str__(self):
		out = ''

		for b in self._tape:
			out += str(b)

		return out

	def __add__(self, operand):
		return HalfTape(self._tape + operand._tape)

	def _extend(self, index):
		dif = index + 1 - len(self)

		if dif > 0:
			self._tape.extend(['_'] * dif)
			return True
		else:
			return False

	def __getitem__(self, index):
		self._extend(index)
		return self._tape[index]

	def __setitem__(self, index, value):
		self._extend(index)
		self._tape[index] = value

	def __len__(self):
		return len(self._tape)

class Tape:
	'''
	Tape for a Turing machine.
	'''

	def __init__(self, array = []):
		self._right = HalfTape(array)
		self._left = HalfTape()

	def __str__(self):
		return str(HalfTape(reversed(self._left)) + self._right)

	def __getitem__(self, index):
		if index < 0:
			index = -index - 1
			return self._left[index]
		else:
			return self._right[index]

	def __setitem__(self, index, value):
		if index < 0:
			index = -index - 1
			self._left[index] = value
		else:
			self._right[index] = value