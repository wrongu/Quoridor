# AI profiler
import cProfile, pstats
from Quoridor.Quoridor import Quoridor
from Quoridor.AlphaBetaAI import AlphaBetaAI2P as AI

def newgame(p1="1P", p2="2P"):
	# create the game object
	g = Quoridor(2)
	g.create_player(p1)
	g.create_player(p2)
	g.begin_game()
	return g

stats = None
if __name__ == '__main__':
	g = newgame()
	ai = AI(g, 0)
	depth = 1
	fname ='tests/stats/AIProfile.dat'
	cProfile.run('ai.process(%d)' % depth, fname)
	stats = pstats.Stats(fname)
	stats.sort_stats('tottime')
	stats.print_stats()