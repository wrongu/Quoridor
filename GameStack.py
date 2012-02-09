from Game import Game
import Helpers as h

class GameStack:
    
    """class that tracks history/redo-history of game states"""
    
    def __init__(self, *args, **kargs):
        """ init either with args to Game() or with game=game_state"""
        
        start = kargs.get("game", None)
        
        if not start:
            start = Game(*args, **kargs)
        
        self.history = []
        self.future = []
        self.current = start
        
    def duplicate(self):
        new_gs = GameStack(game=self.current)
        new_gs.history = h.list_copy(self.history)
        new_gs.future  = h.list_copy(self.future)
        return new_gs
    
    def execute_turn(self, *args, **kargs):
        dupl = self.current.duplicate()
        success = dupl.execute_turn(*args, **kargs)
        if success > 0:
            self.history.append(self.current)
            self.current = dupl
            
            # if not redo, clear future
            if not kargs.get('is_redo', False):
                self.future = []
        
        return success
        
    def undo(self):
        if len(self.history) > 0:
            self.future.append(self.current)
            self.current = self.history.pop()
    
    def redo(self):
        if len(self.future) > 0:
            self.history.append(self.current)
            self.current = self.future.pop()