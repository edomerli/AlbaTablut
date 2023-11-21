
import re
from train import Transition
from conversions import *

def file_to_game_sequence(filename):
    # Open the file in read mode
    with open(f"data/{filename}", "r") as file:
        # Read the contents of the file
        contents = file.read()

    # Split the contents into lines
    # lines = contents.split("\n")
    states = re.findall(r'FINE: Stato:(.*?)-', contents, flags=re.DOTALL)[:-2]
    actions = re.findall(r'FINE: Turn: .* Pawn from (.*) to (.*)', contents)
    winner = contents[-3:-1]

    states = [data_board_to_one_hot_board(state) for state in states]
    actions = [data_action_to_action_dist(action) for action in actions]
    values = [0] * len(states)
    if winner == 'WW':
        values[0::2] = [1] * len(states[0::2])
        values[1::2] = [-1] * len(states[1::2])
    elif winner == 'BW':
        values[1::2] = [1] * len(states[1::2])
        values[0::2] = [-1] * len(states[0::2])
    else:
        # print(winner)
        return []

    # game_values = np.array(game_values, dtype=np.float32)
    game_sequence = [Transition(state=s, pi_prob=pi, value=np.float32(v)) for s, pi, v in zip(states, actions, values)]

    return game_sequence

