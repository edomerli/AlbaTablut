* Data augmentation!
* Add logging to W&B to see training progress

* using the AIs to do the simulation part
* take only a subset of the actions (e.g. summing to 0.8) outputted by the model as the mcts untried actions, or only the actions whose probability is greater than a threshold
* ((Try adding the NN in the simulation as well to see if improves the quality of the simulation or its cost slows down))
* Data augmentation by exploiting the (8) simmetries of the game
* Add 8 step history of previously played moves in the game (how to deal with the first 8 moves of the game? I.e. don't have enought history)

* Implement multithreaded simulation as the guy does in https://github.com/nikcheerla/alphazero/blob/master/mcts.py in order to simulate many games at the same time starting from an expanded node -> get a better estimate of its score (i.e. mean of the winners I guess...)
* Try implementing RL with Fast and Forgetful Memory from paper https://arxiv.org/abs/2310.04128
* Ask Andreji from UCSD on Linkedin about its technique after sending him the code