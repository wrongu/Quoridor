# write history to file

import QuoridorGame

class QuoridorLog:
    
    @staticmethod
    def dump_game_state(game_state, filename=""):
        if not filename:
            filename = ".log_all.txt"
        with open(filename, "a+") as f:
            p_names = [p.name for p in game_state.players]
            f.append("\n"+repr(p_names)+"\n")
            f.append(repr(game_state.history)+"\n")
    
    def read_log(filename=""):
        if not filename:
            filename = ".log_all.txt"
        with open(filename, "r") as f:
            for l in f.read_lines():
                