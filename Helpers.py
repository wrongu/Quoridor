# Helper functions
# Includes functions for dealing with legal moves,
#   global stats,
#   converting to/from notation/geometry, and
#   making new players

import Game, SpecialGraphs
import string

global_stats = {}

def increment_int_stat(name, default=1):
    if name in global_stats:
        global_stats[name] += 1
    else:
        global_stats[name] = default

def append_stat(name, val):
    if name in global_stats:
        global_stats[name].append(val)
    else:
        global_stats[name] = [val]

########################
## Notation functions ##
########################

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

#####################
## Move Generation ##
#####################

def all_walls():
    return ['H1a', 'H1b', 'H1c', 'H1d', 'H1e', 'H1f', 'H1g', 'H1h',\
            'H2a', 'H2b', 'H2c', 'H2d', 'H2e', 'H2f', 'H2g', 'H2h',\
            'H3a', 'H3b', 'H3c', 'H3d', 'H3e', 'H3f', 'H3g', 'H3h',\
            'H4a', 'H4b', 'H4c', 'H4d', 'H4e', 'H4f', 'H4g', 'H4h',\
            'H5a', 'H5b', 'H5c', 'H5d', 'H5e', 'H5f', 'H5g', 'H5h',\
            'H6a', 'H6b', 'H6c', 'H6d', 'H6e', 'H6f', 'H6g', 'H6h',\
            'H7a', 'H7b', 'H7c', 'H7d', 'H7e', 'H7f', 'H7g', 'H7h',\
            'H8a', 'H8b', 'H8c', 'H8d', 'H8e', 'H8f', 'H8g', 'H8h',\
            'V1a', 'V1b', 'V1c', 'V1d', 'V1e', 'V1f', 'V1g', 'V1h',\
            'V2a', 'V2b', 'V2c', 'V2d', 'V2e', 'V2f', 'V2g', 'V2h',\
            'V3a', 'V3b', 'V3c', 'V3d', 'V3e', 'V3f', 'V3g', 'V3h',\
            'V4a', 'V4b', 'V4c', 'V4d', 'V4e', 'V4f', 'V4g', 'V4h',\
            'V5a', 'V5b', 'V5c', 'V5d', 'V5e', 'V5f', 'V5g', 'V5h',\
            'V6a', 'V6b', 'V6c', 'V6d', 'V6e', 'V6f', 'V6g', 'V6h',\
            'V7a', 'V7b', 'V7c', 'V7d', 'V7e', 'V7f', 'V7g', 'V7h',\
            'V8a', 'V8b', 'V8c', 'V8d', 'V8e', 'V8f', 'V8g', 'V8h'];

def get_all_legal_moves(game_state):
    """return all legal moves for the given player.
    
    built-in to player class =)
    """
    player_num = game_state.current_player_num
    player = game_state.get_player_by_num(player_num)
    if not player.available_points:
        game_state.update_available_points()
    player = game_state.get_player_by_num(player_num)

    return [point_to_notation(pt) for pt in player.available_points]

def get_all_legal_walls(game_state):
    return filter_legal_turns(game_state, all_walls());

def get_all_legal_turns(game_state):
    return get_all_legal_moves(game_state) + get_all_legal_walls(game_state)

def filter_legal_turns(game_state, turns):
    return filter(lambda t: game_state.turn_is_valid(t), turns);

########################
## Making new Players ##
########################

def make_2_players(name1="", name2=""):
    from Player import Player
    # definitions of start and goales for 2 players, all stated explicitly
    
    # player 1: 
    start1 = (1,5)
    goals1 = [(9,1), (9,2), (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), (9,9)]
    player1 = Player(start1, goals1, name=name1, sortfunc=SpecialGraphs.graph_net_sortfunc_row_inc)
    # player 2:
    start2 = (9,5)
    goals2 = [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9)]
    player2 = Player(start2, goals2, name=name2, sortfunc=SpecialGraphs.graph_net_sortfunc_row_dec)
    # return list of players, in order
    return [player1, player2]
    
def make_4_players(name1="", name2="", name3="", name4=""):
    from Player import Player
    # definitions of start and goales for 2 players, all stated explicitly
    
    # player 1: 
    start1 = (1,5)
    goals1 = [(9,1), (9,2), (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), (9,9)]
    player1 = Player(start1, goals1, name=name1, num_walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_row_inc)
    # player 2:
    start2 = (5,9)
    goals2 = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (8,1), (9,1)]
    player2 = Player(start2, goals2, name=name2, num_walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_col_dec)
    # player 3:
    start3 = (9,5)
    goals3 = [(1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9)]
    player3 = Player(start3, goals3, name=name3, num_walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_row_dec)
    # player 4:
    start4 = (5,1)
    goals4 = [(1,9), (2,9), (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9)]
    player4 = Player(start4, goals4, name=name4, num_walls=5, sortfunc=SpecialGraphs.graph_net_sortfunc_col_inc)
    # return list of players, in order
    return [player1, player2, player3, player4]
    
#####################
## Other Utilities ##
#####################

def list_copy(L):
    if type(L) is list:
        return [item for item in L]
    else:
        return L