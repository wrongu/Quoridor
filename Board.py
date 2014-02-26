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

	def __eq__(self, other):
		return isinstance(other, Node) and other.position == self.position

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

	def __str__(self):
		return Wall.notate(self.position, self.orientation)

class Grid2D(object):
	"""A Grid2D is a wrapped 2D-array with the ability to index using Nodes, tuples, or standard [r][c] notation,
	and it can be iterated linearly in the order of (0,0), (0,1), (0,2), ..., (1,0), (1,1)"""

	def __init__(self, rows, cols, val=None):
		self.__grid = [None for r in range(rows)]
		for r in range(rows):
			self.__grid[r] = [val for c in range(cols)]

	def __getitem__(self, idx):
		if(isinstance(idx, Node)):
			return self.__getitem__(idx.position)
		elif isinstance(idx, int):
			return self.__grid[idx]
		elif len(idx) == 2:
			return self.__grid[idx[0]][idx[1]]

	def __setitem__(self, idx, val):
		if(isinstance(idx, Node)):
			self.__setitem__(idx.position, val)
		elif isinstance(idx, int):
			self.__grid[idx] = val
		elif len(idx) == 2:
			self.__grid[idx[0]][idx[1]] = val

	def __iter__(self):
		class IterPosition(object):
			def __init__(it):
				it.cr = 0
				it.cc = 0
			def next(it):
				if it.cr < len(self.__grid):
					itm = self[it.cr][it.cc]
					it.cc += 1
					if it.cc >= len(self.__grid[0]):
						it.cr += 1
						it.cc = 0
					return itm
				else:
					raise StopIteration()
		return self

	def __len__(self):
		return len(self.__grid)

class Board(object):

	SIZE = 9

	def __init__(self):
		self.grid = Grid2D(Board.SIZE,Board.SIZE)
		self.walls = []
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				self.grid[r][c] = Node((r,c))

	def summary(self):
		"""returns a Grid2D where grid[r][c] is a single number where the least 4 bits are WESN. that is, north wall is w&0x1"""
		ret = Grid2D(Board.SIZE, Board.SIZE)
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				n = 0
				if self.grid[r][c].has_wall(Node.NORTH):
					n |= 0x1
				if self.grid[r][c].has_wall(Node.SOUTH):
					n |= 0x2
				if self.grid[r][c].has_wall(Node.EAST):
					n |= 0x4
				if self.grid[r][c].has_wall(Node.WEST):
					n |= 0x8
				ret[r][c] = n
		return ret

	def add_wall(self, wall):
		"""add the given Wall object to the board, updating affected Nodes

		It is assumed this wall is valid by the rules of the game.. no checks are performed"""
		(wr, wc) = wall.position # topleft position (min row and min col)
		if wall.orientation == Wall.VERTICAL:
			self.grid[ wr ][ wc ].wall(wall, Node.EAST)
			self.grid[wr+1][ wc ].wall(wall, Node.EAST)
			self.grid[ wr ][wc+1].wall(wall, Node.WEST)
			self.grid[wr+1][wc+1].wall(wall, Node.WEST)
		elif wall.orientation == Wall.HORIZONTAL:
			self.grid[ wr ][ wc ].wall(wall, Node.SOUTH)
			self.grid[ wr ][wc+1].wall(wall, Node.SOUTH)
			self.grid[wr+1][ wc ].wall(wall, Node.NORTH)
			self.grid[wr+1][wc+1].wall(wall, Node.NORTH)
		self.walls.append(wall)

	def remove_wall(self, wall):
		"""remove the given Wall object from the board, updating affected Nodes

		It is assumed this wall already has been played.. no checks are performed"""
		(wr, wc) = wall.position # topleft position (min row and min col)
		if wall.orientation == Wall.VERTICAL:
			self.grid[ wr ][ wc ].unwall(Node.EAST)
			self.grid[wr+1][ wc ].unwall(Node.EAST)
			self.grid[ wr ][wc+1].unwall(Node.WEST)
			self.grid[wr+1][wc+1].unwall(Node.WEST)
		elif wall.orientation == Wall.HORIZONTAL:
			self.grid[ wr ][ wc ].unwall(Node.SOUTH)
			self.grid[ wr ][wc+1].unwall(Node.SOUTH)
			self.grid[wr+1][ wc ].unwall(Node.NORTH)
			self.grid[wr+1][wc+1].unwall(Node.NORTH)
		self.walls.remove(wall)

	def path(self, start, goals):
		"""given start position (row,col) and goals [(row,col),...], returns a list of shortest-path steps
		[start, x, y, ..., g] where g is in goals. If no path exists, returns []"""
		from Queue import Queue
		q = Queue() # a queue of fringe positions
		steps = Grid2D(Board.SIZE, Board.SIZE) # grid[pos] contains the tuple (next_r, next_c) of the next path position from pos
		sentinel = (-1,-1)
		for g in goals:
			q.put(g)
			steps[g] = sentinel # mark end
		while not q.empty():
			fringe = q.get()
			# check if we made it
			if fringe == start:
				break
			for n in self.neighbors(fringe):
				# step to neighbors if not yet visited
				if steps[n] is None:
					steps[n] = fringe
					q.put(n)
		# iff path was found, steps[start] will have a value
		if steps[start] is None:
			return []
		else:
			# follow the trail left in 'steps' from start to goal
			path = [start]
			next = steps[path[-1]]
			while next is not sentinel:
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
			return not (self.grid[ra][ca].has_wall(Node.NORTH))
		elif ra < rb:
			return not (self.grid[ra][ca].has_wall(Node.SOUTH))
		elif ca > cb:
			return not (self.grid[ra][ca].has_wall(Node.WEST))
		elif ca < cb:
			return not (self.grid[ra][ca].has_wall(Node.EAST))

	@classmethod
	def __flip_direction(cls, direction):
		if direction == Node.NORTH:
			return Node.SOUTH
		elif direction == Node.SOUTH:
			return Node.NORTH
		elif direction == Node.EAST:
			return Node.WEST
		elif direction == Node.WEST:
			return Node.EAST

	def neighbors(self, pos):
		"""given a tuple position or Node, return the tuple positions next to and accessible by that position"""
		if isinstance(pos, Node):
			pos = pos.position
		(r,c) = pos
		neighbors = [
			(Node.NORTH, (r-1, c) if r-1 >= 0 else None),
			(Node.SOUTH, (r+1, c) if r+1 < Board.SIZE else None),
			(Node.EAST , (r, c+1) if c+1 < Board.SIZE else None),
			(Node.WEST , (r, c-1) if c-1 >= 0 else None)
		]
		retlist = []
		for direction, npos in neighbors:
			if npos and not self.grid[npos].has_wall(Board.__flip_direction(direction)):
				retlist.append(npos)
		return retlist
