import numpy as np
import copy


# This class represents the individual square of a game board. Because this is a game of ultimate tic tac toe,
# the square can be a board itself.

class GameSquare:
    POSITION_LIST = ['UL', 'UM', 'UR',  # Possible options for position: U = Upper, M = middle, B = bottom,
                     'ML', 'MM', 'MR',  # L = left, R = right
                     'BL', 'BM', 'BR']
    OWNER_LIST = ['X', 'O']  # Potentially redundant list of possible owners

    def __init__(self, position, board=False):
        self.taken = False  # Has this space been taken?
        self.owner = None  # Who owns this space?
        self.board = board  # Is this space also a game board?
        try:
            if position in GameSquare.POSITION_LIST:
                self.position = position
        except NameError:
            print('Invalid position. Uses form UM for UpperMiddle. See README for more information.')
        if board:
            self.sub_game = GameBoard(meta_game=False)  # Defaults to false but for clarity I put it there


# This class represents the game board itself. It contains methods to check if game is completed and its initial setup.
# This class also contains general game info like player turn and current board stati.
class GameBoard:
    def __init__(self, meta_game=False):
        self.player_turn = True  # True for player turn, false for algorithm turn.
        self.meta_game = meta_game
        self.active_board = True  # At creation, all boards are active because they are legal moves (meta always active)
        self.completed = False
        self.winner = None  # probably redundant
        if meta_game:
            self.squares = {'UL': GameSquare('UL', board=True),  # possibly rename to UL_Board?
                            'UM': GameSquare('UM', board=True),
                            'UR': GameSquare('UR', board=True),
                            'ML': GameSquare('ML', board=True),
                            'MM': GameSquare('MM', board=True),
                            'MR': GameSquare('MR', board=True),
                            'BL': GameSquare('BL', board=True),
                            'BM': GameSquare('BM', board=True),
                            'BR': GameSquare('BR', board=True)}
        else:
            self.squares = {'UL': GameSquare('UL'),  # possibly redundant??
                            'UM': GameSquare('UM'),
                            'UR': GameSquare('UR'),
                            'ML': GameSquare('ML'),
                            'MM': GameSquare('MM'),
                            'MR': GameSquare('MR'),
                            'BL': GameSquare('BL'),
                            'BM': GameSquare('BM'),
                            'BR': GameSquare('BR')}

        self.WIN_CONS = [
            (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['UM'].owner) and (
                    self.squares['UM'].owner == self.squares['UR'].owner),  # Top Row
            (self.squares['ML'].owner is not None) and (self.squares['ML'].owner == self.squares['MM'].owner) and (
                    self.squares['MM'].owner == self.squares['MR'].owner),  # Middle Row
            (self.squares['BL'].owner is not None) and (self.squares['BL'].owner == self.squares['BM'].owner) and (
                    self.squares['BM'].owner == self.squares['BR'].owner),  # Bottom Row
            (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['ML'].owner) and (
                    self.squares['ML'].owner == self.squares['BL'].owner),  # Left Column
            (self.squares['UM'].owner is not None) and (self.squares['UM'].owner == self.squares['MM'].owner) and (
                    self.squares['MM'].owner == self.squares['BM'].owner),  # Middle Column
            (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MR'].owner) and (
                    self.squares['MR'].owner == self.squares['BR'].owner),  # Right Column
            (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['MM'].owner) and (
                    self.squares['MM'].owner == self.squares['BR'].owner),  # L-R Diagonal
            (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MM'].owner) and (
                    self.squares['MM'].owner == self.squares['BL'].owner)]  # R-L Diagonal

    def is_complete(self):
        for expr in self.WIN_CONS:  # Iterate over win/tie conditions to see if any are true, else return false
            if expr:
                return True
        for _, v in self.squares.items():  # Checks if there are still unclaimed spaces
            if v.taken is None:
                return False
        return False

    def move(self, target):  # kinda sketchy on this one ;(
        if self.player_turn:
            target.owner = 'X'
        else:
            target.owner = 'O'
        target.taken = True
        self.completed = self.is_complete()
        if self.completed and self.meta_game:
            self.game_end()  # TODO SEE BELOW
        else:
            self.player_turn = not self.player_turn
        return self

    def game_end(self):  # TODO add this
        if self.player_turn:
            self.winner = 'X'
        else:
            self.winner = 'O'
        #  print("Game Over, winner: {}".format(self.winner))


