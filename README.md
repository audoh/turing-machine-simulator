# Turing machine simulator
A simple half-tape Turing machine simulator written in Python.

## Notes on usage
- Programs are represented as sets of quintuples in the format `current_state`, `current_symbol`, `next_state`, `next_symbol`, `head_direction`.
- The start state is always 1.
- The halt state is always 0.
- Head direction is an integer where -1 moves left, 0 does nothing and 1 moves right.

A sample palindrome detector program is provided.

## Features
- Choose from either continuous run or stepping.
- Choose from line-by-line or live display.
- Set or disable step delay.
- See number of steps, number of head moves and state path.
- While stepping, press 'i' to switch to verbose mode. Be careful of issue [#1](/issues/1).
