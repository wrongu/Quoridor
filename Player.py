# Player.py
#
# The Player class represents a generic player (human, ai, networked, etc)

from Exceptions import StateError

class Player(object):

	def __init__(self, name, start_position, goals, start_walls):
		self.__name = name
		self.__position = start_position
		self.__goals = goals
		self.__wall_count = start_walls

	def copy(self):
		PCopy = Player(self.__name, self.__position, self.__goals, self.__wall_count)
		return PCopy

	def __str__(self):
		return str(self.__name)

	def update_position(self, newpos):
		self.__position = newpos

	def reached_goal(self):
		return self.__position in self.__goals

	def num_walls(self):
		return self.__wall_count

	def position(self):
		return self.__position

	def goals(self):
		return self.__goals

	def use_wall(self):
		if self.__wall_count > 0:
			self.__wall_count -= 1
		else:
			raise StateError("Player %s has no walls remaining" % self.__name)

	def unuse_wall(self):
		self.__wall_count += 1
