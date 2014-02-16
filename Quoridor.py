# Quoridor.py
#
# This file is the top-level API for a single game of Quoridor
#
# Author: wrongu
# Date: February 2014

from Board import Board
from Player import Player

class State:
	INIT = 0
	PLAYING = 1
	OVER = 2

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
	state = State.INIT
	board = None
	players = []
	history = [] # stack of moves, history[0] is first, history[-1] is last
	future = []  # stack of 'future moves' (i.e. the redo stack). future[-1] is the next move, future[0] is farthest in the future

	def __init__(self):
		self.board = Board()

	@require_state(State.INIT)
	def add_player(self, player):
		if isinstance(player, Player) and len(self.players) < 4:
			self.players.append(player)
		else:
			raise Exception("Cannot add a 5th player: %s" % str(player))

	@require_state(State.INIT)
	def begin_game(self):
		# assert player count
		# choose starting player
		self.state = State.PLAYING

if __name__ == '__main__':
	# Testing...
	q = Quoridor()
	q.add_player(Player('A'))
	q.add_player(Player('B'))
	q.add_player(Player('C'))
	q.add_player(Player('D'))
	q.begin_game()
	q.begin_game()
