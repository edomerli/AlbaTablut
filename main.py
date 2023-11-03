import pygame

from Board import Board
from utils import *
from AI import *

pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

def draw(display):
	display.fill('white')
	board.draw(display)
	pygame.display.update()


if __name__ == '__main__':
	running = True
	ai_player = None

	if ai_player != None:
		ai = AI(AI_BUDGET)

	draw(screen)

	while running:
		if ai_player == board.turn:
			action, pred_win_rate = ai.MCTS(board)
			print(action, pred_win_rate)
			board.take_action(action)
		else:
			mx, my = pygame.mouse.get_pos()
			for event in pygame.event.get():
				# Quit the game if the user presses the close button
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.MOUSEBUTTONDOWN: 
					# If the mouse is clicked
					if event.button == 1:
						board.handle_click(mx, my)

		end, winner = board.check_end_game()
		if end:
			print(f"{'White' if winner == WHITE_PLAYER else 'Black'} wins!")
			running = False

		# TODO: handle draw by reaching same state twice
		# Draw the board
		draw(screen)