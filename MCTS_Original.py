import copy
import numpy as np
from collections import defaultdict

# The standard implementation of MCTS treats it as a class
class MctsNode():
    def __init__(self, state, parent=None, parent_act=None):
        # Note: an 'action' in this case is a move to be carried out in the game
        self.State = State(state, parent_act)  # represents the board state
        self.parent = parent  # None for the root node and for other nodes it is equal to the node it is derived from
        self.parent_act = parent_act  # None for the root node, otherwise equal to the action its parent carried out
        self.children = []  # All possibled actions from the current node
        self._num_visits = 0  # The number of times the current node is visited
        self._results = defaultdict(int)  # dictionary of results
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_acts = None  # The list of all possible actions
        self._untried_acts = self.set_untried_acts()
        return

    # Returns the list of untried actions from a given state.
    def set_untried_acts(self):
        self._untried_acts = self.get_legal_actions(self.State)
        return self._untried_acts

    # Returns the number of times each node is visited
    def n(self):
        return self._num_visits

    # Returns the difference of wins and losses
    def q(self):
        wins = self._results[1]
        losses = self._results[-1]
        return wins - losses

    # Check if the current node is terminal. A terminal node is reached when the game is over
    def is_terminal_node(self):
        return self.is_sim_over(self.State)

    def expand(self):
        action = self._untried_acts.pop(np.random.randint(0, len(self._untried_acts)))  # added randomized first pop
        self.move(self.State, action)
        next_state = copy.deepcopy(self.State)
        child_node = MctsNode(state=next_state, parent=self, parent_act=action)
        self.children.append(child_node)
        return child_node

    # All the actions are popped out of _untried_acts. When it becomes empty, it is fully expanded.
    def is_fully_expanded(self):
        return len(self._untried_acts) == 0

    def rollout(
            self):  # From the current state, entire game is simulated till there is an outcome for the game. This outcome of the game is returned
        current_rollout_state = self.State
        while not current_rollout_state.is_sim_over:
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = self.move(action, current_rollout_state)
        return current_rollout_state.game_result()

        # Randomly selects a move out of possible moves.

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(0, len(possible_moves))]

    # Selects node to run rollout
    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    # function for backpropagation
    def backpropagate(self, result):
        self._num_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    # All the statistics for the nodes are updated. Until the parent node is reached, the number of visits for each node is incremented by 1.

    def best_child(self, c_param=0.1): #this is the function that determines the best child node. Note the tweak-able parameter
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def best_action(self):  # The best action function returns the node corresponding to the best possible move.
        simulation_n = 100
        for i in range(simulation_n):
            v = self._tree_policy()  # expansion
            reward = v.rollout()  # simulation
            v.backpropagate(reward)  # backpropagation
        return self.best_child(c_param=0.1)

    def is_sim_over(self, State):  # the game over conditions
        for i in range(9):
            if isinstance(State.game_state[i][0], int):
                if State.game_state[i][0] == State.game_state[i][2] == State.game_state[i][3]:  # top row
                    State.game_state[i] = State.game_state[i][0]
                    return True
                elif State.game_state[i][0] == State.game_state[i][4] == State.game_state[i][8]:  # L to R diagonal
                    State.game_state[i] = State.game_state[i][0]
                    return True
                elif State.game_state[i][0] == State.game_state[i][3] == State.game_state[i][6]:  # left column
                    State.game_state[i] = State.game_state[i][0]
                    return True
            elif isinstance(State.game_state[i][3], int):
                if State.game_state[i][3] == State.game_state[i][4] == State.game_state[i][5]:  # middle row
                    State.game_state[i] = State.game_state[i][3]
                    return True
            elif isinstance(State.game_state[i][6], int):
                if State.game_state[i][6] == State.game_state[i][7] == State.game_state[i][8]:  # bottom row
                    State.game_state[i] = State.game_state[i][6]
                    return True
            elif isinstance(State.game_state[i][1], int):
                if State.game_state[i][1] == State.game_state[i][4] == State.game_state[i][7]:  # middle column
                    State.game_state[i] = State.game_state[i][1]
                    return True
            elif isinstance(State.game_state[i][2], int):
                if State.game_state[i][2] == State.game_state[i][5] == State.game_state[i][8]:  # right column
                    State.game_state[i] = State.game_state[i][2]
                    return True
                elif State.game_state[i][2] == State.game_state[i][4] == State.game_state[i][6]:  # R to L diagonal
                    State.game_state[i] = State.game_state[i][2]
                    return True
            elif isinstance(State.game_state[i][0], int):
                for n in State.game_state[i]:
                    if n is None:
                        return False  # still going
                State.game_state[i] = -1
                return True  # Tie

    def get_legal_actions(self, State):  # constructs a list of all possible actions from the current state
        legal_actions = []
        for i in range(9):
            if State.game_state[State.target][i] is None: #checks if target board has open squares
                legal_actions.append(i)
            return legal_actions
        if isinstance(State.game_state[State.target], int): #checks if targeted board is completed (and turned into a number to represent X or O)
            for i in range(9):
                if not isinstance(State.game_state[State.target], int): #if targeted board is not complete, adds it to list of legal board choices
                    legal_actions.append(State.game_state[i])

    def sim_result(self, x):  # returns 1 or 0 or -1 depending on the state, corresponding to win, tie, or loss
        if isinstance(self.State.game_state[x], int):
            return self.State.game_state[x]

    def move(self, State, action):  # Changes the state of your board with a new value.
        is_player_turn = False
        if is_player_turn:
            State.game_state[State.target][action] = 0
        else:
            State.game_state[State.target][action] = 1
        State.target = action
        is_player_turn = not is_player_turn