def get_legal_moves(state):  # See Node below for more info: checks what spaces are available
    """ Determines legal moves """
    legal_moves = []
    if not state.completed:
        if state.meta_game:
            for name, board in state.squares.items:  # maybe fix the tuple unpacking/.items stuff
                if not board.taken:
                    for _, space in board.sub_game.items():
                        if not space.taken:  # does this check for None?
                            legal_moves.append(space)
    else:
        if not state.completed:
            for square_name, space in state.squares.items:
                if not space.taken:
                    legal_moves.append(space)
    return legal_moves


class MCTSNode:
    def __init__(self, state, game, parent=None, parent_act=None):
        self.State = GameState(state, parent_act)  # Get the state of the board and the previous move
        self.game = game  # Reference to the game it is in (useful for checking game end trigger)
        self.parent = parent
        self.parent_action = parent_act
        self.children = []  # more nodes to be added: every possible move from any given place
        self.num_visits = 0
        self.results = {1: 0, 0: 0, -1: 0}  # 1 corresponds to win, 0 to tie, and -1 to loss
        self.untried_actions = get_legal_moves(self.State.board)

    def is_terminal_node(self):  # CHECK WHEN THIS TRIGGERS
        if self.game.completed:
            return True
        return False

    def expand(self):
        action = self.untried_actions.pop(np.random.randint(0, len(self.untried_actions)))  # randomized first pop
        next_state = copy.deepcopy(self.State)
        next_state.board.move(action)
        child_node = MCTSNode(state=next_state, game=self.game, parent=self, parent_act=action)
        self.children.append(child_node)
        return child_node

    def is_fully_expanded(self):  # IS this saying do every possible starting move?
        return len(self.untried_actions) == 0

    def rollout(
            self):  # From the current state, entire game is simulated till there is an outcome for the game. This outcome of the game is returned
        current_rollout_state = SimulationGame(self.State)
        while not current_rollout_state.board.is_complete():
            possible_moves = current_rollout_state.board.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.board.move(action)
        current_rollout_state.board.game_end()  # sets winner of the game based on whose turn it is when game ended
        return 1 if current_rollout_state.board.winner == 'O' else -1  # is returned to backpropogate

    def rollout_policy(self, possible_moves):  # Randomly selects a move out of possible moves.
        return possible_moves[np.random.randint(0, len(possible_moves))]

    def tree_policy(self):  # expands tree until
        if self.State.board.player_turn:
            current_node = self.expand()  # randomly expands once to randomly pick player move
        else:
            current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                _ = self.expand()
            else:
                return self.children[
                    np.random.randint(0, len(self.children))]  # randomly returns one of the children nodes
        return current_node

    # The best action function returns the node corresponding to the best possible move.
    def best_action(self, n_iter=100,  # starts from 0 (so 2 layers is 3 layers deep)
                    num_layers=2):
        simulation_n = n_iter
        best_child = None
        for _ in range(simulation_n):
            v = self.tree_policy()  # expansion
            reward = v.rollout()  # simulation
            v.backpropagate(reward)  # backpropagation
        best_child = self.best_child(c_param=0.1)
        return best_child.best_action(simulation_n, num_layers-1)  # recursively finds the best child for n_layers

    def backpropagate(self, result):
        self.num_visits += 1.
        self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self,
                   c_param=0.1):  # this is the function that determines the best child node. Note the tweak-able parameter
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def n(self):  # Returns the number of times each node is visited
        return self.num_visits

        # Returns the difference of wins and losses (NOTE THAT THERE IS NO WEIGHT TO DRAWS OTHER THAN INCREASING N)

    def q(self):
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses


class SimulationGame:
    def __init__(self, game_board):
        self.State = copy.deepcopy(game_board)


class GameState:
    def __init__(self, state, parent_action):
        self.board = state
        self.parent_action = parent_action


if __name__ == '__main__':
    print('test')
