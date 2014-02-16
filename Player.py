# Player.py
#
# The Player class represents a generic player (human, ai, networked, etc)

class Player(object):

	name = ''

	def __init__(self, name):
		self.name = name

	def __str__(self):
		return str(name)

	