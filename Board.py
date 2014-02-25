# Board.py
#
# This file holds the Board class for the 9x9 board
#
# Author: wrongu
# Date: February 2014

class Node(object):
	""" A Node is a square on the SIZE x SIZE grid references to up to 4 adjacent walls.
	"""
	NORTH = 0 # row-
	EAST = 1  # col+
	SOUTH = 2 # row+
	WEST = 3  # col-

	def __init__(self, pos):
		self.walls = [None]*4 # NORTH, EAST, SOUTH, WEST
		self.position = pos

	def wall(self, w, direction):
		"""Add the given wall to this Node's list of adjacent walls"""
		self.walls[direction] = w

	def unwall(self, direction):
		"""remove the wall (if it exists) indicated by the given direction"""
		self.walls[direction] = None

	def has_wall(self, direction):
		return self.walls[direction] != None

	@classmethod
	def notate(cls, row_col):
		"""return the string notation of the given (row, column) tuple as described in Quoridor.py"""
		return "%d%c" % (row_col[0]+1, chr(ord('a') + row_col[1]))

	@classmethod
	def parse(cls, notate):
		"""the inverse of notate... takes a notation string ('1a' - '9i') and returns the tuple (row, column) ((0,0) - (8,8))"""
		return (int(notate[0] - 1), ord(notate[1]) - ord('a'))

	def __str__(self):
		return Node.notate(self.position)

class Wall(object):
	"""A Wall spans 2 grid spaces and can be either vertical or horizontal.
	"""

	VERTICAL = 'V'
	HORIZONTAL = 'H'

	def __init__(self, topleft, orient):
		self.orientation = orient
		self.position = topleft

	@classmethod
	def notate(cls, topleft, orient):
		"""return the string notation of this Wall as described in Quoridor.py"""
		return "%c%s" % (orient, Node.notate(topleft))

	@classmethod
	def parse(cls, notate):
		"""the inverse of notate... take a notation string and return a wall object"""
		orient = notate[0]
		pos = Node.parse(notate[1:])
		return Wall(pos, orient)

	@classmethod
	def cross(cls, notate):
		"""return the wall that crosses the given wall"""
		if notate[0] == Wall.HORIZONTAL:
			return Wall.VERTICAL + notate[1:]
		elif notate[0] == Wall.VERTICAL:
			return Wall.HORIZONTAL + notate[1:]

	def __str__(self):
		return Wall.notate(self.position, self.orientation)

class Board(object):

	SIZE = 9

	def __init__(self):
		self.grid = Board.__create_grid()
		self.walls = []

	def __neighbors(self, pos):
		neighbors = {
			Node.NORTH : (pos[0]-1, pos[1]) if pos[0]-1 >= 0 else None,
			Node.SOUTH : (pos[0]+1, pos[1]) if pos[0]+1 < Board.SIZE else None,
			Node.EAST  : (pos[0], pos[1]+1) if pos[1]+1 < Board.SIZE else None,
			Node.WEST  : (pos[0], pos[1]-1) if pos[1]-1 >= 0 else None
		}
		n = self.grid[pos[0]][pos[1]]
		retlist = []
		for direction, npos in neighbors.iteritems():
			if npos and not n.has_wall(direction):
				retlist.append(self.grid[npos[0]][npos[1]])
		return retlist

	def path(self, start, goals):
		from Queue import Queue
		q = Queue()
		for g in goals:
			q.put(g)


	def can_step(self, posA, posB):
		"""Check whether or not (adjacent) positions posA and PosB are connected"""
		ra, ca = posA
		rb, cb = posB
		# first assert adjacency - row diff + col diff must be 1
		if abs(ra-rb) + abs(ca-cb) != 1:
			return False
		elif ra > rb:
			return not (self.grid[ra][ca].has_wall(Node.NORTH))
		elif ra < rb:
			return not (self.grid[ra][ca].has_wall(Node.SOUTH))
		elif ca > cb:
			return not (self.grid[ra][ca].has_wall(Node.WEST))
		elif ca < cb:
			return not (self.grid[ra][ca].has_wall(Node.EAST))

	@classmethod
	def __create_grid(cls):
		"""
		The grid consists of a SIZE x SIZE array of nodes indexed by [row][column]. 
		"""
		# Create Nodes
		g = [None] * Board.SIZE
		for r in range(Board.SIZE):
			g[r] = [Node(r, c) for c in range(Board.SIZE)]
		return g

