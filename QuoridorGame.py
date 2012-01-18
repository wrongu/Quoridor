# This module provides python classes to represent the board game Quoridor.
# Modules for player, graph, interaction, graphics, or AI done separately.

import SpecialGraphs
from QuoridorPlayer import QuoridorPlayer
import string

class QuoridorException(Exception):
    pass

class QuoridorGame:
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
            (5,5) --> 5e
            (9,9) --> 9i
        
        A *move* is denoted by the notated-form of the destination. Moving from 3b to 3c is just "3c"
        A *wall* is denoted with a 3-character string. The first character is "H" or "V" for Horizontal or Vertical walls
            -horizontal walls lie along a row and span 2 columns
            -vertical walls lie alonga column and span 2 rows

            the other 2 characters specify the point of the top-left corner of the wall (lowest row, lowest col)
            - must be between (1,1) and (8,8), or 1a and 8h
        
        visuals! (I suggest viewing with a fixed-width font)
        A  B        A || B
        ====          ||
        C  D        C || D
        
        for both of these, the point "A" will be used to denote the wall's location
        
    """
    def __init__(self, num_players = 2):
        self.history = []
        # players: 2 or 4
        if num_players == 2:
            self.players = make_2_players()
        elif num_players == 4:
            self.players = make_4_players()
        else:
            raise QuoridorException("invalid number of players: {0}".format(num_players))
        self.current_player_num = 1
        self.current_player = self.players[0]
        self.other_players = self.players[1:]
        # special graph for grid
        self.graph = SpecialGraphs.GraphNet(9,9)
        # initially no walls
        self.walls = []

    def next_player(self):
        """update 'current_player' variables
        
        includes both num and reference to current player object
        """
        self.current_player_num %= len(self.players)
        self.current_player_num += 1
        self.current_player = self.get_player_by_num(self.current_player_num)
        self.other_players = [p for p in self.players]
        self.other_players.remove(self.current_player)
    
    def get_player_by_num(self, num):
        return self.players[num-1]
        
    def execute_turn(self, turn_string):
        """Given turn (move or wall) in official string notation,
        
        update internal state if move is valid and swap players
        
        return True if player won
        else swap players and return false
        
        usage:
            while (not execute_turn):
                pass
            print "winner:", current_player.name
        """
        w_valid = self.turn_is_valid(turn_string, type="wall")
        m_valid = self.turn_is_valid(turn_string, type="move")
        #print "\twall valid?", w_valid,"\n\tmove valid?", m_valid
        if w_valid:
            #print "\twalled successfully"
            self.add_wall(turn_string)
        elif m_valid:
            #print "\tmoved successfully"
            self.do_move(turn_string)
        else:
            #print "execution failed"
            raise QuoridorException("invalid turn string given to execute_turn()")
        self.history.append(turn_string)
        # check win
        if self.current_player.position in self.current_player.goal_positions:
            return True
        else:
            self.next_player()
            return False
            
    def add_wall(self, wall_string):
        """update game internals with given wall
        
        must run is_valid check first - no checks preformed here
        """
        self.walls.append(wall_string)
        edge1, edge2 = wall_string_to_edges(wall_string)
        self.graph.removeEdge(edge1, directed=False)
        self.graph.removeEdge(edge2, directed=False)
        
    def remove_wall(self, wall_string):
        # same as add_wall function but adds in edges where adding walls
        #   removes edges
        self.walls.pop()
        edge1, edge2 = wall_string_to_edges(wall_string)
        self.graph.addEdge(edge1, directed=False)
        self.graph.addEdge(edge2, directed=False)
                
    def do_move(self, move_string):
        self.current_player.set_pos(notation_to_point(move_string))

    def get_shortest_path(self, start, end):
        return self.graph.findPathBreadthFirst(start, end)

    def path_exists(self, player_num):
        player = self.get_player_by_num(player_num)
        return self.graph.findPathDepthFirst(player.position, player.goal_positions, player.sortfunc) is not None

    def turn_is_valid(self, turn_string, type=""):
        if type and type == "move":
            return self.move_is_valid(turn_string)
        elif type and type == "wall":
            return self.wall_is_valid(turn_string)
        else:
            return ((self.move_is_valid(turn_string)) or (self.wall_is_valid(turn_string)))
            
    def move_is_valid(self, move_string):
        try:
            available_points = self.current_player.available_points
            if not available_points:
                self.update_available_points()
            return notation_to_point(move_string) in self.current_payer.available_points
        except:
            return False
        
    def update_available_points(self):
        for player in self.players:
            other_players = [p for p in self.players]
            cur_pt = player.position
            other_players.remove(player)
            other_pts = [p.position for p in other_players]
            avail_pts_temp = self.graph.get_adj_nodes(cur_pt)
            for s in avail_pts_temp:
                if s in other_pts:
                    avail_pts_temp.remove(s)
                    row_from, col_from = cur_pt
                    row_to, col_to = s
                    skip_pt = (2*row_to-row_from, 2*col_to-col_from)
                    if self.graph.hasEdge((s,skip_pt)) and skip_point not in other_pts:
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
            #print "\tprocessing turn: wall"
            wall_type = wall_string[0]
            
            edge1, edge2 = wall_string_to_edges(wall_string)
            (r1, c1), (r2, c2) = edge1, edge2
            topleft = (min(r1,r2), min(c1,c2))
            
            # not valid if not representing a 2x2 block
            perp_char = 'H' if wall_type is 'V' else 'V'
            if (perp_char + wall_string[1:] in self.walls):
                # print "wall crosses another wall"
                return False
                
            # checking if both edges are in graph (can be removed by placing wall)
            # this effectively checks 2 things:
            #   - wall within bounds of board
            #   - wall does not occupy same space as previous wall
            if not (self.graph.hasEdge(edge1) and self.graph.hasEdge(edge2)):
                # print "wall overlap or out of bounds"
                return False
            
            # if wall cuts off all paths for either player, not valid
            # check by adding in wall, checking paths, then removing wall
            self.add_wall(wall_string)
            paths = [self.path_exists(i) for i in range(len(self.players))]
            self.remove_wall(wall_string)
            
            if paths != [True]*len(self.players):
                return False
            # if passed all the tests, it's valid!
            return True
        except Exception, e:
            print "exceptional problems:", str(e)
            return False

    def replay(self, history_list):
        for i in range (0, len(history_list)):
            # execute. if not successful, break.
            current_turn = history_list[i]
            #print "turn", i
            if not self.execute_turn(current_turn):
                print "on turn", i, "invalid move:", current_turn
                break
            # TODO: draw and pause?
            # check win
            if self.current_player.position in self.current_player.goal_positions:
                print "Winner!", self.current_player.name
        #print "Replay Done"
        

# Helper Functions
def point_to_notation(pt):
    # both row and column are in [1,9]. rows denoted by this number,
    #   but columns denoted by letters 'a' through 'i'
    row, column = pt
    return "{0}{1}".format(row, col_to_letter(column))

def notation_to_point(point_str):
    # must be given as "5e", for example. row int and column letter
    row = int(point_str[0])
    col = letter_to_col(string.lower(point_str[1]))
    return (row, col)

def letter_to_col(letter):
    return ord(letter) - ord('a') + 1

def col_to_letter(num):
    return chr(ord('a') + num - 1)

def wall_string_to_4_points(wall_string):
    """get 4 points as tuples
    
    clockwise starting from 'topleft'
    """
    row_up, col_left = notation_to_point(wall_string[1:3])
    row_down, col_right = row_up+1, col_left+1
    # tuples of 4 adjacent squares
    up_left     = (row_up,   col_left)
    up_right    = (row_up,   col_right)
    down_left   = (row_down, col_left)
    down_right  = (row_down, col_right)
    return (up_left, up_right, down_left, down_right)

def wall_string_to_edges(wall_string):
    """get tuple of 2 edges
    
    each edge has (point1, point2)
    each point is (row, col)
    *matches format in SpecialGraphs.GraphNet
    """
    (up_left, up_right, down_left, down_right) = wall_string_to_4_points(wall_string)
    if wall_string[0] == "H":
        return ((up_left, down_left), (up_right, down_right))
    elif wall_string[0] == "V":
        return ((up_left, up_right), (down_left, down_right))
    else:
        return (None,None)

def make_2_players(name1="", name2=""):
    # definitions of start and goales for 2 players, all stated explicitly
    
    # player 1: 
    start1 = (1,5)
    goals1 = [(9,1), (9,2), (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), (9,9)]
    player1 = QuoridorPlayer(start1, goals1, name=name1, sortfunc=SpecialGraphs.graph_net_sortfunc_row_inc)
    # player 2:
    start2 = (9,5)
    goals2 = [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9)]
    player2 = QuoridorPlayer(start2, goals2, name=name2, sortfunc=SpecialGraphs.graph_net_sortfunc_row_dec)
    # return list of players, in order
    return [player1, player2]
    
def make_4_players(name1="", name2="", name3="", name4=""):
    # definitions of start and goales for 2 players, all stated explicitly
    
    # player 1: 
    start1 = (1,5)
    goals1 = [(9,1), (9,2), (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), (9,9)]
    player1 = QuoridorPlayer(start1, goals1, name=name1, walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_row_inc)
    # player 2:
    start2 = (5,9)
    goals2 = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (8,1), (9,1)]
    player2 = QuoridorPlayer(start2, goals2, name=name2, walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_col_dec)
    # player 3:
    start3 = (9,5)
    goals3 = [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9)]
    player3 = QuoridorPlayer(start3, goals3, name=name3, walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_row_dec)
    # player 4:
    start4 = (5,1)
    goals4 = [(1,9), (2,9), (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9)]
    player4 = QuoridorPlayer(start4, goals4, name=name4, walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_col_inc)
    # return list of players, in order
    return [player1, player2, player3, player4]
    
