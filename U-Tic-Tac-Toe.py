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
            self.board_squares = {'UL': GameSquare('UL', board=True),  # possibly rename to UL_Board?
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

    def isComplete(self):
        for expr in self.WIN_CONS:  # Iterate over win conditions to see if any are true, else return false
            if expr:
                return True
        return False


def set_untried_actions(state):  # See Node below for more info: checks what spaces are available
    legal_moves = []
    if not state.completed:
        if state.meta_game:
            for board in state.board_squares:
                if not board.taken:
                    for space in board.sub_game:
                        if not space.taken:
                            legal_moves.append(space)
    else:
        if not state.completed:
            for space in state.squares:
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
        self.untried_actions = set_untried_actions(self.State)


    def is_terminal_node(self):   # VERY sketchy on when this will trigger: Ideally I want to check AFTER action/node creation
        if self.game.completed:
            return True
        return False

    def n(self):  # Returns the number of times each node is visited
        return self._num_visits

            # Returns the difference of wins and losses (NOTE THAT THERE IS NO WEIGHT TO DRAWS OTHER THAN INCREASING N)
    def q(self):
        wins = self._results[1]
        losses = self._results[-1]
        return wins - losses

class SimulationGame:
    def __init__(self, game_board):
        self.State = copy.deepcopy(game_board)  # MAYBE THIS IS INCORRECT???

class GameState:
    def __init__(self,state,parent_action):
        self.State = state
        self.parent_action = parent_action