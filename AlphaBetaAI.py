from threading import Thread
import time

class AlphaBetaAI2P(object):

	def __init__(self, qgame, pid):
		self.player = pid
		self.game = qgame
		self.processing = False
		self.leaves = 0
		self.thread = None

	def kill(self):
		if self.thread and self.processing:
			self.thread.exit()

	def is_processing(self):
		return self.processing

	def process(self, depth):
		"""Start processing for turn in a separate thread"""
		# processing acts as a lock
		if not self.processing:
			self.thread = Thread(target=self.__alpha_beta_top, args = (self.game.copy(), self.player, depth))
			self.thread.daemon = True
			self.thread.start()

	def __eval(self, state):
		pl = state.get_player(self.player)
		# length of shortest path is opposite to how good this state is.
		selfish = len(state.get_board().path(pl.position(), pl.goals()))
		# similarly, state is worst if other players are doing well
		cautious = min([len(state.get_board().path(p.position(), p.goals())) for p in state.others(self.player)])
		return selfish + cautious

	def __alpha_beta_top(self, state_copy, player, depthlimit):
		self.processing = True
		self.leaves = 0
		tstart = time.time()
		(turn, val) = self.__alpha_beta(depthlimit, state_copy)
		telapse = time.time() - tstart
		print "AI ENACTING TURN", turn
		print "STATS (depth %d):" % depthlimit
		print "\t%d leaf states visited" % self.leaves
		print "\t%f seconds total" % telapse
		self.game.do_turn(self.player, turn)
		self.processing = False

	def __alpha_beta(self, depth, state, minmax=1, alpha=-10000, beta=10000):
		# base case
		if depth == 0:
			self.leaves += 1
			return ('', self.__eval(state))
		best = ''
		# recursive case
		for turn in state.all_turns():
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