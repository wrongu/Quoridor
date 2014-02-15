# Quoridor.py
#
# This file is the top-level API for Quoridor functions. The logic is wrapped in a state machine with two states:
# INIT and PLAYING
#
# Author: wrongu
# Date: February 2014

from Board import Board

class State:
	INIT = 0
	PLAYING = 1

class Quoridor(object):
	state = State.INIT
	board = None
	players = []

	def __init__(self):
		self.board = Board()
		