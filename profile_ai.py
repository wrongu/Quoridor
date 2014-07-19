# AI profiler
import cProfile, pstats
from Quoridor import Quoridor
from AlphaBetaAI import AlphaBetaAI2P as AI

def newgame(p1="1P", p2="2P"):
	# create the game object
	g = Quoridor(2)
	g.create_player(p1)
	g.create_player(p2)
	g.begin_game()
	return g

def runprofile(depth=1):
	stats = None
	g = newgame()
	ai = AI(g, 0)
	fname ='tests/stats/AIProfile.dat'
	cProfile.runctx('ai.process(%d)' % depth, globals(), {'ai': ai}, fname)
	stats = pstats.Stats(fname)
	stats.sort_stats('tottime')
	stats.print_stats()

if __name__ == '__main__':
	from sys import argv
	if len(argv) > 1:
		runprofile(int(argv[1]))
	else:
		runprofile()