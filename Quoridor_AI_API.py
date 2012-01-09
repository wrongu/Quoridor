# Quoridor AI API
# provides functions that are useful for writing an AI

import QuoridorGame;

def get_all_legal_moves(game_state, player_cur_next=1):
    """return all legal moves for the given player.

    if player is 1, uses current player
    if player is 2, uses next player
    (not the greatest system, I know..."""
    player = game_state.current_player if player_cur_next == 1 else game_state.next_player;
    player_r, player_c = player.position;
    # depending on wall/other player situation, available moves could be any of the 8 adjacent spaces, plus the 4 that are 2 spaces away in NSEW
    adjacent_squares = [(r+player_r, c+player_c) for r in range(-1, 2) for c in range(-1,2)];
    # remove the center square (i.e. current position)
    del adjacent_squares[4];
    two_aways = [(player_r, player_c+2), (player_r, player_c-2), (player_r+2, player_c),  (player_r-2, player_c)];
    all_moves = adjacent_squares + two_aways;
    possible_moves_str = filter_legal_turns(game_state, [QuoridorGame.point_to_notation(r, c) for (r, c) in all_moves]);
    return possible_moves_str;

def get_all_legal_walls(game_state, player_cur_net=1):
    all_walls = ['H12ab', 'H12bc', 'H12cd', 'H12de', 'H12ef', 'H12fg', 'H12gh', 'H12hi', 'H23ab', 'H23bc', 'H23cd', 'H23de', 'H23ef', 'H23fg', 'H23gh', 'H23hi', 'H34ab', 'H34bc', 'H34cd', 'H34de', 'H34ef', 'H34fg', 'H34gh', 'H34hi', 'H45ab', 'H45bc', 'H45cd', 'H45de', 'H45ef', 'H45fg', 'H45gh', 'H45hi', 'H56ab', 'H56bc', 'H56cd', 'H56de', 'H56ef', 'H56fg', 'H56gh', 'H56hi', 'H67ab', 'H67bc', 'H67cd', 'H67de', 'H67ef', 'H67fg', 'H67gh', 'H67hi', 'H78ab', 'H78bc', 'H78cd', 'H78de', 'H78ef', 'H78fg', 'H78gh', 'H78hi', 'H89ab', 'H89bc', 'H89cd', 'H89de', 'H89ef', 'H89fg', 'H89gh', 'H89hi', 'V12ab', 'V12bc', 'V12cd', 'V12de', 'V12ef', 'V12fg', 'V12gh', 'V12hi', 'V23ab', 'V23bc', 'V23cd', 'V23de', 'V23ef', 'V23fg', 'V23gh', 'V23hi', 'V34ab', 'V34bc', 'V34cd', 'V34de', 'V34ef', 'V34fg', 'V34gh', 'V34hi', 'V45ab', 'V45bc', 'V45cd', 'V45de', 'V45ef', 'V45fg', 'V45gh', 'V45hi', 'V56ab', 'V56bc', 'V56cd', 'V56de', 'V56ef', 'V56fg', 'V56gh', 'V56hi', 'V67ab', 'V67bc', 'V67cd', 'V67de', 'V67ef', 'V67fg', 'V67gh', 'V67hi', 'V78ab', 'V78bc', 'V78cd', 'V78de', 'V78ef', 'V78fg', 'V78gh', 'V78hi', 'V89ab', 'V89bc', 'V89cd', 'V89de', 'V89ef', 'V89fg', 'V89gh', 'V89hi'];
    return filter_legal_turns(game_state, all_walls);
    
def filter_legal_turns(game_state, turns):
    return filter(lambda t: game_state.turn_is_valid(t), turns);

def state_score_naive(game_state, weight_to_paths = 0.5);
    """return naive score for game state based on # of walls and path lengths only.
    
    (diff in # of walls) * (1-weight) + (diff in path lengths) * weight
    
    computes for current_player
    """
    walls_diff = (game_state.current_player.num_walls - game_state.next_player.num_walls);
    paths_diff = len(other) - len(self)
    