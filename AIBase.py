import threading, time

class AIBase(object):
	
	def __init__(self):
		self.__daemon = None
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def running(self):
		return self.__daemon != None

	def process(self, state, callback=None, **kwargs):
		self.__daemon.daemon = True
		self.__daemon.start()