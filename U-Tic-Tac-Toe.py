import numpy as np
import copy
import random

# This class represents the individual square of a game board. Because this is a game of ultimate tic tac toe,
# the square can be a board itself.

class GameSquare:
    POSITION_LIST = ['UL', 'UM', 'UR',  # Possible options for position: U = Upper, M = middle, B = bottom,
                     'ML', 'MM', 'MR',  # L = left, R = right
                     'BL', 'BM', 'BR']
    OWNER_LIST = ['X', 'O']  # Potentially redundant list of possible owners

    def __init__(self, position, game_board, is_board=False):
        self.taken = False  # Has this space been taken?
        self.owner = None  # Who owns this space?
        self.game_board = game_board  # In what board is this square?
        self.is_board = is_board  # Is this space also a game board?
        try:
            if position in GameSquare.POSITION_LIST:
                self.position = position
        except NameError:
            print('Invalid position. Uses form UM for UpperMiddle. See README for more information.')
        if is_board:
            self.sub_game = GameBoard(meta_game=False,
                                      parent_square=self)  # Defaults to false/None but for here clarity


# This class represents the game board itself. It contains methods to check if game is completed and its initial setup.
# This class also contains general game info like player turn and current board stati.
class GameBoard:
    def __init__(self, meta_game=False, parent_square=None):
        self.player_turn = True  # True for player turn, false for algorithm turn.
        self.meta_game = meta_game
        self.active_board = True  # At creation, all boards are active because they are legal moves (meta always active)
        self.completed = False
        self.winner = None  # probably redundant
        self.parent_square = parent_square
        if meta_game:
            self.squares = {'UL': GameSquare('UL', self, is_board=True),  # possibly rename to UL_Board?
                            'UM': GameSquare('UM', self, is_board=True),
                            'UR': GameSquare('UR', self, is_board=True),
                            'ML': GameSquare('ML', self, is_board=True),
                            'MM': GameSquare('MM', self, is_board=True),
                            'MR': GameSquare('MR', self, is_board=True),
                            'BL': GameSquare('BL', self, is_board=True),
                            'BM': GameSquare('BM', self, is_board=True),
                            'BR': GameSquare('BR', self, is_board=True)}
        else:
            self.squares = {'UL': GameSquare('UL', self),  # possibly redundant??
                            'UM': GameSquare('UM', self),
                            'UR': GameSquare('UR', self),
                            'ML': GameSquare('ML', self),
                            'MM': GameSquare('MM', self),
                            'MR': GameSquare('MR', self),
                            'BL': GameSquare('BL', self),
                            'BM': GameSquare('BM', self),
                            'BR': GameSquare('BR', self)}

    def is_complete(self):  # Iterate over win/tie conditions to see if any are true, else return false
        if (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['UM'].owner) and (
                self.squares['UM'].owner == self.squares['UR'].owner):  # Top Row
            self.winner = self.squares['UL'].owner
            return True
        elif (self.squares['ML'].owner is not None) and (self.squares['ML'].owner == self.squares['MM'].owner) and (
                self.squares['MM'].owner == self.squares['MR'].owner):  # Middle Row
            self.winner = self.squares['ML'].owner
            return True
        elif (self.squares['BL'].owner is not None) and (self.squares['BL'].owner == self.squares['BM'].owner) and (
                self.squares['BM'].owner == self.squares['BR'].owner):  # Bottom Row
            self.winner = self.squares['BL'].owner
            return True
        elif (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['ML'].owner) and (
                self.squares['ML'].owner == self.squares['BL'].owner):  # Left Column
            self.winner = self.squares['UL'].owner
            return True
        elif (self.squares['UM'].owner is not None) and (self.squares['UM'].owner == self.squares['MM'].owner) and (
                self.squares['MM'].owner == self.squares['BM'].owner):  # Middle Column
            self.winner = self.squares['UM'].owner
            return True
        elif (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MR'].owner) and (
                self.squares['MR'].owner == self.squares['BR'].owner):  # Right Column
            self.winner = self.squares['UR'].owner
            return True
        elif (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['MM'].owner) and (
                self.squares['MM'].owner == self.squares['BR'].owner):  # L-R Diagonal
            self.winner = self.squares['UL'].owner
            return True
        elif (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MM'].owner) and (
                self.squares['MM'].owner == self.squares['BL'].owner):  # R-L Diagonal
            self.winner = self.squares['UR'].owner
            return True
        else:
            for v in self.squares.values():  # Checks if there are still unclaimed spaces
                if (v.owner is None) or (v.taken is False):
                    return False
        return True  # no winner and all items are taken = draw

    def initial_move(self, meta_target, target):
        if self.meta_game:
            return self.squares[meta_target].sub_game.move(target)

    def move(self, target):
        target = target  # rename var
        key = None
        if isinstance(target, str):
            target = self.squares[target]
        legal_moves = get_legal_moves(self)
        if target in legal_moves:
            if self.player_turn:
                target.owner = 'X'
            else:
                target.owner = 'O'
            target.taken = True
            # if not self.meta_game: removed this because it should never be meta game I think :/
            key = target.position
            for name, square in self.parent_square.game_board.squares.items():
                if name == key:
                    square.sub_game.active_board = True
                else:
                    square.sub_game.active_board = False

            target.game_board.completed = target.game_board.is_complete()
            if target.game_board.completed:

                target.game_board.parent_square.taken = True
                target.game_board.parent_square.owner = target.game_board.winner
            self.parent_square.game_board.completed = self.parent_square.game_board.is_complete()
            #self.parent_square.game_board.winner = target.game_board.winner
            #if self.parent_square.game_board.completed:
                #self.game_end()
            self.player_turn = not self.player_turn
            #print(print_board(self.parent_square.game_board))  # for debugging
            return self
        else:
            print('Error: Invalid target')  # TODO ADD ERROR CHECKING
            return self  # not right for errors?

    def game_end(self):  # TODO add this
        print("Game Over, winner: {}".format(self.parent_square.game_board.winner))


