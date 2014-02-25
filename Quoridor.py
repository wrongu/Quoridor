# Quoridor.py
#
# This contains the Quoridor class (the state-machine representation of a single game of Quoridor), with supporting
# functions, exceptions, and classes
#
# Author: wrongu
# Date: February 2014

from Board import Board, Node, Wall
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
				raise StateError("Bad method call %s() while in state %d" % (fn.__name__, inst.state))
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
	self.played_walls = []

	ALL_WALLS = ['H1a', 'H1b', 'H1c', 'H1d', 'H1e', 'H1f', 'H1g', 'H1h',
				'H2a', 'H2b', 'H2c', 'H2d', 'H2e', 'H2f', 'H2g', 'H2h',
				'H3a', 'H3b', 'H3c', 'H3d', 'H3e', 'H3f', 'H3g', 'H3h',
				'H4a', 'H4b', 'H4c', 'H4d', 'H4e', 'H4f', 'H4g', 'H4h',
				'H5a', 'H5b', 'H5c', 'H5d', 'H5e', 'H5f', 'H5g', 'H5h',
				'H6a', 'H6b', 'H6c', 'H6d', 'H6e', 'H6f', 'H6g', 'H6h',
				'H7a', 'H7b', 'H7c', 'H7d', 'H7e', 'H7f', 'H7g', 'H7h',
				'H8a', 'H8b', 'H8c', 'H8d', 'H8e', 'H8f', 'H8g', 'H8h',
				'V1a', 'V1b', 'V1c', 'V1d', 'V1e', 'V1f', 'V1g', 'V1h',
				'V2a', 'V2b', 'V2c', 'V2d', 'V2e', 'V2f', 'V2g', 'V2h',
				'V3a', 'V3b', 'V3c', 'V3d', 'V3e', 'V3f', 'V3g', 'V3h',
				'V4a', 'V4b', 'V4c', 'V4d', 'V4e', 'V4f', 'V4g', 'V4h',
				'V5a', 'V5b', 'V5c', 'V5d', 'V5e', 'V5f', 'V5g', 'V5h',
				'V6a', 'V6b', 'V6c', 'V6d', 'V6e', 'V6f', 'V6g', 'V6h',
				'V7a', 'V7b', 'V7c', 'V7d', 'V7e', 'V7f', 'V7g', 'V7h',
				'V8a', 'V8b', 'V8c', 'V8d', 'V8e', 'V8f', 'V8g', 'V8h']

	def __init__(self, n_players=2):
		self.board = Board()
		self.current_player = -1
		self.n_players = n_players
		if self.n_players != 2 and self.n_players != 4:
			raise StateError("Number of players must be either 2 or 4")

	@require_state(State.INIT)
	def create_player(self, pname):
		'''If game is not already full, add the specified player and return their id
		'''
		starts = {
			2 : [(0,4), (8,4)],
			4 : [(0,4), (4,8), (8,4), (4,0)]
		}
		goals = {
			2 : [[(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8)],
				 [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8)]],
			4 : [[(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8)],
				 [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0)],
				 [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8)],
				 [(0,8),(1,8),(2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8)]]
		}
		if len(self.players) < self.n_players:
			next_id = len(self.players)
			self.players.append(Player(name,
				starts[self.n_players][next_id],
				goals [self.n_players][next_id]))
			return next_id
		else:
			raise StateError("The game is already full!")

	@require_state(State.INIT)
	def begin_game(self):
		'''Start the game (move from INIT to PLAYING)

		An exception is raised if there are not the correct number of players
		'''
		if len(self.players) == self.n_players:
			self.current_player = 0
			self.state = State.PLAYING
		else:
			raise StateError("Cannot start a game with %d players" % len(self.players))

	@require_state(State.PLAYING)
	def __current_player(self):
		return self.players[self.current_player]

	@require_state(State.PLAYING)
	def __try_turn(self, turn):
		"""Execute the given turn for the current player, or raise an IllegalMove exception"""
		# TODO ? check format
		if len(turn) == 2:
			# MOVE
			newpos = Node.parse(turn)
			playerpos = self.__current_player().get_position()
			if self.board.can_step(playerpos, newpos):
				self.__current_player().update_position(newpos)
		elif len(turn) == 3:
			# check if it has already been played
			if turn in self.played_walls:
				raise IllegalMove("%s has already been played" % turn)
			# check if the crossing wall (+ shape) has been played (can't overlap)
			if Wall.cross(turn) in self.played_walls:
				raise IllegalMove("Walls may not cross")
			# check players' paths to goals
		else:
			raise IllegalMove("%s is not a turn string" % turn)

	def __game_is_over(self):
		for p in self.players:
			if p.reached_goal():
				return True

	@require_state(State.PLAYING)
	def do_turn(self, pid, turn):
		'''Attempt the given turn for the given player. If it is not that player's turn, a StateError is raised.

		A turn is either Moving or placing a Wall. The notation is as follows:

		# Moving: each row is 

		# Walls:
		'''
		if pid == self.current_player:
			try:
				# try executing the turn
				self.__try_turn(turn)
				# if no exception, it was successful.
				self.current_player = (self.current_player + 1) % len(self.players)
				# (game could be over though)
				if self.__game_is_over():
					self.state = State.OVER
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
