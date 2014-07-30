# Board.py
#
# This file holds the Board class for the 9x9 board
#
# Author: wrongu

from collections import deque
from Cache import cache

class Node(object):
	""" A Node is a square on the SIZE x SIZE grid references to up to 4 adjacent walls.
	"""

	NORTH = 0 # row-
	SOUTH = 1 # row+
	EAST  = 2 # col+
	WEST  = 3 # col-

	__slots__ =  ('walls', 'position', '__neighbors', '__neighbors_cache')

	def __init__(self, pos):
		self.walls = 0 # least-significant 4 bits correspond to NSEW (i.e. byte 0000WESN)
		self.position = pos
		self.__neighbors = [None] * 4 # this is updated as walls are added or removed
		self.__neighbors_cache = [None] * 4 # this is blind to walls

	def __eq__(self, other):
		return isinstance(other, Node) and other.position == self.position

	def wall(self, direction):
		"""Record the wall in the given direction"""
		self.walls |= 1 << direction
		self.__neighbors[direction] = None

	def unwall(self, direction):
		"""remove the wall (if it exists) indicated by the given direction"""
		self.walls &= ~(1 << direction)
		self.__neighbors[direction] = self.__neighbors_cache[direction]

	def has_wall(self, direction):
		return self.walls & (1 << direction)

	def init_neighbors(self, N, S, E, W):
		self.__neighbors_cache = [N, S, E, W]
		self.__neighbors = [N, S, E, W]

	def neighbors(self):
		return self.__neighbors

	@classmethod
	def notate(cls, row_col):
		"""return the string notation of the given (row, column) tuple as described in Quoridor.py"""
		return "%c%d" % (chr(ord('a') + row_col[0]), row_col[1]+1)

	@classmethod
	def parse(cls, notate):
		"""the inverse of notate... takes a notation string ('a1' - 'i9') and returns the tuple (row, column) ((0,0) - (8,8))"""
		return (ord(notate[0]) - ord('a'), int(notate[1]) - 1)

	def __str__(self):
		return Node.notate(self.position)

class Wall(object):
	"""A Wall spans 2 grid spaces and can be either vertical or horizontal.
	"""

	VERTICAL = 'v'
	HORIZONTAL = 'h'

	__slots__ = ('orientation', 'position')

	def __init__(self, topleft, orient):
		self.orientation = orient
		self.position = topleft

	def __eq__(self, other):
		return isinstance(other, Wall) and other.position == self.position and other.orientation == self.orientation

	def blocks(self, posA, posB):
		(ra, ca) = posA
		(rb, cb) = posB
		
		if abs(ra-rb) + abs(ca-cb) != 1:
			# they aren't even adjacent
			return False
		elif (min(ra, rb), min(ca,cb)) != self.position:
			# posA and posB are somewhere else entirely
			return False
		elif abs(ra-rb) == 1:
			# diff is in rows.. blocks iff horizontal
			return self.orientation == Wall.HORIZONTAL
		elif abs(ca-cb) == 1:
			# diff is in cols.. blocks iff vertical
			return self.orientation == Wall.VERTICAL

	@classmethod
	def notate(cls, topleft, orient):
		"""return the string notation of this Wall as described in Quoridor.py"""
		return "%s%c" % (Node.notate(topleft), orient)

	@classmethod
	def parse(cls, notate):
		"""the inverse of notate... take a notation string and return a wall object"""
		orient = notate[2]
		pos = Node.parse(notate[0:2])
		return Wall(pos, orient)

	@classmethod
	def cross(cls, notate):
		"""return the wall that crosses the given wall (just flip h <--> v)"""
		return "%s%c" % (notate[0:2], Wall.HORIZONTAL if notate[2] is Wall.VERTICAL else Wall.VERTICAL)

	@classmethod
	def shift(cls, notate):
		"""return the notation for the walls offset from the given wall colinearly by one space"""
		w = Wall.parse(notate)
		(r,c) = w.position
		lst = []
		if notate[2] == Wall.HORIZONTAL:
			if c > 0:
				lst.append(Wall.notate((r,c-1), Wall.HORIZONTAL))
			if c+1 < Board.SIZE:
				lst.append(Wall.notate((r,c+1), Wall.HORIZONTAL))
		elif notate[2] == Wall.VERTICAL:
			if r > 0:
				lst.append(Wall.notate((r-1,c), Wall.VERTICAL))
			if r+1 < Board.SIZE:
				lst.append(Wall.notate((r+1,c), Wall.VERTICAL))
		return lst

	def __str__(self):
		return Wall.notate(self.position, self.orientation)

class Grid2D(object):
	"""A Grid2D is a wrapped 1D-array with the ability to index as 2D using tuples"""

	__slots__ = ('__grid')

	def __init__(self, rows, cols, val=None):
		self.__grid = [None for r in range(rows)]
		for r in range(rows):
			self.__grid[r] = [val for c in range(cols)]

	def __getitem__(self, idx):
		"""provides [(r,c)] notation for accessing the grid"""
		return self.__grid[idx[0]][idx[1]]

	def __setitem__(self, idx, val):
		"""provides [(r,c)] = val notation"""
		self.__grid[idx[0]][idx[1]] = val

