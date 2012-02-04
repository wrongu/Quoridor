# Quoridor AI API
# provides functions that are useful for writing an AI

import QuoridorGame;

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

    return [QuoridorGame.point_to_notation(pt) for pt in player.available_points]

def get_all_legal_walls(game_state):
    return filter_legal_turns(game_state, all_walls());

def get_all_legal_turns(game_state):
    return get_all_legal_moves(game_state) + get_all_legal_walls(game_state)

def filter_legal_turns(game_state, turns):
    return filter(lambda t: game_state.turn_is_valid(t), turns);