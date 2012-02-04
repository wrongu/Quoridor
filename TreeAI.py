
def state_score_naive(game_state, weight_to_paths = 0.5):
    """return naive score for game state based on # of walls and path lengths only.
    
    (diff in # of walls) * (1-weight) + (diff in path lengths) * weight
    
    computes for current_player
    """
    walls_diff = (game_state.current_player.num_walls - game_state.next_player.num_walls);
#    paths_diff = len(other) - len(self)
    