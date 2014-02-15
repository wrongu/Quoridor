from Quoridor import QGame, QPlayer
from sys import argv

def import_module(path):
	mod = __import__(path)
	components = path.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

modules = {
	Game : 
}

if __name__ == '__main__':
