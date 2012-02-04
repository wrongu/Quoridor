# ai tests

import Game
import GameHelpers
import time

gs = Game.Game()

print "MOVES"
tstart = time.time();
moves =  GameHelpers.get_all_legal_moves(gs, 1);
tend = time.time();
telapsed = tend-tstart;
print moves
print "elapsed time:", telapsed, "seconds"
print "WALLS"
tstart = time.time();
walls = GameHelpers.get_all_legal_walls(gs);
tend = time.time();
telapsed = tend-tstart;
print walls
print "elapsed time:", telapsed, "seconds"