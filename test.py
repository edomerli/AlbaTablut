import random

class X:
    def __init__(self, x):
        self.untried_actions = x

z = [[(4, 2), [(5, 2), (6, 2), (7, 2)]], [(4, 3), [(5, 3)]]]
node = X(z)
i = random.randint(0, len(node.untried_actions)-1)
j = random.randint(0, len(node.untried_actions[i][1])-1)
action = [node.untried_actions[i][0], node.untried_actions[i][1].pop(j)]

if len(node.untried_actions[i][1]) == 0:
    del node.untried_actions[i]

print(z)
print(node.untried_actions)