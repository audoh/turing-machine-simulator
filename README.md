# Turing machine simulator
A Turing machine simulator written in Python.

Programs are represented as sets of quintuples in the format `current_state`, `current_symbol`, `next_state`, `next_symbol`, `head_direction`. Delineators are unnecessary (but should be used anyway for readability's sake).

A sample palindrome detector program is provided. Its minifed version is also provided to demonstrate that delineators aren't necessary for the program's functioning.

## Features:
- Choose from either continuous run or stepping
- Choose from line-by-line or live display
- Set or disable step delay
- See number of steps, number of head moves and state path
