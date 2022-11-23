import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.safes.add(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        
        # Initialize new cells set
        new_cells = set()

        # loop over all cells within one row and column of `cell`
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # add cells that are within bounds and not already known to be safe to the new sentence
                if 0 <= i < self.height and 0 <= j < self.width:
                    c = (i,j)
                    if c not in self.safes:
                        new_cells.add(c)

        # create a new sentence
        new_sentence = Sentence(new_cells, count)
        
        # if the mine count = the number of cells in the new sentence, all such cells must be mines. Update the knowledge base
        if len(new_sentence.cells) == count: # suboptimal double check - again in known_mines()
            for c in new_sentence.known_mines():
                self.mark_mine(c)

        # if the mine count is 0, none of the cells in the sentence are mines. Update the knowledge base
        elif count == 0: # suboptimal double check - again in known_safes()
            for c in new_sentence.known_safes():
                self.mark_safe(c)

        # if mines or safes can't be deduced add the new sentence to the knowledge base
        else:
            self.knowledge.append(new_sentence) 

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        if len(self.knowledge) > 1:

            knowledge = copy.copy(self.knowledge) # self.knowledge may be modified during iteration so we iterate over a copy of it

            empty = Sentence(set(),0)

            for sentence in knowledge:

                # clear empty sentences
                if sentence == empty:
                    self.knowledge.remove(sentence)

            knowledge = copy.copy(self.knowledge)

            for A, B in itertools.permutations(knowledge, 2):
                
                # if set1 of cells is a subset of set2, infer a new sentence as `set2 - set1 = count2 - count1`
                if A.cells.issubset(B.cells):
                    
                    new_sentence = Sentence(B.cells.difference(A.cells), B.count - A.count)
                    if new_sentence.cells and new_sentence not in knowledge:
                        self.knowledge.append(new_sentence)
                        
            knowledge = copy.copy(self.knowledge)

            for sentence in knowledge:
                
                # mark known mines
                known_mines = copy.copy(sentence.known_mines())
                if known_mines:
                    for mine in known_mines:
                        self.mark_mine(mine)

                # mark known safes
                known_safes = copy.copy(sentence.known_safes())
                if known_safes:
                    for safe in known_safes:
                        self.mark_safe(safe)

                # clear empty sentences
                if sentence == empty:
                    self.knowledge.remove(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        possible_safe_moves = list(self.safes.difference(self.moves_made.union(self.mines)))

        safe_move = None

        if possible_safe_moves:
            safe_move = random.choice(possible_safe_moves)

        return safe_move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # get a set of all the cells on the board
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i,j))
        
        # get a set of acceptable random moves by removing moves already made and known mines from all moves
        acceptable_random_moves = list(all_moves.difference(self.mines.union(self.moves_made)))
        
        random_move = None
        
        if acceptable_random_moves:
            random_move = random.choice(acceptable_random_moves)

        return random_move
