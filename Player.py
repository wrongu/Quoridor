import Helpers as h

class Player:
    """Small Class for a Quoridor Player
    
    Player includes position = (row, column), goal squares, and number of walls. optional: name
    row and column are 1 through 9
    """
    def __init__(self, start_position, goals, num_walls = 10, name="", sortfunc=None, ai=None):
        self.position = start_position
        self.goal_positions = goals
        self.name = name
        self.num_walls = num_walls       
        self.sortfunc = sortfunc
        self.available_points = []
        self.movement_history = [start_position] # entire path taken throughout the game
        self.shortest_path = [] # keep track of shortest path at each turn
        self.ai = ai
    
    def duplicate(self, new=False):
        new_p = Player(self.position, h.list_copy(self.goal_positions),\
                        self.num_walls, self.name, self.sortfunc, self.ai)
        if not new:
            new_p.available_points = h.list_copy(self.available_points)
            new_p.movement_history = h.list_copy(self.movement_history)
            new_p.shortest_path = h.list_copy(self.shortest_path)
        return new_p
    
    def push_location(self, grid_pt):
        self.movement_history.append(self.position)
        self.position = grid_pt
    
    def pop_location(self):
        self.position = self.movement_history.pop()
    
    def set_name(self, new_name):
        self.name = new_name
    
    def get_num_walls(self):
        return self.num_walls
    
    def use_wall(self):
        self.num_walls -= 1
    
    def get_pos(self):
        return self.position
    
    def set_pos(self, new_pos):
        self.position = new_pos
        
    def get_goals(self):
        return self.goal_positions