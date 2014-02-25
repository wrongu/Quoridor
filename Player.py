# Player.py
#
# The Player class represents a generic player (human, ai, networked, etc)

class Player(object):

	def __init__(self, name, start_position, goals):
		self.name = name
		self.position = start_position
		self.goals = goals

	def __str__(self):
		return str(name)

	def get_position(self):
		return self.position

	def update_position(self, newpos):
		self.position = newpos

	def reached_goal(self):
		return self.position in self.goals
