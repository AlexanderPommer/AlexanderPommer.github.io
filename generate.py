import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            remove_words = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    remove_words.add(word)              # Can optimize by storing and checking dict of computed remove_words with key of var.lenght
            self.domains[var].difference_update(remove_words)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        remove_words = set()
        overlap = self.crossword.overlaps[x,y]
        if overlap is None:
            return revised
        else:
            i, j = overlap
        for xWord in self.domains[x]:
            possible_value = None
            for yWord in self.domains[y]:
                if xWord == yWord:
                    continue
                elif xWord[i] == yWord[j]:
                    possible_value = yWord
                    break
            if possible_value is None:
                remove_words.add(xWord)
        if remove_words:
            self.domains[x].difference_update(remove_words)
            revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = list()
            for x in self.crossword.variables:
                arcs.extend([(x,y) for y in self.crossword.neighbors(x)])
        while arcs:
            (X,Y) = arcs[0]
            arcs = arcs[1:]
            if self.revise(X, Y):
                if not self.domains[X]:
                    return False
                if self.crossword.neighbors(X).remove(Y) is not None:
                    arcs.extend([(X,y) for y in self.crossword.neighbors(X).remove(Y)])
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if any(var not in assignment for var in self.crossword.variables):
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # word lenght is var lenght
        if any(var.length != len(assignment[var]) for var in assignment):
            return False
        # no duplicate words
        words = set()
        for word in assignment.values():
            words.add(word)
        if len(words) != len(assignment):
            return False
        # no conflicts between neighbors
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    i, j = overlap
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighborsAndDomains = list()
        neighborsDomain =list()

        neighbors = self.crossword.neighbors(var)
        for neighbor in neighbors:
            if neighbor not in assignment:
                neighborsAndDomains.append((neighbor, self.domains[neighbor]))
                neighborsDomain.extend(self.domains[neighbor])

        ruledOut = list()

        domainValues = list(self.domains[var])
        for value in domainValues:

            # helper list of tuples (Variable, set(variables domain))
            # helps get the overlaps between var´s words and neighbors´ words
            neighborsAndValues = neighborsAndDomains.copy()

            # sets used to compute how many values would be ruled out
            removed_words = set()

            # check word pairs for matching overlap
            for neighborAndValues in neighborsAndValues:
                overlap = self.crossword.overlaps[var, neighborAndValues[0]]
                i,j = overlap
                for word in neighborAndValues[1]:
                    if value[i] != word[j]:
                        removed_words.add(word)

            ruledOut.append((len(removed_words), value))

        orderedDomainValues = [word for _,word in sorted(ruledOut, key=lambda words: words[0])]
        return orderedDomainValues

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassignedVariables =  list(self.crossword.variables.difference(set(assignment)))
        domain_sizes = [len(self.domains[x]) for x in unassignedVariables]
        ranked_by_domain_size = [x for _,x in sorted(zip(domain_sizes,unassignedVariables), key=lambda pair: pair[0])]

        minimumDomainVar = ranked_by_domain_size[0]
        if len(ranked_by_domain_size) > 1:
            secondMinimum = ranked_by_domain_size[1]
            # if there is a tie,
            if len(self.domains[minimumDomainVar]) == len(self.domains[secondMinimum]):
                # choose the variable with the highest degree.
                if len(self.crossword.neighbors(minimumDomainVar)) > len(self.crossword.neighbors(secondMinimum)):
                    return minimumDomainVar
                return secondMinimum
        else:
            # choose the variable with the minimum number of remaining values in its domain
            return minimumDomainVar

        return unassignedVariables[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # return a complete assignment when possible
        if self.assignment_complete(assignment):
            return assignment

        # select an unassigned variable by minimum remaining values heuristic
        var = self.select_unassigned_variable(assignment)

        # loop through the words from the selected variable´s domain ordered by least constraining values (on its neighbors´ domains) heuristic 
        for value in self.order_domain_values(var, assignment):
            
            # copy so recursion does not overwrite `assignment`
            nextAssignment = assignment.copy()

            # assign a word
            nextAssignment[var] = value

            # if the assigned word is consistent
            if self.consistent(nextAssignment):
                
                # keep track of the variables domains
                prevDomains = self.domains.copy()

                # infer reduced neighboring domains by mantaining arc consistency
                # without completely eliminating any domain
                arcs = [(neighbor,var) for neighbor in self.crossword.neighbors(var)]
                if self.ac3(arcs):

                    # recursively call bactrack with the new assignment
                    result = self.backtrack(nextAssignment)

                    # while possible word assignments for var remain keep going recursively
                    if result is not None:
                        return result

                # if no words can consistently be assigned to var, reset the assignment and the domains
                del nextAssignment[var]
                self.domains = prevDomains
        
        # possible word assignments exhausted (for the last var assigned)
        return


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