class Board(object):

	SIZE = 9
	__slots__ = ('__grid', '__walls', '__hash')

	def __init__(self):
		self.__walls = []
		self.__grid = Grid2D(Board.SIZE,Board.SIZE)
		self.__hash = [0L, 0L] # 2 64-bit numbers with bits as wall flags. (H, V)
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				self.__grid[r,c] = Node((r,c))
		# initialize nodes' neighbors
		on_board = lambda (x,y): x >=0 and y >=0 and x < Board.SIZE and y < Board.SIZE
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				# note that NSEW order here does matter	
				adj = [(r-1,c),(r+1,c),(r,c+1),(r,c-1)]
				self.__grid[r,c].init_neighbors(*[self.__grid[n] if on_board(n) else None for n in adj])

	def hash(self):
		# convert mutable list into immutable tuple
		return tuple(self.__hash)

	def copy(self):
		BCopy = Board()
		# should be safe to add all the same objects since walls are never manipulated after creation
		# TODO - strict singleton?
		for w in self.__walls:
			BCopy.add_wall(w)
		return BCopy

	def summary(self):
		"""returns a Grid2D where grid[(r,c)] is a single number where the least 4 bits are WESN. that is, north wall is w&0x1"""
		ret = Grid2D(Board.SIZE, Board.SIZE)
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				ret[r,c] = self.__grid[r,c].walls
		return ret

	def add_wall(self, wall):
		"""add the given Wall object to the board, updating affected Nodes

		It is assumed this wall is valid by the rules of the game.. no checks are performed"""
		(wr, wc) = wall.position # topleft position (min row and min col)
		# flag nodes' walls
		if wall.orientation == Wall.VERTICAL:
			self.__grid[ wr ,  wc ].wall(Node.EAST)
			self.__grid[wr+1,  wc ].wall(Node.EAST)
			self.__grid[ wr , wc+1].wall(Node.WEST)
			self.__grid[wr+1, wc+1].wall(Node.WEST)
		elif wall.orientation == Wall.HORIZONTAL:
			self.__grid[ wr ,  wc ].wall(Node.SOUTH)
			self.__grid[ wr , wc+1].wall(Node.SOUTH)
			self.__grid[wr+1,  wc ].wall(Node.NORTH)
			self.__grid[wr+1, wc+1].wall(Node.NORTH)
		# add wall to list of wall objects
		self.__walls.append(wall)
		# update hash
		i = int(wall.orientation == Wall.VERTICAL)
		self.__hash[i] |= 1L << (wr*(Board.SIZE-1) + wc)

	def remove_wall(self, wall):
		"""remove the given Wall object from the board, updating affected Nodes

		It is assumed this wall already has been played.. no checks are performed"""
		(wr, wc) = wall.position # topleft position (min row and min col)
		if wall.orientation == Wall.VERTICAL:
			self.__grid[ wr ,  wc ].unwall(Node.EAST)
			self.__grid[wr+1,  wc ].unwall(Node.EAST)
			self.__grid[ wr , wc+1].unwall(Node.WEST)
			self.__grid[wr+1, wc+1].unwall(Node.WEST)
		elif wall.orientation == Wall.HORIZONTAL:
			self.__grid[ wr ,  wc ].unwall(Node.SOUTH)
			self.__grid[ wr , wc+1].unwall(Node.SOUTH)
			self.__grid[wr+1,  wc ].unwall(Node.NORTH)
			self.__grid[wr+1, wc+1].unwall(Node.NORTH)
		# remove wall from list of wall objects
		self.__walls.remove(wall)
		# update hash
		i = int(wall.orientation == Wall.VERTICAL)
		self.__hash[i] &= ~(1L << (wr*(Board.SIZE-1) + wc))

	@cache(lambda k,a: (k, a[0][0]))
	def __bfs_tree(self, goals):
		"""create a bfs tree on the whole board based on the iterable of goal tuples

		The result is cached"""
		q = deque(goals, Board.SIZE * Board.SIZE) # a queue of fringe positions
		steps = Grid2D(Board.SIZE, Board.SIZE) # grid[pos] contains the tuple (next_r, next_c) of the next path position from pos
		while len(q) > 0:
			fringe = q.pop()
			for n in self.neighbors(fringe):
				# step to neighbors if not yet visited
				if steps[n] is None:
					steps[n] = fringe
					q.append(n)
		for g in goals:
			steps[g] = None
		return steps

	def path(self, start, goals):
		"""given start position (row,col) and goals [(row,col),...], returns a list of shortest-path steps
		[start, x, y, ..., g] where g is in goals. If no path exists, returns []"""
		steps = self.__bfs_tree(goals)
		# iff path was found, steps[start] will have a value
		if steps[start] is None:
			return []
		else:
			# follow the trail left in 'steps' from start to goal
			path = [start]
			next = steps[path[-1]]
			while next is not None:
				path.append(next)
				next = steps[path[-1]]
			return path

	def can_step(self, posA, posB):
		"""Check whether or not (adjacent) positions posA and PosB are connected"""
		ra, ca = posA
		rb, cb = posB
		# first assert adjacency - row diff + col diff must be 1
		if abs(ra-rb) + abs(ca-cb) != 1:
			return False
		elif ra > rb:
			return not (self.__grid[(ra,ca)].has_wall(Node.NORTH))
		elif ra < rb:
			return not (self.__grid[(ra,ca)].has_wall(Node.SOUTH))
		elif ca > cb:
			return not (self.__grid[(ra,ca)].has_wall(Node.WEST))
		elif ca < cb:
			return not (self.__grid[(ra,ca)].has_wall(Node.EAST))

	def __compute_neighbors(self, pos):
		"""given a tuple position or Node, return the tuple positions next to and accessible by that position"""
		(r,c) = pos
		neighbors = [
			(Node.NORTH, (r-1, c) if r-1 >= 0 else None),
			(Node.SOUTH, (r+1, c) if r+1 < Board.SIZE else None),
			(Node.EAST , (r, c+1) if c+1 < Board.SIZE else None),
			(Node.WEST , (r, c-1) if c-1 >= 0 else None)
		]
		node = self.__grid[pos]
		return [npos for (direction, npos) in neighbors if npos and not node.has_wall(direction)]

	def neighbors(self, pos):
		for n in self.__grid[pos].neighbors():
			if n != None:
				yield n.position
