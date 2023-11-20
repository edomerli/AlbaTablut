import pygame
from pathlib import Path

from Board import Board
from utils import *
from AI import *

# Comment next 2 lines and copy/uncomment them in utils.py to visualize simulation 
pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

def draw(display):
	display.fill('white')
	board.draw(display)
	pygame.display.update()


if __name__ == '__main__':
	running = True

	ai_color = BLACK_PLAYER
	
	# if ai_color is not None:
	# 	ai = AI(AI_BUDGET)

	draw(screen)

	while running:
		# if ai_color == board.turn:
		# 	action, pred_win_rate = ai.MCTS(board)
		# 	print(action, pred_win_rate)
		# 	board.take_action(action)
		# else:
		mx, my = pygame.mouse.get_pos()
		for event in pygame.event.get():
			# Quit the game if the user presses the close button
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN: 
				# If the mouse is clicked
				if event.button == 1:
					board.handle_click(mx, my)
		print("QUI")

		end, winner = board.check_end_game()
		if end:
			print(f"{'White' if winner == WHITE_PLAYER else 'Black'} wins!")
			running = False

		# TODO: handle draw by reaching same state twice
		# Draw the board
		draw(screen)