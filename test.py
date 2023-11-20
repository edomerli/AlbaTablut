# # import random

# # class X:
# #     def __init__(self, x):
# #         self.untried_actions = x

# # z = [[(4, 2), [(5, 2), (6, 2), (7, 2)]], [(4, 3), [(5, 3)]]]
# # node = X(z)
# # i = random.randint(0, len(node.untried_actions)-1)
# # j = random.randint(0, len(node.untried_actions[i][1])-1)
# # action = [node.untried_actions[i][0], node.untried_actions[i][1].pop(j)]

# # if len(node.untried_actions[i][1]) == 0:
# #     del node.untried_actions[i]

# # print(z)
# # print(node.untried_actions)

# import numpy as np

# a = np.array([[[1, 2, 3],
#               [4, 5, 6]],
#               [[7, 8, 9],
#               [10, 11, 12]]])

# print(a.shape)
# from Board import *
# from utils import *

# board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

# actions = board.actions()
# c = 0
# for a in actions:
#     c += len(a[1])
# print(c)

# legal_actions = board.legal_actions_array()

# for z in actions:
#     print(z)
# for i in range(len(legal_actions)):
#     if legal_actions[i] == 1:
#         a = board.index_to_action(i)
#         print(a)

import numpy as np

a = [1, 2, 3, 4]
a = np.array(a, dtype=np.float32)
print(a)