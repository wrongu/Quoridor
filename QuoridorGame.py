# This module provides python classes to represent the board game Quoridor.
# Modules for interaction, graphics, or AI done separately.
import SpecialGraphs;

class QuoridorPlayer:
    """Small Class for a Quoridor Player
    
    Player includes position = (row, column), goal squares, and number of walls.
    row and column are 1 through 9
    """
    def __init__(self, num, name=""):
        """num should be 1 or 2. defines which row is goal for each player"""
        start_row = 1 if num == 1 else 9;
        self.position = (start_row, 5);
        # goal is other side of the board (10-9 = 1; 10-1 = 9)
        goal_row = 10-start_row;
        self.goal_positions = [(goal_row, i) for i in range(1,10)]
        self.num_walls = 10;
        self.name = name;
    
    def set_name(self, new_name):
        self.name = new_name;
    
    def get_num_walls(self):
        return self.num_walls;

class QuoridorGame:
    """Abstract representation of a game of quoridor
    
    history: a list of turn strings
    walls: list of walls in official notation (list of strings)
    2 players
    graph of open paths (nodes are squares and edges are open paths)
    """
    def __init__(self, name1="", name2=""):
        self.history = [];
        self.current_player = QuoridorPlayer(1, name1);
        self.next_player = QuoridorPlayer(2, name2);
        self.graph = SpecialGraphs.GraphNet(9,9);
        self.walls = [];

    def next_turn(self):
        cur_p_temp = self.current_player;
        self.current_player = self.next_player;
        self.next_player = cur_p_temp;
    
    def execute_turn(self, turn_string):
        """Given turn (move or wall) in official string notation,
        
        update internal state if move is valid and swap players
        """
        # the following functions only apply if valid, so no need
        #   to check here. They return true if successful
        w_valid = self.turn_is_valid(turn_string, type="wall");
        m_valid = self.turn_is_valid(turn_string, type="move");
        #print "\twall valid?", w_valid,"\n\tmove valid?", m_valid
        if w_valid:
            #print "\twalled successfully"
            self.add_wall(turn_string);
        elif m_valid:
            #print "\tmoved successfully"
            self.do_move(turn_string);
        else:
            #print "execution failed"
            return False;
        self.next_turn();
        self.history.append(turn_string);
        return True;
            
    def add_wall(self, wall_string):
        # add wall; update
        self.walls.append(wall_string);
        row_up, col_left = notation_to_point(wall_string[1]+wall_string[3]);
        row_down, col_right = notation_to_point(wall_string[2]+wall_string[4]);
        # tuples of 4 adjacent squares
        up_left = (row_up, col_left);
        up_right = (row_up, col_right);
        down_left = (row_down, col_left);
        down_right = (row_down, col_right);
        if wall_string[0] is 'H':
            self.graph.removeEdge((up_left, down_left), directed=False);
            self.graph.removeEdge((up_right, down_right), directed=False);
        elif wall_string[0] is 'V':
            self.graph.removeEdge((up_left, up_right), directed=False);
            self.graph.removeEdge((down_left, down_right), directed=False);
            
    def remove_wall(self, wall_string):
        # same as add_wall function but adds in edges where adding walls
        #   removes edges
        self.walls.pop();
        row_up, col_left = notation_to_point(wall_string[1]+wall_string[3]);
        row_down, col_right = notation_to_point(wall_string[2]+wall_string[4]);
        # tuples of 4 adjacent squares
        up_left = (row_up, col_left);
        up_right = (row_up, col_right);
        down_left = (row_down, col_left);
        down_right = (row_down, col_right);
        if wall_string[0] is 'H':
            self.graph.addEdge((up_left, down_left), directed=False);
            self.graph.addEdge((up_right, down_right), directed=False);
        elif wall_string[0] is 'V':
            self.graph.addEdge((up_left, up_right), directed=False);
            self.graph.addEdge((down_left, down_right), directed=False);
                
    def do_move(self, move_string):
        self.current_player.position = notation_to_point(move_string);

    def get_shortest_path(self, start, end):
        return self.graph.findPathBreadthFirst(start, end);

    def turn_is_valid(self, turn_string, type=""):
        # Wall: notated with H or V for horz/vert, then adjacent 2 rows and
        #   2 columns
        # Move: notated by row then column.
        # in both, Row is a number 1-9 and column is a letter a-i
        # length 5: wall
        try:
            if  (type is "wall" or type is "") and len(turn_string) == 5:
                #print "\tprocessing turn: wall"
                wall_type = turn_string[0];
                # parse RRcc as row and columns
                row_up, col_left = notation_to_point(turn_string[1]+turn_string[3]);
                row_down, col_right = notation_to_point(turn_string[2]+turn_string[4]);
                # not valid if not representing a 2x2 block
                if row_down-row_up is not 1 or col_right-col_left is not 1:
                    #print "wall coordinates not 2x2"
                    return False;
                # not valid if out of bounds
                if not 1 <= row_up < 9 or not 1 <= col_left < 9:
                    #print "wall out of bounds"
                    return False;
                # if perpendicular wall exists in same place, not valid
                perp_char = 'H' if wall_type is 'V' else 'V';
                if (perp_char + turn_string[1:] in self.walls):
                    #print "wall crosses another wall"
                    return False;
                # not valid if overlaps with any other walls of same orientation
                if wall_type is 'H':
                    left_cols = col_to_letter(col_left-1)+col_to_letter(col_right-1);
                    right_cols = col_to_letter(col_left+1)+col_to_letter(col_right+1);
                    left_wall = 'H'+turn_string[1:2]+left_cols;
                    right_wall = 'H'+turn_string[1:2]+right_cols;
                    if left_wall in self.walls or right_wall in self.walls:
                        #print "horizontal wall overlap"
                        return False;
                if wall_type is 'V':
                    up_rows = str(row_up+1)+str(row_down+1);
                    down_rows = str(row_up-1)+str(row_down-1);
                    up_wall = 'V'+up_rows+turn_string[3:];
                    down_wall = 'V'+down_rows+turn_string[3:];
                    if up_wall in self.walls or down_wall in self.walls:
                        #print "vertical wall overalap"
                        return False;
                # if wall cuts off all paths for either player, not valid
                # check by adding in wall, checking paths, then removing wall
                self.add_wall(turn_string);
                # Player 1
                start = self.current_player.position;
                goals = self.current_player.goal_positions;
                paths = [self.get_shortest_path(start, goal) for goal in goals];
                # if paths are all None - not valid
                if len(paths) - paths.count(None) == 0:
                    #print "wall cuts off path: current player"
                    return False;
                # Player 2
                start = self.next_player.position;
                goals = self.next_player.goal_positions;
                paths = [self.get_shortest_path(start, goal) for goal in goals];
                # if paths are all None - not valid
                if len(paths) - paths.count(None) == 0:
                    #print "wall cuts off path: next player"
                    return False;
                self.remove_wall(turn_string);
                # if passed all the tests, it's valid!
                return True;
                
            if (type is "move" or type is "") and len(turn_string) == 2:
                #print "\tprocessing turn: move"
                move = notation_to_point(turn_string);
                cur = self.current_player.position;
                other = self.next_player.position;
                avail_squares = self.graph.get_adj_nodes(cur);
                # if 2 players are adjacent with no wall between them (i.e. if path
                #   between them is length 1), 
                if len(self.get_shortest_path(cur, other)) == 1:
                    avail_squares.remove(other);
                    o_row, o_col = other;
                    c_row, c_col = cur;
                    # if no walls in the way, jump square is behind other player.
                    #   jump = other + (other-cur) = 2*other - cur
                    j_row = 2*o_row - c_row;
                    j_col = 2*o_col - c_col;
                    jump = (j_row, j_col);
                    # check if no wall here
                    if self.graph.hasEdge((other, jump)):
                        avail_squares.insert(jump);
                    # if wall, use spaces to side ('L' movement)
                    else:
                        # if horizontal from cur to other, use vertical
                        if o_row == c_row:
                            jumps = [(c_row+1, o_col), (c_row-1, o_col)];
                        # vice versa
                        if o_col == c_col:
                            jumps = [(o_row, c_col+1), (o_row, o_col-1)];
                        avail_squares.extend(jumps);
                          
                is_valid = move in avail_squares;
                
                return is_valid
    
        except Exception as inst:
            #print "error processing turn {0}: {1}".format(turn_string, inst);
            return False;
        
        return False;
    
    def replay(self, history_list):
        for i in range (0, len(history_list)):
            # execute. if not successful, break.
            current_turn = history_list[i];
            #print "turn", i;
            if not self.execute_turn(current_turn):
                print "on turn", i, "invalid move:", current_turn;
                break;
            # TODO: draw and pause?
            # check win
            if self.current_player.position in self.current_player.goal_positions:
                print "Winner!", self.current_player.name;
        #print "Replay Done"
        

# Helper Functions
def point_to_notation(row, column):
    # both row and column are in [1,9]. rows denoted by this number,
    #   but columns denoted by letters 'a' through 'i'
    return "{0}{1}".format(row, col_to_letter(column));

def notation_to_point(point_str):
    # must be given as "5e", for example. row int and column letter
    row = int(point_str[0]);
    col = letter_to_col(point_str[1]);
    return (row, col);

def letter_to_col(letter):
    return ord(letter) - ord('a') + 1;

def col_to_letter(num):
    return chr(ord('a') + num - 1);