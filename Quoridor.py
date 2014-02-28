# Quoridor.py
#
# This contains the Quoridor class (the state-machine representation of a single game of Quoridor), with supporting
# functions, exceptions, and classes
#
# Author: wrongu
# Date: February 2014

from Board import Board, Node, Wall, Grid2D
from Player import Player
from Exceptions import IllegalMove, StateError

class State:
	INIT = 0
	PLAYING = 1
	OVER = 2

def require_state(st):
	'''A decorator method for requiring certain state

	because it takes a parameter, it is really a decorator inside a decorator...'''
	try:
		test = None in st
	except:
		st = [st]
	def decorator(fn):
		def wrapper(inst, *args):
			if inst.state() in st:
				return fn(inst, *args)
			else:
				raise StateError("Bad method call %s() while in state %d" % (fn.__name__, inst.state))
		return wrapper
	return decorator

def copy_only(fn):
	'''A decorator method that only works if the object is a copy'''
	def wrapper(inst, *args):
		if inst.is_copy():
			return fn(inst, *args)
		else:
			raise StateError("%s() may only be called on copies of the original state" % fn.__name__)
	return wrapper

class Quoridor(object):
	'''A class representing a single game (2 or 4 player) of Quoridor.

	NOTATION:
		While grid locations are represented as a tuple of two zero-indexed numbers, the actual game notation 
		uses letters for rows. 1-9 becomes a-i        
			(0,0) --> a1
			(1,6) --> g2
			(8,8) --> i9
		
		A *move* is denoted by the notated-form of the destination. Moving from b3 to c3 is just "c3"
		A *wall* is denoted with a 3-character string. The first character is "H" or "V" for Horizontal or Vertical walls
			-horizontal walls lie between rows and span 2 columns
			-vertical walls lie between columns and span 2 rows

			the other 2 characters specify the point of the top-left corner of the wall (lowest row, lowest col)
			- must be between (0,0) and (7,7), or a1 and h8
		
		visuals! (I suggest viewing with a fixed-width font)
		horizontal  vertical
		A  B        A || B
		====          ||
		C  D        C || D
		
		for both of these, the point "A" will be used to denote the wall's location. For example, a fully notated wall
		might be 'd4h' for a horizontal wall that touches d4, d5, e4, and e5

	'''

	ALL_WALLS = ['a1h', 'b1h', 'c1h', 'd1h', 'e1h', 'f1h', 'g1h', 'h1h',
				'a2h', 'b2h', 'c2h', 'd2h', 'e2h', 'f2h', 'g2h', 'h2h',
				'a3h', 'b3h', 'c3h', 'd3h', 'e3h', 'f3h', 'g3h', 'h3h',
				'a4h', 'b4h', 'c4h', 'd4h', 'e4h', 'f4h', 'g4h', 'h4h',
				'a5h', 'b5h', 'c5h', 'd5h', 'e5h', 'f5h', 'g5h', 'h5h',
				'a6h', 'b6h', 'c6h', 'd6h', 'e6h', 'f6h', 'g6h', 'h6h',
				'a7h', 'b7h', 'c7h', 'd7h', 'e7h', 'f7h', 'g7h', 'h7h',
				'a8h', 'b8h', 'c8h', 'd8h', 'e8h', 'f8h', 'g8h', 'h8h',
				'a1v', 'b1v', 'c1v', 'd1v', 'e1v', 'f1v', 'g1v', 'h1v',
				'a2v', 'b2v', 'c2v', 'd2v', 'e2v', 'f2v', 'g2v', 'h2v',
				'a3v', 'b3v', 'c3v', 'd3v', 'e3v', 'f3v', 'g3v', 'h3v',
				'a4v', 'b4v', 'c4v', 'd4v', 'e4v', 'f4v', 'g4v', 'h4v',
				'a5v', 'b5v', 'c5v', 'd5v', 'e5v', 'f5v', 'g5v', 'h5v',
				'a6v', 'b6v', 'c6v', 'd6v', 'e6v', 'f6v', 'g6v', 'h6v',
				'a7v', 'b7v', 'c7v', 'd7v', 'e7v', 'f7v', 'g7v', 'h7v',
				'a8v', 'b8v', 'c8v', 'd8v', 'e8v', 'f8v', 'g8v', 'h8v']

	def __init__(self, n_players=2):
		if n_players != 2 and n_players != 4:
			raise StateError("Number of players must be either 2 or 4")
		self.__state = State.INIT
		self.__played_walls = []
		self.__board = Board()
		self.__current_player = -1
		self.__n_players = n_players
		self.__players = []
		self.__player_moves = [] # player_moves is an array of square notations where the current player may move to, updated at the start of their turn
		self.__original = True
		self.__callbacks = []

	def state(self):
		return self.__state

	@require_state(State.PLAYING)
	def moveables(self):
		return self.__player_moves

	def copy(self):
		QCopy = Quoridor(self.__n_players)
		QCopy.__state = self.__state
		QCopy.__played_walls = [w for w in self.__played_walls]
		QCopy.__board = self.__board.copy()
		QCopy.__current_player = self.__current_player
		QCopy.__n_players = self.__n_players
		QCopy.__players = [p.copy() for p in self.__players]
		QCopy.__player_moves = [mv for mv in self.__player_moves]
		QCopy.__original = False
		return QCopy

	def register_callback(self, fn):
		self.__callbacks.append(fn)

	@copy_only
	def get_player(self, pid):
		return self.__players[pid]

	@copy_only
	def get_board(self):
		return self.__board

	@copy_only
	def others(self, pid):
		others = self.__players[0:pid]
		others.extend(self.__players[(pid+1):])
		return others

	# TODO remove this - dangerous!
	def get_current_pid(self):
		return self.__current_player

	def is_copy(self):
		return self.__original is False

	@require_state([State.PLAYING, State.OVER])
	def summary(self):
		"""return a dict representation (copy such that writes dont matter) of the current state of the game

		Dict structure:
			{
				players : { position : (name, num walls), ... },
				board : (see Board.summary)
			}"""
		grid = Grid2D(Board.SIZE, Board.SIZE)
		return {
			'players' : dict(zip([p.position() for p in self.__players], [(str(p), p.num_walls()) for p in self.__players])),
			'board' : self.__board.summary()
		}

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
		if len(self.__players) < self.__n_players:
			next_id = len(self.__players)
			self.__players.append(Player(pname,
				starts[self.__n_players][next_id],
				goals [self.__n_players][next_id],
				5 if self.__n_players == 4 else 10))
			return next_id
		else:
			raise StateError("The game is already full!")

	@require_state(State.INIT)
	def begin_game(self):
		'''Start the game (move from INIT to PLAYING)

		An exception is raised if there are not the correct number of players
		'''
		if len(self.__players) == self.__n_players:
			self.__current_player = 0
			self.__state = State.PLAYING
			self.__player_moves = self.__prep_moves(self.__current_player)
		else:
			raise StateError("Cannot start a game with %d players" % len(self.__players))

	@require_state(State.PLAYING)
	def do_turn(self, pid, turnstring):
		'''Attempt the given turn for the given player. If it is not that player's turn, a StateError is raised.

		A turn is either Moving or placing a Wall. The notation is as follows:
		'''
		if pid == self.__current_player:
			legal, info = self.turn_is_legal(turnstring)
			if legal:
				if isinstance(info, Node):
					self.__player().update_position(info.position)
				elif isinstance(info, Wall):
					self.__board.add_wall(info)
					self.__played_walls.append(turnstring)
					self.__player().use_wall()
				else:
					raise StateError("broken internal function turn_is_legal")
				# game could be over
				if self.__game_is_over():
					self.__state = State.OVER
					# note that by changing the state, no futher moves may be made, and "current_player"
					# is now the winning player
				else:
					# advance to next player
					self.__current_player = (self.__current_player + 1) % len(self.__players)
					# update moves now that it's a new player's turn
					self.__player_moves = self.__prep_moves(self.__current_player)
				# on successful turn, do callbacks
				for fn in self.__callbacks:
					fn()
			else:
				raise IllegalMove(info)
		else:
			raise StateError("Bad request for a turn by player %d. It's %d's turn." % (pid, self.__current_player))

	@require_state(State.PLAYING)
	def turn_is_legal(self, turnstring):
		if len(turnstring) == 2:
			# MOVE
			# self.__player_moves is updated at the start of this turn with all locations where the current
			# player may move.. so this is a simple lookup
			try:
				n = Node.parse(turnstring)
			except:
				return (False, "Cannot parse %s as a Node" % turnstring)
			if n in self.__player_moves:
				return (True, Node(n))
			else:
				return (False, "%s cannot move to %s" % (str(self.__player()), turnstring))
		elif len(turnstring) == 3:
			try:
				w = Wall.parse(turnstring)
				(wr, wc) = w.position
				if wr < 0 or wr+1 >= Board.SIZE or wc < 0 or wc+1 >= Board.SIZE:
					return (False, "%s is out of bounds" % turnstring)
			except:
				return (False, "Cannot parse %s as a Wall" % turnstring)
			# check if current player has any walls remaining
			if self.__player().num_walls() <= 0:
				return (False, "Player %s has no remaining walls" % str(self.__player()))
			# check if it has already been played
			if turnstring in self.__played_walls:
				return (False, "Wall %s has already been played" % turnstring)
			
			# check if the crossing wall (+ shape) has been played (can't overlap)
			if Wall.cross(turnstring) in self.__played_walls:
				return (False, "Walls may not cross")
			# check if offset walls (colinear, one space to the side) have been played
			for shifted in Wall.shift(turnstring):
				if shifted in self.__played_walls:
					return (False, "Walls may not overlap")
			
			## ADD WALL ##
			self.__board.add_wall(w)
			# check player paths
			for p in self.__players:
				if not self.__board.path(p.position(), p.goals()):
					self.__board.remove_wall(w)
					return (False, "Wall cuts off the path for %s" % str(p))
			
			## REMOVE WALL ## (check complete)
			self.__board.remove_wall(w)

			# all checks passed!
			return (True, w)
		else:
			return (False, "%s is not a valid turn string" % turnstring)

	@require_state(State.PLAYING)
	def all_turns(self):
		lst = [Node.notate(mv) for mv in self.__player_moves]
		lst.extend(filter(lambda w : self.turn_is_legal(w)[0], Quoridor.ALL_WALLS))
		return lst

	@require_state(State.PLAYING)
	def undo(self):
		pass # TODO

	@require_state(State.PLAYING)
	def redo(self):
		pass # TODO

	@require_state(State.PLAYING)
	def __prep_moves(self, pid):
		pl = self.__players[pid]
		(pr, pc) = pl.position()
		# get all adjacent squares (0 to 4 of them)
		adjacents = set(self.__board.neighbors(pl.position()))
		players_pos = set([p.position() for p in self.__players])
		# free to step to any adjacent squares that do not have players on them
		steppable = list(adjacents - players_pos)
		# further processing required if player is adjacent - pl can jump
		jumps = adjacents & players_pos
		for (jr, jc) in jumps:
			# need to know direction we are going
			(dir_r, dir_c) = (jr-pr, jc-pc)
			# simple jump: over other player
			simple_next = (jr + dir_r, jc+dir_c)
			# test if simple jump is ok (i.e. no wall and no 3rd player there)
			if self.__board.can_step((jr,jc), simple_next) and simple_next not in players_pos:
					steppable.append(simple_next)
			else:
				# jump is blocked either by a wall or by a 3rd player. this is where diagonal moves are allowed
				two_away = (simple_next[0] + dir_r, simple_next[1] + dir_c)
				diagonals_set = set(self.__board.neighbors((jr,jc))) - set([pl.position(), two_away])
				steppable.extend(list(diagonals_set))
		return steppable
 
	@require_state(State.PLAYING)
	def __player(self):
		return self.__players[self.__current_player]

	def __game_is_over(self):
		for p in self.__players:
			if p.reached_goal():
				return True

if __name__ == '__main__':
	# Testing...
	q = Quoridor()
	q.create_player(Player('A'))
	q.create_player(Player('B'))
	q.create_player(Player('C'))
	q.create_player(Player('D'))
	q.begin_game()
	q.begin_game()
