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
    all_topleft = [(r, c) for r in range(1,9) for c in range(1,9)];
    all_bottomright = [(r, c) for r in range(2,10) for c in range(2,10)];
    all_tl_str = [QuoridorGame.point_to_notation(r, c) for (r, c) in all_topleft];
    all_br_str = [QuoridorGame.point_to_notation(r, c) for (r, c) in all_bottomright];
    combined = zip(all_tl_str, all_br_str);
    all_2_by_2 = [tl[0]+br[0]+tl[1]+br[1] for (tl, br) in combined];
    all_H = ["H"+pos_str for pos_str in all_2_by_2];
    all_V = ["V"+pos_str for pos_str in all_2_by_2];
    return filter_legal_turns(game_state, all_H + all_V);
    
def filter_legal_turns(game_state, turns):
    return filter(lambda t: game_state.turn_is_valid(t), turns);

def state_score_naive(game_state):
    pass;