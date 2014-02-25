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

class Grid2D(object):
	"""A Grid2D is a wrapped 2D-array with the ability to index using Nodes, tuples, or standard [r][c] notation,
	and it can be iterated linearly in the order of (0,0), (0,1), (0,2), ..., (1,0), (1,1)"""

	def __init__(self, rows, cols):
		self.__grid = [None for r in range(rows)]
		for r in range(rows):
			self.__grid[r] = [None for c in range(cols)]

	def __getitem__(self, idx):
		if(isinstance(idx, Node)):
			return self.__getitem__(idx.position)
		elif len(idx) == 1:
			return self.__grid[idx]
		elif len(idx) == 2:
			return self.__grid[idx[0]][idx[1]]

	def __setitem__(self, idx, val):
		if(isinstance(idx, Node)):
			self.__setitem__(idx.position, val)
		elif len(idx) == 1:
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

class Board(object):

	SIZE = 9

	def __init__(self):
		self.grid = Grid2D(Board.SIZE,Board.SIZE)
		self.walls = []
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				self.grid[r][c] = Node((r,c))

	def add_wall(self, wall):
		pass

	def remove_wall(self, wall):
		pass

	def path(self, start, goals):
		"""given start position (row,col) and goals [(row,col),...], returns a list of shortest-path steps
		[start, x, y, ..., g] where g is in goals. If no path exists, returns []"""
		from Queue import Queue
		q = Queue() # a queue of fringe positions
		steps = Grid2D(Board.SIZE, Board.SIZE) # grid[pos] contains the tuple (next_r, next_c) of the next path position from pos
		for g in goals:
			q.put(g)
		while not q.empty():
			fringe = q.get()
			# check if we made it
			if fringe == start:
				break
			for n in self.__neighbors(fringe):
				# step to neighbors if not yet visited
				if steps[n] is None:
					steps[n] = fringe
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
			return not (self.grid[ra][ca].has_wall(Node.NORTH))
		elif ra < rb:
			return not (self.grid[ra][ca].has_wall(Node.SOUTH))
		elif ca > cb:
			return not (self.grid[ra][ca].has_wall(Node.WEST))
		elif ca < cb:
			return not (self.grid[ra][ca].has_wall(Node.EAST))

	def __neighbors(self, pos):
		"""given a tuple position or Node, return the tuple positions next to and accessible by that position"""
		if isinstance(pos, Node):
			pos = pos.position
		neighbors = [
			(Node.NORTH, (pos[0]-1, pos[1]) if pos[0]-1 >= 0 else None),
			(Node.SOUTH, (pos[0]+1, pos[1]) if pos[0]+1 < Board.SIZE else None),
			(Node.EAST , (pos[0], pos[1]+1) if pos[1]+1 < Board.SIZE else None),
			(Node.WEST , (pos[0], pos[1]-1) if pos[1]-1 >= 0 else None)
		]
		retlist = []
		for direction, npos in neighbors:
			if npos and not self.grid[npos].has_wall(direction):
				retlist.append(npos)
		return retlist
