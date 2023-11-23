from torch.utils.data import Dataset, DataLoader
import os
from pathlib import Path
import pytorch_lightning as pl
from pytorch_lightning.loggers import WandbLogger


from AlphaZeroNet import AlphaZeroNet
from data_handler import *
from utils import *

class TransitionsDataset(Dataset):
    def __init__(self, transitions) -> None:
        super().__init__()
        self.transitions = transitions

    def __len__(self):
        return len(self.transitions)
    
    def __getitem__(self, idx):
        return self.transitions[idx]
    

if __name__ == '__main__':
    NUM_EPOCHS = 100

    # Create the two sets of transitions from data and pass it to the dataset
    white_transitions = []
    black_transitions = []

    draws = 0
    invalids = 0
    for filename in os.listdir('data'):
        
        try:
            game_sequence = file_to_game_sequence(f"data/{filename}")
        except Exception as e:
            invalids += 1
            continue

        if game_sequence == []:
            draws += 1
            continue

        white_transitions.extend(game_sequence[::2])
        black_transitions.extend(game_sequence[1::2])

    print(f"White transitions collected {len(white_transitions)}")
    print(f"Black transitions collected {len(black_transitions)}")
    print("Draws:", draws)
    print("Invalids:", invalids)

    white_dataset = TransitionsDataset(white_transitions)
    black_dataset = TransitionsDataset(black_transitions)

    # train_white_dataset, val_white_dataset = torch.utils.data.random_split(white_dataset, [0.8, 0.2])
    # train_black_dataset, val_black_dataset = torch.utils.data.random_split(black_dataset, [0.8, 0.2])

    # Create the dataloaders
    train_white_dataloader = DataLoader(white_dataset, batch_size=64, shuffle=True, num_workers=4, persistent_workers=True)
    train_black_dataloader = DataLoader(black_dataset, batch_size=64, shuffle=True, num_workers=4, persistent_workers=True)

    # val_white_dataloader = DataLoader(val_white_dataset, batch_size=64, shuffle=False, num_workers=4, persistent_workers=True)
    # val_black_dataloader = DataLoader(val_black_dataset, batch_size=64, shuffle=False, num_workers=4, persistent_workers=True)

    # Train the networks
    WHITE_AI_PATH = Path('./ckpts/white_model.ckpt')
    BLACK_AI_PATH = Path('./ckpts/black_model.ckpt')

    # if WHITE_AI_PATH.is_file():
    #     ai_white.alphazero = AlphaZeroNet.load_from_checkpoint(WHITE_AI_PATH)
    #     print("Loaded white model")
    # if BLACK_AI_PATH.is_file():
    #     ai_black.alphazero = AlphaZeroNet.load_from_checkpoint(BLACK_AI_PATH)
    #     print("Loaded black model")

    white_alphazero = AlphaZeroNet((3, 9, 9), NUM_ACTIONS, num_res_block=9, num_filters=128, num_fc_units=128, learning_rate=1e-3).float()
    black_alphazero = AlphaZeroNet((3, 9, 9), NUM_ACTIONS, num_res_block=9, num_filters=128, num_fc_units=128, learning_rate=1e-3).float()
    
    white_alphazero.train()
    black_alphazero.train()

    white_wandb_logger = WandbLogger(log_model="all", project="TablutRL", name="white")
    black_wandb_logger = WandbLogger(log_model="all", project="TablutRL", name="black")

    trainer_white = pl.Trainer(max_epochs=NUM_EPOCHS, logger=white_wandb_logger)
    trainer_black = pl.Trainer(max_epochs=NUM_EPOCHS, logger=black_wandb_logger)
    print("Training WHITE...")
    trainer_white.fit(white_alphazero, train_white_dataloader)
    trainer_white.save_checkpoint(WHITE_AI_PATH)

    print("Training BLACK...")
    trainer_black.fit(black_alphazero, train_black_dataloader)
    trainer_black.save_checkpoint(BLACK_AI_PATH) 