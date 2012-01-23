from Tkinter import *
from math import floor
import QuoridorGame as QG
#from QuoridorGame import QuoridorGame

class TkBoard():
    # CONSTANTS
    SQUARE_SIZE = 50
    PLAYER_SIZE = SQUARE_SIZE * 0.8
    SQUARE_SPACING = 10
    MARGIN = 20
    PANEL_WIDTH = 200
    BUTTON_WIDTH = 140
    BUTTON_HEIGHT = 60
    BUTTON_MARGIN = 20
    DEFAULT_COLORS = {'bg': '#FFFFFF',
                      'square': '#333333',
                      'wall': '#CCCC11',
                      'wall-error': '#CC1111',
                      'panel': '#333333',
                      'button': '#880088',
                      'text': '#000000',
                      'players': ['#11CC11', '#CC11CC', '#BB0011', '#00CC00']
                      }
    # CLASS VARIABLES - DRAWING
    squares = [[0]*9]*9
    tk_root = None
    tk_canv = None
    players = []
    grid = None
    canvas_dims = (0,0)
    buttons = [] # will contain bbox and callback as tuple for each button
    
    # GAME-INTERACTION VARIABLES
    gs = None
    moveType = "wall"
    
    def set_default_colors(new_colors_dict={}):
        """update default colors with given dictionary of new color scheme
        
        Given colors don't need to be complete - only updates those given"""
        for k in new_colors_dict.keys():
            if k in self.DEFAULT_COLORS.keys():
                self.DEFAULT_COLORS[k] = new_colors_dict[k]
    
    def draw_new_board(self, game_state):
        """Destroy old board, draw new board, update object state with new board
        """
        if self.tk_root:
            self.tk_root.destroy()
            
        self.tk_root = Tk()
        self.tk_root.bind("<Escape>", lambda e: self.tk_root.destroy())
        self.tk_root.bind("<Motion>", lambda e: self.handle_mouse_motion(e))
        self.tk_root.bind("<Button-1>", lambda e: self.handle_click(e))
    
        # margin - space/2 - square - space - square - ... - square - space/2 - margin - panel
        total_height = 9*self.SQUARE_SIZE + 9*self.SQUARE_SPACING + 2*self.MARGIN
        total_width = total_height + self.PANEL_WIDTH
        self.canvas_dims = (total_width, total_height)
    
        self.tk_canv = Canvas(self.tk_root, width=total_width, height=total_height, background=self.DEFAULT_COLORS['bg'])
        self.tk_canv.pack()
        
        self.draw_squares()
        if game_state:
            self.gs = game_state
            self.players = [None]*len(game_state.players)
            self.draw_players(game_state)
        self.draw_panel()

        self.tk_root.mainloop()

    def new_rect_button(self, text, fill, x0, y0, x1, y1, callback):
        hover_lighten = TkBoard.alpha_hax(fill, "#FFFFFF", 0.1)
        self.tk_canv.create_rectangle(x0, y0, x1, y1, fill=fill, activefill=hover_lighten)
        midx = (x0 + x1) / 2
        midy = (y0 + y1) / 2
        self.tk_canv.create_text((midx, midy), text=text, font=("Arial", 14, "bold"))
        self.buttons.append(((x0, y0, x1, y1), callback))
    
    def set_movetype(self, type):
        self.moveType = type
    
    def draw_panel(self):
        w, h = self.canvas_dims
        c = self.DEFAULT_COLORS['panel']
        self.tk_canv.create_rectangle(w-self.PANEL_WIDTH, 0, w, h, fill=c)
        # buttons!
        c = self.DEFAULT_COLORS['button']
        midx = w-self.PANEL_WIDTH/2
        x0, x1 = midx-self.BUTTON_WIDTH/2, midx+self.BUTTON_WIDTH/2
        y0, y1 = self.BUTTON_MARGIN, self.BUTTON_MARGIN + self.BUTTON_HEIGHT
        self.new_rect_button("Move", c, x0, y0, x1, y1, lambda: self.set_movetype("move"))
        yshift = self.BUTTON_HEIGHT + self.BUTTON_MARGIN
        y0 += yshift
        y1 += yshift
        self.new_rect_button("Wall", c, x0, y0, x1, y1, lambda: self.set_movetype("wall"))

    def handle_mouse_motion(self, e):
        # TODO
        #   depending on current turn type and legal turns..
        x = e.x
        y = e.y
        grid = self.point_to_grid((x,y))
        if grid != self.grid:
            # print grid
            self.grid = grid
            if grid:
                self.draw_player(grid, 0)
    
    def handle_click(self, e):
        # TODO
        #   check buttons
        #   check board/turn
        pass
    
    def draw_squares(self):
        import random
        for r in range(9):
            for c in range(9):
                x = self.MARGIN + self.SQUARE_SPACING/2 + (self.SQUARE_SIZE+self.SQUARE_SPACING)*c
                y = self.MARGIN + self.SQUARE_SPACING/2 + (self.SQUARE_SIZE+self.SQUARE_SPACING)*r
                color = self.DEFAULT_COLORS['square']
                sq = self.tk_canv.create_rectangle(x, y, x+self.SQUARE_SIZE, y+self.SQUARE_SIZE, fill=color, outline="")
                self.squares[r][c] = sq
    
    def draw_players(self, game_state):
        # draw new ones
        for i in range(len(game_state.players)):
            p = game_state.players[i]
            self.draw_player(p.get_pos(), i)
    
    def draw_player(self, center, num, alpha=1):
        xy = self.grid_to_point(center)
        if not xy:
            return
        x, y = xy
        # remove old ovals from the board
        if self.players[num]:
            self.tk_canv.delete(self.players[num])
        # draw new
        c = self.DEFAULT_COLORS['players'][num]
        bg = self.DEFAULT_COLORS['square']
        c_blend = TkBoard.alpha_hax(bg, c, alpha)
        radius = self.PLAYER_SIZE/2
        self.players[num] = self.tk_canv.create_oval(x-radius, y-radius, x+radius, y+radius, fill=c_blend, outline="")

    def grid_to_point(self, grid_pt):
        """given (row, col), return centerpoint of that square on the canvas
        
        If not a valid grid point, return None"""
        r, c = grid_pt
        if (1 <= r <= 9) and (1 <= c <= 9):
            x = self.MARGIN + self.SQUARE_SPACING/2 + (self.SQUARE_SIZE+self.SQUARE_SPACING)*(c-1)
            y = self.MARGIN + self.SQUARE_SPACING/2 + (self.SQUARE_SIZE+self.SQUARE_SPACING)*(r-1)
            halfsquare = self.SQUARE_SIZE/2
            return (x+halfsquare, y+halfsquare)
        else:
            return None
        
    def point_to_grid(self, xy):
        """given (x, y), return (row, col) of corresponding grid space.
        
        If off the grid or one row of spacing on outside, returns None"""
        x, y = xy
        x -= self.MARGIN
        y -= self.MARGIN
        full_space = self.SQUARE_SIZE + self.SQUARE_SPACING
        r = int(floor(y / full_space) + 1)
        c = int(floor(x / full_space) + 1)
        if (1 <= r <= 9) and (1 <= c <= 9):
            return (r, c)
        else:
            return None
    
    @staticmethod
    def alpha_hax(back, front, alpha):
        """since tkinter doesnt support alpha channels as far as I can tell,
        this function does 2-color blending on hex strings, returning blended hex string"""
        
        # get numeric values
        b_r = int(back[1:3], 16)
        b_g = int(back[3:5], 16)
        b_b = int(back[5:7], 16)
        
        f_r = int(front[1:3], 16)
        f_g = int(front[3:5], 16)
        f_b = int(front[5:7], 16)
        
        # combine 'em
        new_r = int(b_r * (1-alpha) + f_r * alpha)
        new_g = int(b_g * (1-alpha) + f_g * alpha)
        new_b = int(b_b * (1-alpha) + f_b * alpha)
        
        # get hex versions, take off leading '0x' and pad with "0" when len() < 2
        hex_r = hex(new_r)[2:].rjust(2,"0")
        hex_g = hex(new_g)[2:].rjust(2,"0")
        hex_b = hex(new_b)[2:].rjust(2,"0")
        
        return "#"+hex_r+hex_g+hex_b

    def __init__(self, gs=None):
        self.draw_new_board(gs)

if __name__ == "__main__":
    gs = QG.QuoridorGame()
    tkb = TkBoard(gs)