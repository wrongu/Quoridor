# Quoridor.py
#
# This contains the Quoridor class (the state-machine representation of a single game of Quoridor), with supporting
# functions, exceptions, and classes
#
# Author: wrongu
# Date: February 2014

from Board import Board
from Player import Player

class State:
	INIT = 0
	PLAYING = 1
	OVER = 2

class StateError(Exception):
	pass

class IllegalMove(Exception):
	pass

def require_state(st):
	'''A decorator method for requiring certain state

	because it takes a parameter, it is really a decorator inside a decorator...'''
	def decorator(fn):
		def wrapper(inst, *args):
			if inst.state == st:
				return fn(inst, *args)
			else:
				raise Exception("Bad state machine call %s() while in state %d" % (fn.__name__, inst.state))
		return wrapper
	return decorator

class Quoridor(object):
	'''A class representing a single game (2 or 4 player) of Quoridor.

	NOTATION:
		While grid locations are represented as a tuple of two numbers, the actual game notation uses letters for columns. 1-9 becomes a-i        
			(1,1) --> 1a
			(2,7) --> 2g
			(9,9) --> 9i
		
		A *move* is denoted by the notated-form of the destination. Moving from 3b to 3c is just "3c"
		A *wall* is denoted with a 3-character string. The first character is "H" or "V" for Horizontal or Vertical walls
			-horizontal walls lie between rows and span 2 columns
			-vertical walls lie between columns and span 2 rows

			the other 2 characters specify the point of the top-left corner of the wall (lowest row, lowest col)
			- must be between (1,1) and (8,8), or 1a and 8h
		
		visuals! (I suggest viewing with a fixed-width font)
		horizontal  vertical
		A  B        A || B
		====          ||
		C  D        C || D
		
		for both of these, the point "A" will be used to denote the wall's location. For example, a fully notated wall
		might be 'H4d' for a horizontal wall that touches 4d, 5d, 4e, and 5e

	'''
	state = State.INIT
	board = None
	players = []
	history = [] # stack of moves, history[0] is first, history[-1] is last
	future = []  # stack of 'future moves' (i.e. the redo stack). future[-1] is the next move, future[0] is farthest in the future

	def __init__(self):
		self.board = Board()
		self.current_player = -1

	@require_state(State.INIT)
	def create_player(self, pname):
		'''If game is not already full, add the specified player and return an id

		An id of -1 means the game is full
		'''
		if len(self.players) < 4:
			self.players.append(Player(name))
			return len(self.players)
		else:
			return -1

	@require_state(State.INIT)
	def begin_game(self):
		'''Start the game (move from INIT to PLAYING)

		An exception is raised if there are not 2 or 4 players
		'''
		if len(self.players) == 2 or len(self.players) == 4:
			self.current_player = 0
			self.state = State.PLAYING
		else:
			raise StateError("Cannot start a game with %d players" % len(self.players))

	def __try_turn(self, turn):
		if len(turn) == 2:
			# MOVE
			pass
		elif len(turn) == 3:
			# WALL
			pass

	@require_state(State.PLAYING)
	def do_turn(self, pid, turn):
		'''Attempt the given turn for the given player. If it is not that player's turn, a StateError is raised.

		A turn is either Moving or placing a Wall. The notation is as follows:

		# Moving: each row is 

		# Walls:
		'''
		if pid == self.current_player:
			try:
				self.__try_turn(turn)
			except IllegalMove as e:
				print "Illegal Move by %d: %s" % (pid, str(turn))
		else:
			raise StateError("Bad request for a turn by player %d. It's %d's turn." % (pid, self.current_player))

if __name__ == '__main__':
	# Testing...
	q = Quoridor()
	q.create_player(Player('A'))
	q.create_player(Player('B'))
	q.create_player(Player('C'))
	q.create_player(Player('D'))
	q.begin_game()
	q.begin_game()
