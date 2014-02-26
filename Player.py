# Player.py
#
# The Player class represents a generic player (human, ai, networked, etc)

from Quoridor import StateError

class Player(object):

	def __init__(self, name, start_position, goals, start_walls):
		self.__name = name
		self.__position = start_position
		self.__goals = goals
		self.__wall_count = start_walls

	def __str__(self):
		return str(self.__name)

	def get_position(self):
		return self.__position

	def update_position(self, newpos):
		self.__position = newpos

	def reached_goal(self):
		return self.__position in self.__goals

	def num_walls():
		return self.__wall_count

	def position():
		return self.__position

	def use_wall():
		if self.__wall_count > 0:
			self.__wall_count -= 1
		else:
			raise StateError("Player %s has no walls remaining" % self.__name)

	def unuse_wall():
		self.__wall_count += 1
