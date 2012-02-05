from time import time
import json
from threading import Thread

class TreeAI():
    
    INF = 1000000
    DEFAULT_WEIGHTS = [0.5, 1.0]
    PLY_COUNT = 0
    
    def __init__(self, score_func=None, score_weights=None):
        if score_func:
            self.score_func = score_func
        elif score_weights:
            self.score_func = lambda gs: TreeAI.state_score_naive(gs, score_weights)
        else:
            self.score_func = lambda gs: TreeAI.state_score_naive(gs, self.DEFAULT_WEIGHTS)
        self.threaded_turn = ""
    
    @classmethod
    def state_score_naive(self, game_state, weights):
        """return naive score for game state based on # of walls and path lengths only.
        higher score corresponds to better position for the current player
        
        (diff in # of walls) * (1-weight) + (diff in path lengths) * weight
    
        computes for current_player
        """
        my_walls = game_state.current_player.num_walls
        their_walls = max([p.num_walls for p in game_state.other_players])
        walls_diff = (my_walls - their_walls)
        my_path = len(game_state.get_shortest_path_player(game_state.current_player))
        their_path = min([len(game_state.get_shortest_path_player(p)) for p in game_state.other_players])
        paths_diff = their_path - my_path
        
        return weights[0]*walls_diff + weights[1]*paths_diff
    
    def get_move_thread_start(self, *args, **kargs):
        th = Thread(target=lambda:self.get_move(args, kargs))
        th.start()
    
    def get_threaded_move(self):
        if self.threaded_turn:
            turn = self.threaded_turn
            self.threaded_turn = ""
            return turn
        else:
            return None
      
    def get_move(self, game_state_copy):
        print "AI: GET_MOVE CALLED"
        gs = game_state_copy
        all_plies = gs.legal_moves + gs.legal_walls
        scores = [-self.INF] * len(all_plies)
        self.PLY_COUNT = 0
        tstart = time()
        for i in range(len(all_plies)):
            ply = all_plies[i]
            gs.execute_turn(ply)
            scores[i] = self.NegaMax(gs)
            print "%-5sscored %f" % (ply, scores[i])
            gs.undo()
        # now sort by score
        score_ply = zip(scores, all_plies)
        score_ply = sorted(score_ply, reverse=True)
        best_score, best_ply = score_ply[0]
        all_best = [ply for score, ply in score_ply if score == best_score]
        chosen_ply = random.choice(all_best)
        print "analyzed %d positions in %f seconds" % (self.PLY_COUNT, time()-tstart)
        print "Best Move is %s with score %f" % (chosen_ply, best_score)
        print "---------------------------------------------"
        self.threaded_turn = best_ply
        return best_ply
    
    def NegaMax(self, game_state_copy, minmax=-1, depth=1, timeout=None, start_time=None, print_space=" "):
        """Negamax implementation
        
        Note: only for 2-player
        """
        gs = game_state_copy
        if not start_time:
            start_time = time()
        if depth == 0 or (timeout and time()-start_time > timeout):
            self.PLY_COUNT += 1
            score = self.score_func(gs)
            return minmax * score
        max_score = -self.INF
        all_plies = gs.legal_moves + gs.legal_walls
        for ply in all_plies:
            gs.execute_turn(ply)
            #print "%d%s%s" % (depth-1, print_space, ply)
            max_score = max(max_score, self.NegaMax(gs, -minmax, depth-1, timeout, start_time, print_space+"   "))
            gs.undo()
        
        return max_score
    
    def AlphaBeta(self, game_state_copy, my_num):
        pass
        # TODO - sort turns so most relevant are first