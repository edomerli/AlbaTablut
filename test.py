from data_handler import *

game_sequence = file_to_game_sequence("data/_UniWarsLAs_vs_TheQuarant_1590701495535_gameLog.txt")

# state = torch.arange(8).view(2, 2, 2)
# print(state)
# print(torch.flip(state, [1]))   # flip vertically
# print(torch.flip(state, [2]))   # flip horizontally
# print(torch.flip(torch.rot90(state, 1, [1, 2]), [1]))
# print(torch.flip(torch.rot90(state, 1, [1, 2]), [2]))