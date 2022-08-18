"""
Command Line Chess
2022 August 
Alexander Michael Pommer Alba
"""

from time import sleep

BOARD = [] # 1d board that stores instances of Squares or Pieces
UCI_map = {} # Universal Chess Interface dictionary to map player input
LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
counter = 0
for number in range(1,9):
    for letter in LETTERS:
        UCI_map[f'{letter}{number}'] = counter
        counter += 1
reverse_UCI_map = {value: key for key, value in UCI_map.items()} # Helps users see legal moves for a selected piece
KINGS = {} # Tracks kings to make checks easier to compute
EN_PASSANT = [] # Tracks pawns capable of an en passant move, helps remove such capacity after one turn


class Square:

    def __init__(self, position: int, color = 'Empty', type_ = ' ') -> None:
        self.position = position # 0 to 63
        self.color = color # 'Black', 'White' or 'Empty'
        self.type_ = type_

    def is_empty(self) -> bool:
        return self.color == "Empty"

    def legal_moves(self):
        return []

    def print_legal_moves(self, legal):
        rev = []
        for l in legal:
            rev.append(reverse_UCI_map[l])
        print('legal moves', rev)


class Pawn(Square):

    def __init__(self, position: int, color: str, type_: str, en_passant = False) -> None:
        super().__init__(position, color, type_)
        self.en_passant = en_passant

    def is_empty(self) -> bool:
        return super().is_empty()

    def legal_moves(self):

        legal = []

        if self.color == 'White':
            
            one_step = self.position + 8
            if one_step < 64 and BOARD[one_step].is_empty():
                legal.append(one_step)

            capture_right = self.position + 9
            # Not in far right file 'h' and enemy piece in position
            if self.position % 8 != 7 and BOARD[capture_right].is_empty() == False and BOARD[capture_right].color != self.color:
                legal.append(capture_right)
            
            capture_left = self.position + 7
            # Not in far left file 'a' and enemy piece in position
            if self.position % 8 != 0 and BOARD[capture_left].is_empty() == False and BOARD[capture_left].color != self.color:
                legal.append(capture_left)

            two_steps = self.position + 16
            if self.position in range(8, 16) and BOARD[two_steps].is_empty():
                legal.append(two_steps)

        if self.color == 'Black':

            one_step = self.position - 8
            if one_step >= 0 and BOARD[one_step].is_empty():
                legal.append(one_step)

            capture_right = self.position - 7
            # Not in far right file 'h' and enemy piece in position
            if self.position % 8 != 7 and BOARD[capture_right].is_empty() == False and BOARD[capture_right].color != self.color:
                legal.append(capture_right)

            capture_left = self.position - 9
            # Not in far left file 'a' and enemy piece in position
            if self.position % 8 != 0 and BOARD[capture_left].is_empty() == False and BOARD[capture_left].color != self.color:
                legal.append(capture_left)
            
            two_steps = self.position - 16
            if self.position in range(48, 56) and BOARD[two_steps].is_empty():
                legal.append(two_steps)
                
        if self.en_passant:
            legal.append(self.en_passant)

        return legal
        
    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:
            
            if self.color == 'White':

                # Set en passant
                if move_to == self.position + 16: # if 2 step move
                    for side_pawn in [move_to - 1, move_to + 1]: # check for enemy neighboring pawns that could intercept en passant
                        if side_pawn in range((move_to // 8) * 8, (move_to // 8) * 8 + 8) and BOARD[side_pawn].type_ == 'p':

                            BOARD[side_pawn].en_passant = move_to - 8 # set interception position
                            EN_PASSANT.append(BOARD[side_pawn]) # track pawns

                    BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)
                
                # Execute en passant
                # if a pawn can move to an empty square diagonally
                elif BOARD[move_to].is_empty() and (move_to == self.position + 7 or move_to == self.position + 9):
                        BOARD[move_to - 8] = Square(move_to - 8)
                        BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)

                # Promote if pawn reaches it's highest rank
                elif move_to in range(56, 64):
                    while True:
                        try:
                            promotion = input(f"Type 'Queen', 'Rook', 'Knight' or 'Bishop' to promote pawn at {reverse_UCI_map[move_to]}: ").lower()

                            if promotion[:1] == 'q':
                                BOARD[self.position], BOARD[move_to] = Square(self.position), Queen(move_to, self.color, 'Q')
                                return
                            elif promotion[:1] == 'r':
                                BOARD[self.position], BOARD[move_to] = Square(self.position), Rook(move_to, self.color, 'R')
                                return
                            elif promotion[:1] == 'k':
                                BOARD[self.position], BOARD[move_to] = Square(self.position), Knight(move_to, self.color, 'N')
                                return
                            elif promotion[:1] == 'b':
                                BOARD[self.position], BOARD[move_to] = Square(self.position), Bishop(move_to, self.color, 'B')
                                return
                        except:
                            pass
                else:
                    # Basic move
                    BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)

            
            elif self.color == 'Black':
                        
                # Set en passant
                if move_to == self.position - 16: # if 2 step move
                    for side_pawn in [move_to - 1, move_to + 1]: # check for enemy neighboring pawns that could intercept en passant
                        if side_pawn in range((move_to // 8) * 8, (move_to // 8) * 8 + 8) and BOARD[side_pawn].type_ == 'P':

                            BOARD[side_pawn].en_passant = move_to + 8 # set interception position
                            EN_PASSANT.append(BOARD[side_pawn]) # track pawns
                    # Basic move
                    BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)
                
                # Execute en passant
                    # if a pawn can move to an empty square diagonally
                elif BOARD[move_to].is_empty() and (move_to == self.position - 9 or move_to == self.position - 7):

                        BOARD[move_to + 8] = Square(move_to + 8, 'Empty', ' ')
                        # Basic move
                        BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)
                
                    # Promote if pawn reaches it's highest rank
                elif move_to in range(0, 8):
                    while True:
                        try:
                            promote_black = input(f"Type 'Queen', 'Rook', 'Knight' or 'Bishop' to promote pawn at {reverse_UCI_map[move_to]}: ").lower()
                        
                            if promote_black[:1] == 'q':
                                BOARD[self.position], BOARD[move_to] = Square(self.position),Queen(move_to, self.color, 'q')
                                return
                            elif promote_black[:1] == 'k':
                                BOARD[self.position], BOARD[move_to] = Square(self.position),Knight(move_to, self.color, 'n')
                                return
                            elif promote_black[:1] == 'r':
                                BOARD[self.position], BOARD[move_to] = Square(self.position),Rook(move_to, self.color, 'r')
                                return
                            elif promote_black[:1] == 'b':
                                BOARD[self.position], BOARD[move_to] = Square(self.position),Bishop(move_to, self.color, 'b')
                                return
                    
                        except:
                            pass

                else:
                    # Basic move
                    BOARD[self.position], BOARD[move_to] = Square(self.position), Pawn(move_to, self.color, self.type_)      

                
            
        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


