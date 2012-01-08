# Quoridor AI API
# provides functions that are useful for writing an AI

import QuoridorGame;

def get_all_legal_turns(game_state):
    all_turns = [];
    
    
def filter_legal_turns(game_state, turns):
    return filter(lambda t: game_state.turn_is_valid(t), turns);

def state_score_naive(game_state)