def get_legal_moves(state):  # steps out into meta_game board then checks what spaces are available
    """ Determines legal moves """
    current_board = state
    legal_moves = []
    play_anywhere_flag = False
    if not current_board.meta_game:  # gets to meta-game board
        current_board = current_board.parent_square.game_board

    if not current_board.completed:  # game not over
        for board in current_board.squares.values():
            if board.sub_game.active_board and (not board.taken or not board.sub_game.completed):
                for square in board.sub_game.squares.values():
                    if not square.taken:
                        legal_moves.append(square)
            elif board.sub_game.active_board and (board.taken or board.sub_game.completed):
                play_anywhere_flag = True
                break
    if play_anywhere_flag:
        for  board in current_board.squares.values():  # becomes gameSquare class
            if (not board.taken) or board.sub_game.completed:
                for space in board.sub_game.squares.values():
                    if not space.taken:  # does this check for None?
                        legal_moves.append(space)

    return legal_moves


def print_board(board):
    """Prints visual representation of the Board"""
    base_string = ""
    counter1 = 0
    counter2 = 3
    inner_counter1 = 0
    inner_counter2 = 3
    POSITION_LIST = ['UL', 'UM', 'UR',  # Possible options for position: U = Upper, M = middle, B = bottom,
                     'ML', 'MM', 'MR',  # L = left, R = right
                     'BL', 'BM', 'BR']
    if board.meta_game:
        for i in range(3):
            for j in range(3):
                for name1 in POSITION_LIST[counter1: counter2]:
                    for name2 in POSITION_LIST[inner_counter1: inner_counter2]:
                        if board.squares[name1].sub_game.squares[name2].owner is not None:
                            base_string += " " + board.squares[name1].sub_game.squares[name2].owner + " "
                        else:
                            base_string += " - "
                    base_string += '|'
                base_string += '\n'
                inner_counter1 += 3
                inner_counter2 += 3
            inner_counter1 = 0
            inner_counter2 = 3
            base_string += ("_" * 30) + '\n'
            counter1 += 3
            counter2 += 3
    else:
        for square in board.squares.values():
            counter1 += 1
            if square.owner is not None:
                base_string += " " + square.owner + " "
            else:
                base_string += ' - '
            if counter1 == 3:
                counter1 = 0
                base_string += base_string + '\n'  # TODO ADD |
                base_string = ''
    return base_string

