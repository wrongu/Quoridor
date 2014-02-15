# Board.py
#
# This file holds the Board class for the 9x9 board
#
# Author: wrongu
# Date: February 2014

class Node(object):
	""" A Node is a square on the SIZE x SIZE grid references to neighbors.
		Neighbors will be removed as walls are placed.

		In terms of implementation, it is essentially a wrapper for a tuple (r, c)
		with neighbors, connect() and disconnect() functions
	"""

	def __init__(self, pos=None):
		self.neighbors = []
		self.position = pos

	def __eq__(self, other):
		return self.position == other.position

	def __str__(self):
		return str(self.position)

	def connect(self, other):
		self.neighbors.append(other)

	def disconnect(self, other):
		if other in self.neighbors:
			self.neighbors.remove(other)
		else:
			raise Exception("cannot remove %s from %s.. not connected" % (str(self), str(other)))

class Board(object):

	SIZE = 9

	def __init__(self):
		self.grid = Board.__create_grid()

	def __create_grid():
		"""
		The grid consists of a SIZE x SIZE array of nodes indexed by [row][column]. 
		Each node is connected to its immediate neighbors.
		"""
		# Create Nodes
		g = [None] * Board.SIZE
		for r in range(Board.SIZE):
			g[r] = [Node() for c in range(Board.SIZE)]
		# Connect node neighbors
		# could be faster, but it is only done at initialization and the board is small
		for r in range(Board.SIZE):
			for c in range(Board.SIZE):
				for offr, offc in [(-1,0), (1,0), (0,-1), (0,1)]:
					if r + offr in range(Board.SIZE) and c + offc in range(Board.SIZE):
						g[r][c].connect(g[r+offr][c+offc])

