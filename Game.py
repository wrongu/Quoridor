# This module provides python classes to represent the board game Quoridor.
# Modules for player, graph, interaction, graphics, or AI done separately.

import SpecialGraphs
from Graph import Graph
from Player import Player
import string
import Helpers as h
import random
from TreeAI import TreeAI
from pprint import pprint 
from Helpers import global_stats

class Exception(Exception):
    pass

class Game:
    """Abstract representation of a game of quoridor
    
    history: a list of turn strings
    walls: list of walls in official notation (list of strings)
    Players
        -name
        -number of walls
        -position
        -goal positions
        -sortfunc (orders points so direction of goal is first)
    graph of open paths (nodes are squares and edges are open paths)
    
    GRID LAYOUT:
        There are many places in this code where a 'point' is used to denote a position on the board. The format is (row, column)
        top/bottom refer to rows
        left/right refer to columns
        (1,1) is the top-left and (9,9) is the bottom-right

    NOTATION:
        While grid points are represented as a tuple of two numbers, the actual game notation uses letters for columns. 1-9 becomes a-i        
            (1,1) --> 1a
            (2,7) --> 2g
            (9,9) --> 9i
        
        A *move* is denoted by the notated-form of the destination. Moving from 3b to 3c is just "3c"
        A *wall* is denoted with a 3-character string. The first character is "H" or "V" for Horizontal or Vertical walls
            -horizontal walls lie between rows and span 2 columns
            -vertical walls lie between columns and span 2 rows

            the other 2 characters specify the point of the top-left corner of the wall (lowest row, lowest col)
            - must be between (1,1) and (8,8), or 1a and 8h
        
        visuals! (I suggest viewing with a fixed-width font)
        horizontal  vertical
        A  B        A || B
        ====          ||
        C  D        C || D
        
        for both of these, the point "A" will be used to denote the wall's location
        
    """
    
    def __init__(self, num_players=2, num_ai=0, duplicate=False):
        self.history             = []
        self.redo_history        = []
        self.players             = None
        self.starting_player_num = 1
        self.current_player_num  = 1
        self.current_player      = None
        self.other_players       = None
        # special graph for grid
        self.graph               = None
        # initially no walls
        self.walls               = []
        self.legal_moves         = []
        self.legal_walls         = []
        
        if not duplicate:
            # players: 2 or 4
            if num_players == 2:
                self.players = h.make_2_players()
            elif num_players == 4:
                self.players = h.make_4_players()
            else:
                raise Exception("invalid number of players: {0}".format(num_players))
            if num_ai > num_players:
                raise Exception("cannot have more ai than players")
            
            self.graph = SpecialGraphs.GraphNet(9,9)
            
            cpn = random.randint(1,num_players)
            #self.starting_player_num = cpn # never forget who started!
            self.current_player_num = cpn
            self.current_player = self.players[cpn-1]
            self.other_players = [p for p in self.players if p != self.current_player]
            all_inds = range(len(self.players))
            while num_ai > 0:
                ai_player = random.choice(all_inds)
                self.players[ai_player].ai = TreeAI()
                all_inds.remove(ai_player)
                num_ai -= 1
            self.update_legal_moves()
            self.update_legal_walls()
            for p in self.players:
                self.update_shortest_path(p)
    
    def duplicate(self):
        # make new game with same state as self
        #   this copy game should be passed to AI n' stuff so they can't actually do any damage
        new_gs = Game(len(self.players), duplicate=True)
        
        new_gs.history             = h.list_copy(self.history)
        new_gs.redo_history        = h.list_copy(self.redo_history)
        new_gs.players             = [p.duplicate() for p in self.players]
        #new_gs.starting_player_num = self.starting_player_num
        new_gs.current_player_num  = self.current_player_num
        new_gs.current_player      = new_gs.players[new_gs.current_player_num-1]
        new_gs.other_players       = [p for p in new_gs.players if p != new_gs.current_player]
        # special graph for grid
        new_gs.graph               = Graph(graph_in = self.graph)
        # initially no walls
        new_gs.walls               = h.list_copy(self.walls)
        new_gs.legal_moves         = h.list_copy(self.legal_moves)
        new_gs.legal_walls         = h.list_copy(self.legal_walls)
        
        return new_gs

    def next_player(self):
        """update 'current_player' variables
        
        includes both num and reference to current player object
        """
        self.current_player_num %= len(self.players)
        self.current_player_num += 1
        self.current_player = self.get_player_by_num(self.current_player_num)
        self.other_players = [p for p in self.players]
        self.other_players.remove(self.current_player)
        #print "current player:", self.current_player_num
        #print "current player position:", self.current_player.position
    
    def prev_player(self):
        self.current_player_num -= 1
        if self.current_player_num == 0:
            self.current_player_num = len(self.players)
        self.current_player = self.get_player_by_num(self.current_player_num)
        self.other_players = [p for p in self.players]
        self.other_players.remove(self.current_player)
        
    
    def get_player_by_num(self, num):
        return self.players[num-1]
        
    # TODO - if not a redo, clear redo hist
    def execute_turn(self, turn_string, is_redo=False, verify_legal=True):
        """Given turn (move or wall) in official string notation,
        
        update internal state if move is valid and swap players
        
        return 0 if failed
               1 if executed
               2 if executed and player just won!
        
        usage:
            while (not execute_turn):
                pass
            print "winner:", current_player.name
        """
        if verify_legal:
            w_valid = self.turn_is_valid(turn_string, type="wall")
            m_valid = self.turn_is_valid(turn_string, type="move")
            #print "\twall valid?", w_valid,"\n\tmove valid?", m_valid
            if w_valid:
                #print "\twalled successfully"
                self.add_wall(turn_string)
                self.current_player.use_wall()
            elif m_valid:
                #print "\tmoved successfully"
                self.do_move(turn_string)
            else:
                #print "execution failed"
                #raise Exception("invalid turn string given to execute_turn()")
                return 0
        else:
            # no verifications
            if len(turn_string) == 2:
                self.do_move(turn_string)
            elif len(turn_string) == 3:
                self.add_wall(turn_string)
        
        # check for win
        if self.current_player.position in self.current_player.goal_positions:
            return 2
        # no win - move on to next player
        else:
            if not is_redo:
                self.redo_history = []
            # time consuming to do all this updating and checking
            #   if not verify, don't update.
            if verify_legal:
                self.update_all([self.current_player])
            self.history.append(turn_string)
            self.next_player()
            return 1
    
    def undo(self):
        if len(self.history) > 0:
            self.prev_player()
            turn = self.history.pop()
            self.redo_history.append(turn)
            if len(turn) == 2:
                self.current_player.pop_location()
                self.update_shortest_path(self.current_player)
            elif len(turn) == 3:
                self.remove_wall(turn)
                self.current_player.num_walls += 1
            self.update_legal_moves()
            self.update_legal_walls()
    
    def redo(self):
        if len(self.redo_history) > 0:
            self.execute_turn(self.redo_history.pop(), True)
            
    def add_wall(self, wall_string, playernum=None):
        """update game internals with given wall
        
        must run is_valid check first - no checks preformed here
        """
        self.walls.append(wall_string)
        edge1, edge2 = h.wall_string_to_edges(wall_string)
        self.graph.removeEdge(edge1, directed=False)
        self.graph.removeEdge(edge2, directed=False)
        if playernum:
            p = self.get_player_by_num(playernum)
        
    def remove_wall(self, wall_string):
        # same as add_wall function but adds in edges where adding walls
        #   removes edges
        self.walls.pop()
        edge1, edge2 = h.wall_string_to_edges(wall_string)
        self.graph.addEdge(edge1, directed=False)
        self.graph.addEdge(edge2, directed=False)
                
    def do_move(self, move_string):
        self.current_player.push_location(h.notation_to_point(move_string))

    def get_shortest_path(self, start, end):
        return self.graph.findPathBreadthFirst(start, end)

    def get_shortest_path_player(self, player, force_bfs=False):
        p = player
        if force_bfs or not p.shortest_path:
            bfs_tree = self.graph.build_BFS_tree(p.position)
            paths = [self.graph.pathFromBFSTree(bfs_tree, p.position, g) for g in p.goal_positions]
            paths = filter(lambda p: p is not None, paths)
            paths = sorted(paths, cmp = lambda a, b: len(a)-len(b))
            return paths[0]
        else:
            return p.shortest_path

    def path_exists(self, player_num):
        player = self.get_player_by_num(player_num)
        return self.graph.findPathDepthFirst(player.position, player.goal_positions, player.sortfunc) is not None

    def update_all(self, player_list=None):
        for p in player_list:
            self.update_shortest_path(p)
        self.update_legal_moves()
        self.update_legal_walls()
    
    def update_legal_moves(self):
        self.update_available_points()
        legal_pts = self.current_player.available_points
        self.legal_moves = [h.point_to_notation(p) for p in legal_pts]
        #print "legal moves updated to:", self.legal_moves

    def update_legal_walls(self):
        all_w = h.all_walls()
        all_w = [w for w in all_w if w not in self.walls]
        all_w = filter(lambda w: self.wall_is_valid(w), all_w)
        self.legal_walls = all_w
        #print "legal walls updated to:", self.legal_walls
    
    def update_shortest_path(self, player):
        sp = player.shortest_path
        recalc_path = True
        if sp:
            if player.position == sp[1]:
                # player moved one step along shortest path.
                #   new shortest path is same as previous, starting 1 farther along
                player.shortest_path = sp[1:]
                recalc_path = False
            elif player.position == sp[0]:
                # p hasn't moved - check if sp is still clear
                for i in range(len(sp)-1):
                    e = (sp[i], sp[i+1], 1)
                    if not self.graph.hasEdge(e):
                        # path interrupted by new wall
                        break
                # path still clear, therefore still shortest. no change!
                recalc_path = False
        
        if recalc_path:
            player.shortest_path = self.get_shortest_path_player(player)
            h.increment_int_stat('sp-slow-updates')
        else:
            h.increment_int_stat('sp-fast-updates')

    def turn_is_valid(self, turn_string, type=""):
        if type and type == "move":
            return turn_string in self.legal_moves
        elif type and type == "wall":
            return turn_string in self.legal_walls
        else:
            return (turn_string in (self.legal_walls + self.legal_moves))
    
    def update_available_points(self):
        player = self.current_player
        other_players = self.other_players
        cur_pt = player.position
        other_pts = [p.position for p in other_players]
        avail_pts_temp = self.graph.get_adj_nodes(cur_pt)
        for s in avail_pts_temp:
            if s in other_pts:
                avail_pts_temp.remove(s)
                row_from, col_from = cur_pt
                row_to, col_to = s
                skip_pt = (2*row_to-row_from, 2*col_to-col_from)
                # can skip if path from other player to spot behind
                if self.graph.hasEdge((s,skip_pt)):
                    if skip_pt not in other_pts:
                        avail_pts_temp.append(skip_pt)
                else:
                    # create T points (diagonal movement)
                    T_point_1 = (row_to + (col_to-col_from), col_to+(row_to-row_from))
                    if self.graph.hasEdge((s, T_point_1)):
                        avail_pts_temp.append(T_point_1)
                    T_point_2 = (row_to + (col_from-col_to), col_to+(row_from-row_to))
                    if self.graph.hasEdge((s, T_point_2)):
                        avail_pts_temp.append(T_point_2)
        player.available_points = avail_pts_temp

    def wall_is_valid(self, wall_string):
        try:
            if len(wall_string) != 3:
                print "wall invalid:", wall_string
                return False
            
            if self.current_player.num_walls == 0:
                return False
            
            #print "\tprocessing turn: wall"
            wall_type = wall_string[0]
            
            edge1, edge2 = h.wall_string_to_edges(wall_string)
            (r1, c1), (r2, c2) = edge1, edge2
            topleft = (min(r1,r2), min(c1,c2))
            
            # not valid if not representing a 2x2 block
            perp_char = 'H' if wall_type is 'V' else 'V'
            if (perp_char + wall_string[1:] in self.walls):
                # print "wall crosses another wall:", wall_string
                return False
                
            # checking if both edges are in graph (are there to be removed with wall)
            # this effectively checks 2 things:
            #   - wall within bounds of board
            #   - wall does not occupy same space as previous wall
            if not (self.graph.hasEdge(edge1) and self.graph.hasEdge(edge2)):
                # print "wall overlap or out of bounds:", wall_string
                return False
            
            # if wall cuts off all paths for either player, not valid
            # check by adding in wall, checking paths, then removing wall
            self.add_wall(wall_string)
            paths = [self.path_exists(i) for i in range(len(self.players))]
            self.remove_wall(wall_string)
            
            if paths != [True]*len(self.players):
                # print "wall cuts off path:", wall_string
                return False
            # if passed all the tests, it's valid!
            return True
        except Exception, e:
            print "exceptional problems (wall is valid):", str(e)
            return False

    def replay(self, history_list, verify=True):
        for turn in history_list:
            success = self.execute_turn(turn, verify_legal=verify)
            if verify and not success:
                print "REPLAY FAIL: " + turn
                break
        self.update_all(self.players)