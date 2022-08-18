# Command Line Chess
#### Video Demo:  [Chess Demo](https://www.youtube.com/watch?v=As9JWDEAN3Q)
#### Description:

A python program that runs a 2 player game of chess in the command line.

#### Instructions for players

Download chess.py install python, open the command line and go to the directory where chess.py is located, then type:
`python3 chess.py`
you will be prompted for the white player's move. You can type moves in the Universal Chess Interface format as "LetterNumberLetterNumber", e.g. "e2e4", the first 2 characters indicate the file (column) and rank (row) of the piece you want to move, and the last 2 characters mark the destination. If you mistype a move, the game will print a list of the legal moves for your selected piece. You can type "resign" instead of a move to end the game.

#### Design choices

This was built from an Object Oriented Programing (OOP) outlook.

The chess board `BOARD` is represented by a 1 dimensional list of 64 objects that are instances of classes. It could be represented as 2d or with extra objects that could aid in computing moves. I found it simpler to work with a 1d list. To get a rank (row) for a given position the program does a floor division `x // 8` by and to get the file (column) it uses modulo `x % 8`.

The base class `Square` has attributes `position`, `color` and `type_` and a few basic methods that are inherited and/or extended by the rest of the piece classes.
The `Pawn` class extends `Square.__init()__` with the attribute `en_passant` that tracks if a pawn can perform an en passant move. The `King` and `Rook` classes also extended the `__init__` method with an attribute `can_castle` that records whether those pieces have moved previously (if so castling is ilegal).

 The methods used to move are `legal_moves()`, which returns a list of all the legal moves for a given chess piece, and `move()` which takes a valid user move format as input, checks if its legal and creates new instances of pieces or `Square` classes on the corresponding positions on the `BOARD`. 
 
 The OOP approach made it notably easy to code the `Queen` class, it simply inherited the `legal_moves()` method from the `Rook` and the `Bishop` classes.

 The game runs as a while loop where the board is displayed, the player is asked for input and the moves are executed until a checkmate or a resignation happens. 

 #### Files

* chess_demo.txt - This file contains the moves used in the demo video, you can copy and then paste them to the terminal with a right click.

* chess.py - The program.

* README.md - This file.