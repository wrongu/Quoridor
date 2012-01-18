class QuoridorPlayer:
    """Small Class for a Quoridor Player
    
    Player includes position = (row, column), goal squares, and number of walls. optional: name
    row and column are 1 through 9
    """
    def __init__(self, start_position, goals, num_walls = 10, name="", sortfunc=None):
        self.position = start_position
        self.goal_positions = goals
        self.name = name
        self.num_walls = num_walls       
        self.sortfunc = sortfunc
        self.available_points = []
    
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
    
    def duplicate(self):
        return QuoridorPlayer(
            self.position,
            self.goals,
            self.num_walls,
            self.name
            )