class State(): #state class that holds both state of entire game, and the board it will target next.
    def __init__(self, state, target):
        self.game_state = {}
        self.game_state = state
        self.target = target


def is_game_over(game):  # the game over conditions. These are the same as the above, but for the game, and not the simulation of the game
    for i in range(9):
        if isinstance(game[i][0], int):
            if game[i][0] == game[i][2] == game[i][3]:  # top row
                game[i] = game[i][0]
                return True
            elif game[i][0] == game[i][4] == game[i][8]:  # L to R diagonal
                game[i] = game[i][0]
                return True
            elif game[i][0] == game[i][3] == game[i][6]:  # left column
                game[i] = game[i][0]
                return True
        elif isinstance(game[i][3], int):
            if game[i][3] == game[i][4] == game[i][5]:  # middle row
                game[i] = game[i][3]
                return True
        elif isinstance(game[i][6], int):
            if game[i][6] == game[i][7] == game[i][8]:  # bottom row
                game[i] = game[i][6]
                return True
        elif isinstance(game[i][1], int):
            if game[i][1] == game[i][4] == game[i][7]:  # middle column
                game[i] = game[i][1]
                return True
        elif isinstance(game[i][2], int):
            if game[i][2] == game[i][5] == game[i][8]:  # right column
                game[i] = game[i][2]
                return True
            elif game[i][2] == game[i][4] == game[i][6]:  # R to L diagonal
                game[i] = game[i][2]
                return True
        elif isinstance(game[i][0], int):
            for n in game[i]:
                if n is None:
                    return False  # still going
            game[i] = -1
            return True  # Tie


def game_result(game, x):  # returns 1 or 0 or -1 depending on the state, corresponding to win, tie, or loss
    if isinstance(game[x], int):
        return game[x]


if __name__ == '__main__':
    game = { #create initial blank game
        0: [None, None, None, None, None, None, None, None, None],
        1: [None, None, None, None, None, None, None, None, None],
        2: [None, None, None, None, None, None, None, None, None],
        3: [None, None, None, None, None, None, None, None, None],
        4: [None, None, None, None, None, None, None, None, None],
        5: [None, None, None, None, None, None, None, None, None],
        6: [None, None, None, None, None, None, None, None, None],
        7: [None, None, None, None, None, None, None, None, None],
        8: [None, None, None, None, None, None, None, None, None],
    }
    first_input = int(input("Which board would you like to start one? 0-8: ")) #first moves to add before the game begins properly
    first_target = int(input("Which space would you like to choose? 0-8: "))
    game[first_input][first_target] = 0
    #small_game_results = [] TODO: implement this useful way to check game ending conditions
    initial_state = copy.deepcopy(game) # create some true copies of the game for use in simulation
    simul_state = copy.deepcopy(game)
    root = MctsNode(state=simul_state, parent_act=first_target) #creates first node
    while not is_game_over(game): # TODO: finish game loop. Currently there is no way to play the game.
        root.best_action()