class MCTSNode:
    def __init__(self, state, game, parent=None, parent_action = None):
        self.State = copy.deepcopy(state)  # Get the state of the board and the previous move
        self.game = game  # Reference to the game it is in (useful for checking game end trigger)
        self.parent = parent
        self.parent_action = parent_action
        self.children = []  # more nodes to be added: every possible move from any given place
        self.num_visits = 0
        self.results = {1: 0, 0: 0, -1: 0}  # 1 corresponds to win, 0 to tie, and -1 to loss
        self.untried_actions = get_legal_moves(self.State)

    def is_terminal_node(self):  # TODO change to check when MAIN game ends?
        if self.game.completed:
            return True
        return False

    def expand(self):
        action = self.untried_actions.pop(np.random.randint(0, len(self.untried_actions)))  # randomized index for pop
        next_state = copy.deepcopy(self.State)  # copies state for child node
        next_state_actions = get_legal_moves(next_state)
        random.shuffle(next_state_actions)  # makes sure not in order in case of multiple matches for position
        for square in next_state_actions:
            if square.position == action.position:  # finds equivalent position in copy
                next_state = next_state.move(square)
                child_node = MCTSNode(state=next_state, game=self.game, parent=self,parent_action=square)
                break
        self.children.append(child_node)
        return child_node

    def is_fully_expanded(self):  # IS this saying do every possible starting move?
        return len(self.untried_actions) == 0

    def rollout(
            self):  # From the current state, entire game is simulated till there is an outcome for the game. This outcome of the game is returned
        current_rollout_state = copy.deepcopy(self.State)
        while not current_rollout_state.parent_square.game_board.is_complete():
            possible_moves = get_legal_moves(current_rollout_state)
            try:
                action = self.rollout_policy(possible_moves)
            except:
                return 0
            current_rollout_state = current_rollout_state.move(action)
        if current_rollout_state.parent_square.game_board.winner == 'O':   # is returned to backpropogate
            return 1
        elif current_rollout_state.parent_square.game_board.winner == 'X':
            return -1
        else:
            return 0

    def rollout_policy(self, possible_moves):  # Randomly selects a move out of possible moves.
        return possible_moves[np.random.randint(0, len(possible_moves))]

    def tree_policy(self):  # expands tree until full
        if self.State.player_turn:
            current_node = self.expand()  # randomly expands once to randomly pick player move
        else:
            current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                _ = current_node.expand()
            else:
                return current_node.children[
                    np.random.randint(0, len(current_node.children))]  # randomly returns one of the children nodes
        return current_node

    # The best action function returns the node corresponding to the best possible move.
    def best_action(self, n_iter=100,  # starts from 0 (so 2 layers is 3 layers deep)
                    ):
        simulation_n = n_iter
        best_child = None
        for i in range(simulation_n):
            v = self.tree_policy()  # expansion
            reward = v.rollout()  # simulation
            v.backpropagate(reward)  # backpropagation
            #print('Game: {}'.format(i))  # for debugging
        best_child = self.best_child(c_param=0.1)
        #if num_layers > 0:
         #   return best_child.best_action(simulation_n, num_layers - 1)  # recursively finds the best child for n_layers
        #else:
        #    return best_child
        return best_child
    def backpropagate(self, result):
        self.num_visits += 1.
        self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self,
                   c_param=0.1):  # this is the function that determines the best child node. Note the tweak-able parameter
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children if c.n() != 0]
        return self.children[np.argmax(choices_weights)]

    def n(self):  # Returns the number of times each node is visited
        return self.num_visits

        # Returns the difference of wins and losses (NOTE THAT THERE IS NO WEIGHT TO DRAWS OTHER THAN INCREASING N)

    def q(self):
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses


if __name__ == '__main__':
    main_game = GameBoard(meta_game=True)
    fmove1 = input("first board: ")
    fmove2 = input("first square: ")
    curr_pos = main_game.initial_move(fmove1, fmove2)
    tree = MCTSNode(curr_pos, main_game)
    print(print_board(main_game))
    best_move = tree.best_action(100)
    curr_pos = curr_pos.move(best_move.parent_action.position)
    print(print_board(main_game))
    while not main_game.is_complete():
        curr_pos = curr_pos.move(input("Your turn: "))
        tree = MCTSNode(curr_pos, main_game)
        curr_pos = curr_pos.move(tree.best_action().parent_action.position)
        print(print_board(main_game))





