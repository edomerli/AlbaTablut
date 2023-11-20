import pygame
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from typing import NamedTuple
import numpy as np
import pytorch_lightning as pl
import time


from Board import Board
from utils import *
from AI import *


class Transition(NamedTuple):   
    state: np.ndarray
    pi_prob: np.ndarray
    value: float

class TransitionsDataset(Dataset):
    def __init__(self, transitions) -> None:
        super().__init__()
        self.transitions = transitions

    def __len__(self):
        return len(self.transitions)
    
    def __getitem__(self, idx):
        return self.transitions[idx]

def draw(display, board):
    display.fill('white')
    board.draw(display)
    pygame.display.update()
    pygame.event.get()

if __name__ == '__main__':
    num_games = 10
    visualize = True
    if visualize:
        pygame.init()
        screen = pygame.display.set_mode(WINDOW_SIZE)

    ai_white = AI(AI_BUDGET, WHITE_PLAYER)
    ai_black = AI(AI_BUDGET, BLACK_PLAYER)

    WHITE_AI_PATH = Path('./ckpts/white_model.ckpt')
    BLACK_AI_PATH = Path('./ckpts/black_model.ckpt')

    if WHITE_AI_PATH.is_file():
        ai_white.alphazero = AlphaZeroNet.load_from_checkpoint(WHITE_AI_PATH)
        print("Loaded white model")
    if BLACK_AI_PATH.is_file():
        ai_black.alphazero = AlphaZeroNet.load_from_checkpoint(BLACK_AI_PATH)
        print("Loaded black model")

    ai_white.alphazero.eval()
    ai_black.alphazero.eval()

    for j in range(num_games):
        print(f"-------------Game {j}-------------")
        board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

        game_states = []
        game_pis = []
        game_values = []
        to_plays = []

        running = True

        if visualize:
            draw(screen, board)
        while running:
            start = time.process_time()
            
            if board.turn == WHITE_PLAYER:
                action, pred_win_rate, root_pi = ai_white.MCTS(board)
                print("White's turn played with pred win rate", pred_win_rate)

            else:
                action, pred_win_rate, root_pi = ai_black.MCTS(board)
                print("Black's turn played with pred win rate", pred_win_rate)
            
            print(f"Time taken for action: {time.process_time() - start}")

            game_states.append(board.to_onehot_tensor().squeeze())
            game_pis.append(torch.from_numpy(root_pi).float())
            game_values.append(0)
            to_plays.append(board.turn)

            board.take_action(action)

            # else:
            #     mx, my = pygame.mouse.get_pos()
            #     for event in pygame.event.get():
			# 		# Quit the game if the user presses the close button
            #         if event.type == pygame.QUIT:
            #             running = False
            #         elif event.type == pygame.MOUSEBUTTONDOWN: 
			# 			# If the mouse is clicked
            #             if event.button == 1:
            #                 board.handle_click(mx, my)

            if visualize:
                draw(screen, board) # Uncomment if want to see the game playing on

            end, winner = board.check_end_game()
            if end:
                running = False

                for i, play_id in enumerate(to_plays):
                    if play_id == winner:
                        game_values[i] = 1
                    else:
                        game_values[i] = -1
                game_values = np.array(game_values, dtype=np.float32)
            

        game_seq = [
            Transition(state=x, pi_prob=pi, value=v) for x, pi, v in zip(game_states, game_pis, game_values)
        ]

        print(f"Game {j} lasted {len(game_seq)} moves and {'White' if winner==WHITE_PLAYER else 'Black'} won!")
        
        white_transitions_data = game_seq[0::2]
        black_transitions_data = game_seq[1::2]


        dataset_white = TransitionsDataset(white_transitions_data)
        dataset_black = TransitionsDataset(black_transitions_data)

        train_dataloader_white = DataLoader(dataset_white, batch_size=len(white_transitions_data)//4, shuffle=True)
        train_dataloader_black = DataLoader(dataset_black, batch_size=len(black_transitions_data)//4, shuffle=True)

        ai_white.alphazero.train()
        ai_black.alphazero.train()

        trainer_white = pl.Trainer(max_epochs=10)
        trainer_black = pl.Trainer(max_epochs=10)
        print("Training WHITE...")
        trainer_white.fit(ai_white.alphazero, train_dataloader_white)
        trainer_white.save_checkpoint(WHITE_AI_PATH)
        print("Training BLACK...")
        trainer_black.fit(ai_black.alphazero, train_dataloader_black)
        trainer_black.save_checkpoint(BLACK_AI_PATH) 
    
    print(f"Terminated after {num_games} games")