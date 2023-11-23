
import re
from conversions import *
from typing import NamedTuple
import math

class Transition(NamedTuple):   
    state: np.ndarray
    pi_prob: np.ndarray
    value: float

def rotate(point, degrees):
    
    x = point[0] - 4
    y = point[1] - 4

    # Convert degrees to radians
    angle = math.radians(degrees)

    # Rotation matrix multiplication to get rotated x & y
    xr = (x * math.cos(angle)) - (y * math.sin(angle)) + 4
    yr = (x * math.sin(angle)) + (y * math.cos(angle)) + 4

    return (round(xr), round(yr))

def flip(point, axis):
    if axis == 0:
        return (point[0], 8 - point[1])
    elif axis == 1:
        return (8 - point[0], point[1])
    else:
        raise ValueError

def file_to_game_sequence(filename, data_augmentation=True):
    # Open the file in read mode
    with open(filename, "r") as file:
        # Read the contents of the file
        contents = file.read()

    # Split the contents into lines
    # lines = contents.split("\n")
    states = re.findall(r'FINE: Stato:(.*?)-', contents, flags=re.DOTALL)[:-2]
    actions = re.findall(r'FINE: Turn: .* Pawn from (..) to (..)', contents)
    winner = contents[-3:-1]
    if winner != 'WW' and winner != 'BW':
        return []
    
    
    if data_augmentation:
        states = [data_board_to_one_hot_board(state) for state in states]

        aug_states = []
        for state in states:
            
            aug_states.append(state)
            aug_states.append(torch.rot90(state, 1, [1, 2]))
            aug_states.append(torch.rot90(state, 2, [1, 2]))
            aug_states.append(torch.rot90(state, 3, [1, 2]))
            aug_states.append(torch.flip(state, [1]))   # flip vertically
            aug_states.append(torch.flip(state, [2]))   # flip horizontally
            aug_states.append(torch.flip(torch.rot90(state, 1, [1, 2]), [1]))
            aug_states.append(torch.flip(torch.rot90(state, 1, [1, 2]), [2]))

        states = aug_states

        aug_actions = []
        for literal_pos1, literal_pos2 in actions:

            pos1 = literal_to_pos_action(literal_pos1)
            pos2 = literal_to_pos_action(literal_pos2)

            aug_actions.append([pos1, pos2])
            aug_actions.append([rotate(pos1, -90), rotate(pos2, -90)])
            aug_actions.append([rotate(pos1, -180), rotate(pos2, -180)])
            aug_actions.append([rotate(pos1, -270), rotate(pos2, -270)])
            aug_actions.append([flip(pos1, 0), flip(pos2, 0)])
            aug_actions.append([flip(pos1, 1), flip(pos2, 1)])
            aug_actions.append([flip(rotate(pos1, -90), 0), flip(rotate(pos2, -90), 0)])
            aug_actions.append([flip(rotate(pos1, -90), 1), flip(rotate(pos2, -90), 1)])

        actions = aug_actions
        actions = [data_action_to_action_dist(action, literal_form=False) for action in actions]
    
    else:
        states = [data_board_to_one_hot_board(state) for state in states]
        actions = [data_action_to_action_dist(action) for action in actions]

    assert len(actions) == len(states)

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

