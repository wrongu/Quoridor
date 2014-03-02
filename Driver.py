from Quoridor import Quoridor, State
from AlphaBetaAI import AlphaBetaAI2P as AI
from Exceptions import IllegalMove, StateError
from Board import Board, Grid2D, Node
from sys import argv
import math

def board_string(state_dict):
	players = state_dict['players']
	pkeys = players.keys()
	board = state_dict['board']

	print "Player positions", players

	# each cell is a 5x5 string which will be stiched together later
	st_cells = Grid2D(Board.SIZE+1, Board.SIZE+1)
	for r in range(Board.SIZE + 1):
		# special case first row and first column
		if r == 0:
			for c in range(Board.SIZE + 1):
				if c == 0:
					st_cells[(r,c)] = "".join([" "]*25)
				else:
					st_cells[(r,c)] = "            %d    |       " % c 
		else:
			for c in range(Board.SIZE + 1):
				if c == 0:
					st_cells[(r,c)] = "            %c-           " % chr(ord('a') + r - 1)
				else:
					st = ("     " #  0 - 4
						  " +-+ " #  5 - 9
						  " | | " # 10 - 14
						  " +-+ " # 15 - 19
						  "     ")# 20 - 24
					if players.has_key((r-1,c-1)):
						st = "%s%c%s" % (st[0:12], players[(r-1,c-1)][0][0], st[13:])
					# check 4 walls:
					if board[r-1,c-1] & 0x1:
						# north wall
						st = "#####" + st[5:]
					if board[r-1,c-1] & 0x2:
						# south wall
						st = st[0:20] + "#####"
					if board[r-1,c-1] & 0x4:
						# east wall
						st = "".join([st[(5*i):(5*i+4)]+"#" for i in range(5)])
					if board[r-1,c-1] & 0x8:
						# west wall
						st = "".join(["#"+st[(5*i+1):(5*i+5)] for i in range(5)])
					st_cells[(r,c)] = st

	st_final = ""
	for cr in range(5*(Board.SIZE+1)):
		ri = (cr / 5)
		sub_r = cr - 5*ri
		for cc in range(5*(Board.SIZE+1)):
			ci = (cc / 5)
			sub_c = cc - 5*ci
			st_final += st_cells[(ri,ci)][5*sub_r + sub_c]
		st_final += "\n"
	return st_final

if __name__ == '__main__':
	QGame = Quoridor(2)
	name1 = "RDL" #raw_input("Enter a name: ")
	name2 = "CCL" #raw_input("Enter another name: ")

	id1 = QGame.create_player(name1)
	id2 = QGame.create_player(name2)

	QGame.begin_game()

	cur_play = id1
	ai = None

	def redraw():
		print board_string(QGame.summary())
	QGame.register_callback(redraw)

	def print_prompt():
		print "moveable:", [Node.notate(pos) for pos in QGame.moveables()]
		prompt = "%s>" % (name1 if QGame.get_current_pid() == id1 else name2)
		print "\n%s" % prompt,

	def turn_update(pid, t):
		QGame.do_turn(pid, t)
		redraw()
		if not QGame.game_is_over():
			print_prompt()

	redraw()
	print_prompt()
	while QGame.state != State.OVER:
		try:
			move = raw_input()
			cur_play = QGame.get_current_pid()
			# special processing
			if move != '':
				if move[0:2] == 'ai':
					if ai and ai.is_processing():
						print "AI already in use..?"
					else:
						print "USING ALPHA-BETA AI"
						ai = AI(QGame, cur_play)
						depth = int(move[2:].strip())
						ai.process(depth, lambda t : turn_update(cur_play, t))
				elif move[0] == 'q':
					raise KeyboardInterrupt()
				else:
					# treat input as a normal move
					turn_update(cur_play, move)
		except IllegalMove as im:
			print "ILLEGAL MOVE", im
		except StateError as se:
			print "STATE ERROR", se
		except KeyboardInterrupt as ki:
			if ai.is_processing():
				ai.kill()
			else:
				i = raw_input("\nreally quit? (y/N)")
				if i != '':
					if i[0] == 'y' or i[0] == 'Y':
						break
					elif i == 'st':
						import traceback
						print traceback.format_exc()
	print "-- done --"
	if QGame.state() == State.OVER:
		redraw()
		print "Winner was", QGame.players[QGame.current_player]