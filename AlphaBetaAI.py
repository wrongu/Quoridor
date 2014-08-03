from threading import Thread
import time

class AlphaBetaAI2P(object):

	def __init__(self, qgame, pid, wall_weight=1.0):
		self.player = pid
		self.game = qgame
		self.wall_weight = wall_weight
		self.processing = False
		self.leaves = 0
		self.thread = None
		self.result = ''

	def kill(self):
		if self.thread and self.processing:
			self.thread.exit()

	def is_processing(self):
		return self.processing

	def process(self, depth, callback=None):
		"""Start processing for turn in a separate thread"""
		# processing acts as a lock
		if not self.processing:
			self.__alpha_beta_top(self.game.copy(), depth, callback)
		else:
			print "AI already in use"

	def __eval(self, state):
		score = 0.0
		# game-over is kind of a big deal
		if state.game_is_over():
			score += (50 if state.get_current_pid() == self.player else -50)
		pl = state.get_player(self.player)
		# length of shortest path is opposite to how good this state is.
		score -= len(state.get_board().path(pl.position(), pl.goals()))
		# similarly, state is better if the best of other players is doing poorly
		score += min([len(state.get_board().path(p.position(), p.goals())) for p in state.others(self.player)])
		# hoarding walls is good, right?
		score += self.wall_weight * pl.num_walls()
		return score

	def __alpha_beta_top(self, state_copy, depthlimit, callback):
		self.processing = True
		self.leaves = 0
		tstart = time.time()
		(turn, val) = self.__alpha_beta(depthlimit, state_copy)
		telapse = time.time() - tstart
		print "AI ENACTING TURN", turn
		print "STATS (depth %d):" % depthlimit
		print "\t%d leaf states visited" % self.leaves
		print "\t%f seconds total" % telapse
		self.processing = False
		self.result = turn
		if callback:
			callback(turn)

	def __alpha_beta(self, depth, state, minmax=1, alpha=-10000, beta=10000):
		# base case
		if depth == 0 or state.game_is_over():
			self.leaves += 1
			return ('', self.__eval(state))
		best = ''
		# recursive case
		for turn in state.all_turns():
			# print "%s%d: turn %s" % (''.join(['  ']*depth), depth, turn)
			# copy state for next level, and perform the turn
			scopy = state.copy()
			 # TODO fix the hack:
			pid = self.player if minmax==1 else 1-self.player
			scopy.do_turn(pid, turn)
			# recurse
			(_, value) = self.__alpha_beta(depth-1, scopy, -minmax, -beta, -alpha)
			value *= minmax
			# if value is better than what we've found so far, record it
			# TODO some randomization
			if value > alpha:
				best = turn
				alpha = value
			# if we went past our ceiling, don't bother to keep looking
			if alpha >= beta:
				break
		return (best, alpha)