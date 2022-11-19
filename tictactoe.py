"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X

    Xs = sum(row.count(X) for row in board)
    Os = sum(row.count(O) for row in board)

    if Xs > Os:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Return empty positions
    legal_moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                legal_moves.add((i,j))
    return legal_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Prevent illegal moves
    if action not in actions(board):
        raise ValueError
    
    res = copy.deepcopy(board)
    i, j = action
    res[i][j] = player(board)
    return res


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    lines = [[(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)], # horizontal
             [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)], # vertical
             [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]                       # diagonal
            ]
    
    for line in lines:
        Ai = line[0][0]
        Aj = line[0][1]
        Bi = line[1][0]
        Bj = line[1][1]
        Ci = line[2][0]
        Cj = line[2][1]
        
        if board[Ai][Aj] == board[Bi][Bj] and board[Bi][Bj] == board[Ci][Cj]:
            if board[Ai][Aj] != EMPTY:
                return board[Ai][Aj]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    for row in board:
        for square in row:
            if square == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)

    if win == X:
        return 1

    if win == O:
        return -1
    
    return 0


def max_value(board):
    v = float("-inf")
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    v = float("inf")
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    max_player = "X"
    min_player = "O"
    optimal_action = None
    
    if player(board) == max_player:
        v = float("-inf")
        
        for action in actions(board):

            val = min_value(result(board, action))
            if val > v:
                optimal_action = action
                v = val

    elif player(board) == min_player:
        v = float("inf")
        
        for action in actions(board):
            
            val = max_value(result(board, action))
            if val < v:
                optimal_action = action
                v = val

    return optimal_action
