from time import time, sleep
import json
from threading import Thread
import random
import Helpers as h

class TreeAI():
    
    INF = 1000000
    DEFAULT_WEIGHTS = [0.5, 1.0]
    PLY_COUNT = 0
    
    def __init__(self, score_func=None, score_weights=None):
        if score_func:
            self.score_func = score_func
        elif score_weights:
            self.score_func = lambda gs, p: TreeAI.state_score_naive(gs, p, score_weights)
        else:
            self.score_func = lambda gs, p: TreeAI.state_score_naive(gs, p, self.DEFAULT_WEIGHTS)
        self.threaded_turn = ""
        self.thread_started = False
        self.kill = False
    
    @classmethod
    def state_score_naive(self, game_state, player, weights):
        """return naive score for game state based on # of walls and path lengths only.
        higher score corresponds to better position
        
        (diff in # of walls) * weights[0] + (diff in path lengths) * weights[1]
        """
        # walls score
        other_players = [p for p in game_state.players if p != player]
        my_walls = player.num_walls
        their_walls = max([p.num_walls for p in other_players])
        walls_diff = (my_walls - their_walls)
        # path length score
        my_path = len(game_state.get_shortest_path_player(player))
        their_path = min([len(game_state.get_shortest_path_player(p)) for p in other_players])
        paths_diff = their_path - my_path
        
        return weights[0]*walls_diff + weights[1]*paths_diff

    def get_move_thread_start(self, *args, **kargs):
        if not self.thread_started:
            self.thread_started = True
            th = Thread(target=lambda:self.get_move(*args, **kargs))
            th.start()
    
    def kill_thread(self):
        self.kill = True
    
    def get_threaded_move(self):
        if self.threaded_turn:
            turn = self.threaded_turn
            self.threaded_turn = ""
            self.thread_started = False
            return turn
        else:
            return None
      
    def get_move(self, game_state_copy):
        print "AI: GET_MOVE CALLED"
        #print "sleeping to let game state update.."
        #sleep(0.1)
        gs = game_state_copy
        if not gs.current_player.ai:
            print "WTF, mate? i'm not AI"
            self.threaded_turn = ""
            return ""
        #all_plies = gs.legal_moves + gs.legal_walls
        self.PLY_COUNT = 0
        tstart = time()
        """
        for i in range(len(all_plies)):
            if self.kill:
                return ""
            ply = all_plies[i]
            print "%-5s(%d of %d)" % (ply, i+1, len(all_plies))
            gs.execute_turn(ply)
            scores[i] = self.NegaMax(gs)
            print "     %f" % (scores[i])
            print "------------------"
            gs.undo()
        """
        #best_score, best_plies = self.NegaMax(gs, gs.current_player)
        best_score, best_plies = self.AlphaBeta(gs, gs.current_player, depth=3)
        if best_plies:
            # now sort by score
            chosen_ply = random.choice(best_plies)
            print "analyzed %d positions in %f seconds" % (self.PLY_COUNT, (time()-tstart))
            print "Chosen Move is %s with score %f" % (chosen_ply, best_score)
            if len(best_plies) > 1:
                print "All moves with same score are:"
                for ply in best_plies:
                    print "\t%s" % ply
            print "---------------------------------------------"
            self.threaded_turn = chosen_ply
            return chosen_ply
        else:
            return ""
    
    def NegaMax(self, game_state_copy, player, minmax=1, depth=2, timeout=None, start_time=None, print_space=" "):
        """Negamax implementation
        
        Note: only for 2-player
        """
        gs = game_state_copy
        if not start_time:
            start_time = time()
        if depth == 0:
            self.PLY_COUNT += 1
            return minmax * self.score_func(gs, player), []
        #all_plies = gs.legal_moves + gs.legal_walls
        all_plies = TreeAI.get_relevant_plies(gs, True)
        all_scores = [-TreeAI.INF] * len(all_plies)
        for i in range(len(all_plies)):
            if self.kill or (timeout and time()-start_time > timeout):
                return -TreeAI.INF, []
            ply = all_plies[i]
            gs.execute_turn(ply)
            print "(%-3d of %-3d)%s%s" % (i+1, len(all_plies), print_space, ply)
            ply_score, _ = self.NegaMax(gs, player, -minmax, depth-1, timeout, start_time, print_space+"   ")
            ply_score = -ply_score
            gs.undo()
            all_scores[i] = ply_score
        
        # all in list with max first
        score_ply = sorted(zip(all_scores, all_plies), reverse=True)
        (best_score, _) = score_ply[0]
        best_plies = [p for s, p in score_ply if s == best_score]
        
        # return best score and list of all plies with that score
        return (best_score, best_plies)
    
    def AlphaBeta(self, game_state_copy, player, alpha=-INF, beta=INF, minmax=1, depth=2, timeout=None, start_time=None, print_space=" "):
        """Alpha-Beta Pruning implementation (on NegaMax)
        
        Note: only for 2-player
        """
        gs = game_state_copy
        if not start_time:
            start_time = time()
        if depth == 0:
            self.PLY_COUNT += 1
            return minmax * self.score_func(gs, player), []
        #all_plies = gs.legal_moves + gs.legal_walls
        all_plies = TreeAI.get_relevant_plies(gs, True)
        all_scores = [-TreeAI.INF] * len(all_plies)
        for i in range(len(all_plies)):
            if self.kill or (timeout and time()-start_time > timeout):
                return -TreeAI.INF, []
            ply = all_plies[i]
            gs.execute_turn(ply)
            print "(%-3d of %-3d)%s%s" % (i+1, len(all_plies), print_space, ply)
            ply_score, _ = self.AlphaBeta(gs, player, -beta, -alpha, -minmax, depth-1, timeout, start_time, print_space+"   ")
            ply_score = -ply_score
            gs.undo()
            all_scores[i] = ply_score
            if ply_score > alpha:
                alpha = ply_score
            if alpha >= beta:
                break
        
        # all in list with max first
        score_ply = sorted(zip(all_scores, all_plies), reverse=True)
        (best_score, _) = score_ply[0]
        best_plies = [p for s, p in score_ply if s == best_score]
        
        # return best score and list of all plies with that score
        return (best_score, best_plies)
    
    @staticmethod
    def get_relevant_plies(game_state_copy, verbose=False):
        gs = game_state_copy
        relevant_walls = []
        # timing/stats
        tstart = time()
        num_plies = len(gs.legal_walls) + len(gs.legal_moves)
        # consider walls around the 2 players, plus or minus a row and column
        for p in gs.players:
            pr, pc = p.position
            for r in range(pr-2, pr+2):
                for c in range(pc-2, pc+2):
                    upleft = h.point_to_notation((r,c))
                    relevant_walls.extend(['H'+upleft, 'V'+upleft])

        """ OLD VERSION: all walls in bounding box of players, + 1 border
        cp = gs.current_player
        ops = gs.other_players
        cpr, cpc = cp.position
        for op in ops:
            opr, opc = op.position
            for r in range(min(cpr-2, opr-2), max(cpr+2, opr+2)):
                for c in range(min(cpc-2, opc-2), max(cpc+2, opc+2)):
                    upleft = h.point_to_notation((r,c))
                    relevant_walls.extend(['H'+upleft, 'V'+upleft])
        """
        # consider 'choke points' (i.e. narrow passages on the board)
        h_choke_points = TreeAI.get_h_chokepoints(gs, 4)
        v_choke_points = TreeAI.get_v_chokepoints(gs, 4)
        
        # now we have choke-points. consider walls in their range
        # TODO - if multiple similar in a row, use even # one
        #      - include walls with upleft 1 space further from border than start
        #   horizontal chokes
        for ((sr, sc), length) in h_choke_points:
            for c in range(sc, sc+length):
                upleft = h.point_to_notation((sr, c))
                relevant_walls.extend(['H'+upleft, 'V'+upleft])
        #   vertical chokes
        for ((sr, sc), length) in v_choke_points:
            for r in range(sr, sr+length):
                upleft = h.point_to_notation((r, sc))
                relevant_walls.extend(['H'+upleft, 'V'+upleft])
        
        # filter so only legal walls
        relevant_walls = [wall for wall in relevant_walls if wall in gs.legal_walls]
        
        # unique-ify them
        rw_dict = {}
        for w in relevant_walls:
            rw_dict[w] = 1
        relevant_walls = rw_dict.keys()
        
        relevant_plies = gs.legal_moves + relevant_walls
        
        # print stats
        new_num_plies = len(relevant_plies)
        if verbose:
            print "reduced %-3d plies to %-3d in %f seconds" % (num_plies, new_num_plies, time()-tstart)
        return relevant_plies
    
    # TODO:
    # - some actually are zero: a H wall means next H 'chunk' starts 2 away (inside the wall doesn't count as 1)
    
    @staticmethod
    def get_h_chokepoints(game_state_copy, max_choke_dist):
        # loop over all horizontal edges, count 'chunks' of consecutive open space
        h_chunks = []
        graph = game_state_copy.graph
        for r in range(1, 9):
            cur_count = 0 # num of spaces wide (for current 'chunk')
            cur_start = (r, 1)
            for c in range(1, 10):
                                                    # if edge DNE, it means:
                edges = [((r+1, c), (r+1, c+1), 1), # H gap meets top of vert wall
                         ((r, c),   (r, c+1),   1), # H gap meets bottom of vert wall
                         ((r, c),   (r+1, c),   1)] # H gap occupied by another H wall
                # check existence of edges
                e0 = graph.hasEdge(edges[0]) or c == 9
                e1 = graph.hasEdge(edges[1]) or c == 9
                e2 = graph.hasEdge(edges[2])
                # e2 is really the gap we're counting towards the chunk
                #   e0 and e1 are vertical walls that count as the border of a chunk
                #   SO! *count* whenever e2 is there, but chunk-end if any are missing
                if e2:
                    if cur_count == 0:
                        cur_start = (r, c)
                    cur_count += 1
                chunk_end = not (e0 and e1 and e2)
                board_end = (c == 9)
                if chunk_end or board_end:
                    if cur_count:
                        h_chunks.append((cur_start, cur_count))
                    cur_count = 0
        
        # choke points are chunks that are 4 or less across
        h_choke_points = [(point, length) for (point, length) in h_chunks if length <= max_choke_dist]
        #print "%d horizontal choke points:" % len(h_choke_points)
        #for (s, l) in h_choke_points:
        #    print s, l
        
        return h_choke_points

    @staticmethod
    def get_v_chokepoints(game_state_copy, max_choke_dist):# loop over all horizontal edges, count 'chunks' of consecutive open space
        v_chunks = []
        graph = game_state_copy.graph
        for c in range(1, 9):
            cur_count = 0 # num of spaces wide (for current 'chunk')
            cur_start = (1, c)
            for r in range(1, 10):
                                                    # if edge DNE, it means:
                edges = [((r, c+1), (r+1, c+1), 1), # V gap meets left of horz wall
                         ((r, c),   (r+1, c),   1), # V gap meets right of horz wall
                         ((r, c),   (r, c+1),   1)] # V gap occupied by another V wall
                # check existence of edges
                e0 = graph.hasEdge(edges[0]) or r == 9
                e1 = graph.hasEdge(edges[1]) or r == 9
                e2 = graph.hasEdge(edges[2])
                # e2 is really the gap we're counting towards the chunk
                #   e0 and e1 are horizontal walls that count as the border of a chunk
                #   SO! *count* whenever e2 is there, but new chunk if any are missing
                if e2:
                    if cur_count == 0:
                        cur_start = (r, c)
                    cur_count += 1
                chunk_end = not (e0 and e1 and e2)
                board_end = (r == 9)
                if chunk_end or board_end:
                    if cur_count:
                        v_chunks.append((cur_start, cur_count))
                    cur_count = 0
        
        # choke points are chunks that are 4 or less across
        v_choke_points = [(point, length) for (point, length) in v_chunks if length <= max_choke_dist]
        #print "%d vertical choke points:" % len(v_choke_points)
        #for (s, l) in v_choke_points:
        #    print s, l
        
        return v_choke_points