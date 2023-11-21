
import numpy as np
import torch



def data_board_to_one_hot_board(board_string):
    """Convert a board to a one-hot encoding."""
    tensor = np.zeros((3, 9, 9))     # index 0 for black, 1 for white and 2 for king

    x = 0
    y = -1
    for c in board_string:
        if c == '\n':
            y += 1
            x = 0
            continue

        if c == 'B':
            tensor[0, y, x] = 1
        elif c == 'W':
            tensor[1, y, x] = 1
        elif c == 'K':
            tensor[2, y, x] = 1

        x += 1
    
    return torch.from_numpy(tensor).float()

def data_action_to_action_dist(action):
    """Convert an action to a one-hot encoding."""

    pos_start = (ord(action[0][0].lower()) - ord('a'), int(action[0][1]) - 1)
    pos_end = (ord(action[1][0].lower()) - ord('a'), int(action[1][1]) - 1)

    tensor = np.zeros((9, 9, 32))  
            
    if pos_start[0] == pos_end[0]:
        i = pos_end[1] - pos_start[1]
        i -= 1 if i > 0 else 0
        i += 8

    elif pos_start[1] == pos_end[1]:
        i = pos_end[0] - pos_start[0]
        i -= 1 if i > 0 else 0
        i += 8 + 16
    
    else:
        raise ValueError
            
    # print(f"Action {action} i.e. pos {pos_start} to {pos_end} is encoded as {i}")
    tensor[pos_start[0], pos_start[1], i] = 1

    tensor = tensor.ravel()     # flatten tensor
    return tensor

def action_dist_to_action(action_dist):
    """Convert an action distribution to an action."""
    # TODO: double check! Copilot generated and see if it is really needed or not

    action_dist = action_dist.reshape((9, 9, 32))
    pos_start = np.unravel_index(action_dist.argmax(), action_dist.shape)
    pos_end = (pos_start[0] + 1, pos_start[1] + 1)

    if pos_start[2] < 16:
        pos_end = (pos_end[0], pos_end[1] + 1)
    else:
        pos_end = (pos_end[0] + 1, pos_end[1])

    return (pos_start, pos_end)