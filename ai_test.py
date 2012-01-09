# ai tests

import QuoridorGame
import Quoridor_AI_API
import time

gs = QuoridorGame.QuoridorGame("rich", "chris");

print "MOVES"
print Quoridor_AI_API.get_all_legal_moves(gs);
print "WALLS"
tstart = time.time();
print Quoridor_AI_API.get_all_legal_walls(gs);
tend = time.time();
telapsed = tend-tstart;
print "elapsed time:", telapsed, "seconds"