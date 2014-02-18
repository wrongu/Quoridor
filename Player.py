# Player.py
#
# The Player class represents a generic player (human, ai, networked, etc)

class Player(object):

	name = ''

	def __init__(self, name):
		self.name = name
		self.walls = 0

	def __str__(self):
		return str(name)

	def set_walls(self, w):
		self.walls = w

	def use_wall(self):
		self.walls -= 1
	