class King(Square):

    def __init__(self, position: int, color: str, type_: str, can_castle = False) -> None:
        super().__init__(position, color, type_)
        self.can_castle = can_castle # Enables castling if True

    def is_empty(self) -> bool:
        return super().is_empty()
    
    def enemy_color(self):
        if self.color == 'White':
            return 'Black'
        else:
            return 'White'

    def check(self):
        for enemy_piece in BOARD:
            if self.enemy_color() == enemy_piece.color:
                if self.position in enemy_piece.legal_moves():
                    return True
        return False

    def legal_moves(self):
        legal = []

        top_left = self.position - 9
        up = self.position - 8
        top_right = self.position - 7

        for sq in [top_left, up, top_right]:
            if sq >= 0 and BOARD[sq].color != self.color and self.position // 8 == sq // 8 + 1:
                legal.append(sq)

        bottom_left = self.position + 7
        down = self.position + 8
        bottom_right = self.position + 9

        for sq in [bottom_left, down, bottom_right]:
            if sq < 64 and BOARD[sq].color != self.color and self.position // 8 + 1 == sq // 8:
                legal.append(sq)

        left = self.position - 1
        right = self.position + 1

        for sq in [left, right]:
            if sq >= 0 and sq < 64 and self.color != BOARD[sq].color and self.position // 8 == sq // 8:
                legal.append(sq)

        if self.can_castle:

            left_rook = BOARD[(self.position // 8 * 8)] # object at index 0 or 56
            right_rook = BOARD[(self.position // 8 * 8 + 7)] # object at index 7 or 63

            if left_rook.is_empty() == False:
                    l, r = self.position - 2, self.position - 1
                    if BOARD[l].is_empty() and BOARD[r].is_empty():
                        legal.append(l)
            
            if right_rook.is_empty() == False:
                if right_rook.can_castle:
                    l, r = self.position + 1, self.position + 2
                    if BOARD[l].is_empty() and BOARD[r].is_empty():
                        legal.append(r)
                        
        return legal

    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:

            # Castle left
            if move_to == self.position - 2:
                BOARD[move_to + 1], BOARD[self.position - 4] = Rook(move_to + 1, self.color, BOARD[self.position - 4].type_), Square(self.position - 4)

            # Castle right
            elif move_to == self.position + 2:
                BOARD[move_to - 1], BOARD[self.position + 3] = Rook(move_to + 1, self.color, BOARD[self.position + 3].type_), Square(self.position + 3,)

            BOARD[self.position], BOARD[move_to] = Square(self.position, 'Empty', ' '), King(move_to, self.color, self.type_)

            KINGS[turn_color] = BOARD[move_to]

        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


class Knight(Square):

    def __init__(self, position: int, color: str, type_: str) -> None:
        super().__init__(position, color, type_)

    def is_empty(self) -> bool:
        return super().is_empty()

    def legal_moves(self):
        legal = []

        up2_right1 = self.position - 15
        up2_left1 = self.position - 17
        
        for up2 in [up2_right1, up2_left1]:
            
            # No up2 squares left
            if self.position // 8 != up2 // 8 + 2:
                continue
            
            if up2 >= 0:

                # Prevent friendly fire
                if BOARD[up2].color == self.color:
                    continue

                legal.append(up2)
        
        up1_right2 = self.position - 6
        up1_left2 = self.position - 10

        for up1 in[up1_right2, up1_left2]:

            # No up1 squares left
            if self.position // 8 != up1 // 8 + 1:
                continue

            if up1 >= 0:

                # Prevent friendly fire
                if BOARD[up1].color == self.color:
                    continue

                legal.append(up1)

        down1_left2 = self.position + 6
        down1_right2 = self.position +10

        for down1 in [down1_left2, down1_right2]:

            # No down1 squares left
            if self.position // 8 != down1 // 8 - 1:
                continue

            if down1 < 64:

                # Prevent friendly fire
                if BOARD[down1].color == self.color:
                    continue

                legal.append(down1)

        down2_left1 = self.position + 15
        down2_right1 = self.position + 17

        for down2 in [down2_left1, down2_right1]:

            # No down2 squares left
            if self.position // 8 != down2 // 8 - 2:
                continue

            if down2 < 64:

                # Prevent friendly fire
                if BOARD[down2].color == self.color:
                    continue

                legal.append(down2)

        return legal
    
    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:

            BOARD[self.position], BOARD[move_to] = Square(self.position, 'Empty', ' '), Knight(move_to, self.color, self.type_)

        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


class Rook(Square):

    def __init__(self, position: int, color: str, type_: str, can_castle = False) -> None:
        super().__init__(position, color, type_)
        self.can_castle = can_castle # Enables Castling if True

    def is_empty(self) -> bool:
        return super().is_empty()

    def legal_moves(self):
        legal = []

        for up in range(self.position - 8, -1, -8):

            if BOARD[up].color != self.color:
                legal.append(up)
            
            if BOARD[up].is_empty() == False:
                break

        for down in range(self.position + 8, 64, 8):

            if BOARD[down].color != self.color:
                legal.append(down)
            
            if BOARD[down].is_empty() == False:
                break

        for left in range(self.position - 1, ((self.position//8) * 8) - 1, -1):
            
            if BOARD[left].color != self.color:
                legal.append(left)

            if BOARD[left].is_empty() == False:
                break

        for right in range(self.position + 1, (self.position//8) * 8 + 8):
            
            if BOARD[right].color != self.color:
                legal.append(right)

            if BOARD[right].is_empty() == False:
                break

        return legal

    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:

            BOARD[self.position], BOARD[move_to] = Square(self.position, 'Empty', ' '), Rook(move_to, self.color, self.type_)

        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


class Bishop(Square):

    def __init__(self, position: int, color: str, type_: str) -> None:
        super().__init__(position, color, type_)

    def is_empty(self) -> bool:
        return super().is_empty()

    def legal_moves(self):
        legal = []
        
        prev_top_right = self.position
        for top_right in range(self.position - 7, 0, - 7):
            
            # No top right square
            if prev_top_right // 8 == top_right // 8:
                break

            # Prevent friendly fire
            if BOARD[top_right].color == self.color:
                break

            legal.append(top_right)

            # End path at obstruction
            if BOARD[top_right].is_empty() == False:
                break

            # Update trailing variable
            prev_top_right = top_right

        prev_top_left = self.position
        for top_left in range(self.position - 9, -1, - 9):
            
            # No top left square
            if prev_top_left // 8 != top_left // 8 + 1:
                break

            # Prevent friendly fire
            if BOARD[top_left].color == self.color:
                break

            legal.append(top_left)

            # End path at obstruction
            if BOARD[top_left].is_empty() == False:
                break

            # Update trailing variable
            prev_top_left = top_left

        prev_bottom_right = self.position
        for bottom_right in range(self.position + 9, 64, 9):
            
            # No bottom right square
            if prev_bottom_right // 8 + 1 != bottom_right // 8:
                break

            # Prevent friendly fire
            if BOARD[bottom_right].color == self.color:
                break

            legal.append(bottom_right)

            # End path at obstruction
            if BOARD[bottom_right].is_empty() == False:
                break
            
            # Update trailing variable
            prev_bottom_right = bottom_right

        prev_bottom_left = self.position
        for bottom_left in range(self.position + 7, 64, 7):
            
            # No bottom left square
            if prev_bottom_left // 8 == bottom_left // 8:
                break

            # Prevent friendly fire
            if BOARD[bottom_left].color == self.color:
                break

            legal.append(bottom_left)

            # End path at obstruction
            if BOARD[bottom_left].is_empty() == False:
                break

            # Update trailing variable
            prev_bottom_left = bottom_left

        return legal

    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:

            BOARD[self.position], BOARD[move_to] = Square(self.position, 'Empty', ' '), Bishop(move_to, self.color, self.type_)

        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


class Queen(Rook, Bishop):

    def __init__(self, position: int, color: str, type_: str) -> None:
        super().__init__(position, color, type_)

    def is_empty(self) -> bool:
        return super().is_empty()

    def legal_moves(self):
        legal = []
        legal.extend(Rook.legal_moves(self))
        legal.extend(Bishop.legal_moves(self))
        return(legal)

    def move(self, move_to, turn_color):
        legal = self.legal_moves()

        if move_to in legal:

            BOARD[self.position], BOARD[move_to] = Square(self.position, 'Empty', ' '), Queen(move_to, self.color, self.type_)

        # ilegal move, try again
        else:
            super().print_legal_moves(legal)
            return player_input(turn_color)


def initialize_board():
    BOARD.append(Rook(0, 'White', 'R', True)) # can_castle defaults to False, it is only set to true on start(when a piece has not moved)
    BOARD.append(Knight(1, 'White', 'N'))     # any move will create another instance on the board setting can_castle to its default value
    BOARD.append(Bishop(2, 'White', 'B'))
    BOARD.append(Queen(3, 'White', 'Q'))
    BOARD.append(King(4, 'White', 'K', True))
    KINGS['White'] = BOARD[4]
    BOARD.append(Bishop(5, 'White', 'B'))
    BOARD.append(Knight(6, 'White', 'N'))
    BOARD.append(Rook(7, 'White', 'R', True))
    for sq in range(8, 16):
        BOARD.append(Pawn(sq, 'White', 'P'))
    for sq in range(16, 48):
        BOARD.append(Square(sq, 'Empty', ' '))
    for sq in range(48, 56):
        BOARD.append(Pawn(sq, 'Black', 'p'))
    BOARD.append(Rook(56, 'Black', 'r', True))
    BOARD.append(Knight(57, 'Black', 'n'))
    BOARD.append(Bishop(58, 'Black', 'b'))
    BOARD.append(Queen(59, 'Black', 'q'))
    BOARD.append(King(60, 'Black', 'k', True))
    KINGS['Black'] = BOARD[60]
    BOARD.append(Bishop(61, 'Black', 'b'))
    BOARD.append(Knight(62, 'Black', 'n'))
    BOARD.append(Rook(63, 'Black', 'r', True))


def display_board():

    print('\n'*3) # clear screen

    files = '   |' # columns header
    for letter in LETTERS:
        files += f' {letter} |'
    print(files)

    for rank in range(1, 9): # rows
        ranks = f' {rank} |'
        for sq in range(rank * 8 - 8, rank * 8):
            ranks += f' {BOARD[sq].type_} |'
        print('------------------------------------')
        print(ranks)
    print('   ---------------------------------')
    print('\n'*3)


def player_input(turn_color, checked = False):

    while True:
        try:
            
            input_text = input(f"{turn_color} player's move: ").lower()
            if input_text == 'resign':
                print(KINGS[turn_color].enemy_color(), 'Wins!')
                break

            selected_piece = BOARD[UCI_map[input_text[:2]]]

            if turn_color == selected_piece.color:
                
                move_to = BOARD[UCI_map[input_text[-2:]]].position
                
                selected_piece.move(move_to, turn_color)

                display_board()

                sleep(1.25) # Allows Demo using copy + paste from a list of moves 

                # Check helpers
                own_king = KINGS[turn_color]
                enemy_king = KINGS[own_king.enemy_color()]
                
                # Checkmate
                if own_king.check():
                    if checked:
                        print('Checkmate!')
                        sleep(1)
                        print(enemy_king.color, 'wins!')
                        break
                    return player_input(turn_color)

                # Check
                if enemy_king.check():
                    print('Check!')
                    sleep(1)
                    return player_input(enemy_king.color, checked = True)

                # Ensure pawns are only capable of an en passant move for a single turn
                for pawn in EN_PASSANT:
                    if pawn.color == turn_color:
                        pawn.en_passant = False
                        EN_PASSANT.remove(pawn)

                if turn_color == 'White':
                    return player_input('Black')
                else:
                    return player_input('White')

        except:
            pass

# Run the game
initialize_board()
display_board()
player_input('White')
