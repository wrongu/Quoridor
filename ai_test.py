# ai tests

import QuoridorGame
import Quoridor_AI_API
import time

gs = QuoridorGame.QuoridorGame()

print "MOVES"
tstart = time.time();
moves =  Quoridor_AI_API.get_all_legal_moves(gs, 1);
tend = time.time();
telapsed = tend-tstart;
print moves
print "elapsed time:", telapsed, "seconds"
print "WALLS"
tstart = time.time();
walls = Quoridor_AI_API.get_all_legal_walls(gs);
tend = time.time();
telapsed = tend-tstart;
print walls
print "elapsed time:", telapsed, "seconds"