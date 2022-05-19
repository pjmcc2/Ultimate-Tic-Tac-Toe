# This class represents the individual square of a game board. Because this is a game of ultimate tic tac toe,
# the square can be a board itself.

class GameSquare:
    POSITION_LIST = ['TL', 'TM', 'TR',  # Possible options for position: T = top, M = middle, B = bottom,
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
            print('Invalid position. Uses form TM for TopMiddle. See README for more information.')  # Update README
        if board:
            self.sub_game = GameBoard()


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
            self.squares = {'UL_Board': GameSquare('UL', board=True),  # possibly rename to UL form
                            'UM_Board': GameSquare('UM', board=True),
                            'UR_Board': GameSquare('UR', board=True),
                            'ML_Board': GameSquare('ML', board=True),
                            'MM_Board': GameSquare('MM', board=True),
                            'MR_Board': GameSquare('MR', board=True),
                            'BL_Board': GameSquare('BL', board=True),
                            'BM_Board': GameSquare('BM', board=True),
                            'BR_Board': GameSquare('BR', board=True)}
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
        self.WIN_CONS = [(self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['UM'].owner) and (self.squares['UM'].owner == self.squares['UR'].owner),  # Top Row
                    (self.squares['ML'].owner is not None) and (self.squares['ML'].owner == self.squares['MM'].owner) and (self.squares['MM'].owner == self.squares['MR'].owner),  # Middle Row
                    (self.squares['BL'].owner is not None) and (self.squares['BL'].owner == self.squares['BM'].owner) and (self.squares['BM'].owner == self.squares['BR'].owner),  # Bottom Row
                    (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['ML'].owner) and (self.squares['ML'].owner == self.squares['BL'].owner),  # Left Column
                    (self.squares['UM'].owner is not None) and (self.squares['UM'].owner == self.squares['MM'].owner) and (self.squares['MM'].owner == self.squares['BM'].owner),  # Middle Column
                    (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MR'].owner) and (self.squares['MR'].owner == self.squares['BR'].owner),  # Right Column
                    (self.squares['UL'].owner is not None) and (self.squares['UL'].owner == self.squares['MM'].owner) and (self.squares['MM'].owner == self.squares['BR'].owner),  # L-R Diagonal
                    (self.squares['UR'].owner is not None) and (self.squares['UR'].owner == self.squares['MM'].owner) and (self.squares['MM'].owner == self.squares['BL'].owner)] # R-L Diagonal

    def isComplete(self):
        for expr in self.WIN_CONS: # Iterate over win conditions to see if any are true, else return false
            if expr:
                return True
        return False

