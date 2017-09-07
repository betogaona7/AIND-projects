import itertools
assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
col_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[rows[i]+cols[i] for i in range(0,len(rows))]] + [[rows[i]+cols[-i-1] for i in range(0, len(rows))]]

unitlist = row_units + col_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[])) - set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    dictionary = {}
    for box, value in zip(boxes, grid):
        if value == '.':
            value = '123456789'
        dictionary[box] = value
    return dictionary

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

""" 
    Naked twin - is an intermediate solving technique, where Sudoku is scanned for a pair of cells in a unit containing only the 
       same two candidates. Since these candidates must go in these cells, the can therefore be removed from the candidate lists 
       of all other unsolved cells in that unit. Reducing candidate lists may reveal a hidden or naked single in another unsolved
       cell, however the technique is a step to solving the next cell
"""
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist: 
        # List of all values (and their boxes) containing only 2 possibilities (candidates to be naked pair)
        candidates = [(values[box], box) for box in unit if len(values[box]) == 2] 
        if len(candidates) >= 2:
            # Get pairs, if len(candidates > 2), then we need to make combinations to test each possible pair
            pairs = [list(combination) for combination in itertools.combinations(candidates,2)]
            for pair in pairs:
                candidate1, candidate2 = pair[0], pair[1]
                # Here we know if is a naked pair or not and then we eliminate it as possibilities for their peers 
                if candidate1[0] == candidate2[0]: 
                    for box in unit:
                        # Ensure that we don't modify boxes with values already assigned or modify our naked pair
                        if len(values[box]) >= 2 and candidate1[1] != box and candidate2[1] != box: 
                            for digit in candidate1[0]:
                                assign_value(values, box, values[box].replace(digit,""))
    return values

"""
    Elimination - If a box has a value assgined, then none of the peers of this box can have this value
"""
def eliminate(values):
    """

    This function will iterate over all the boxes in the puzzle that only have one value 
    assigned to them, and it will remove this value from every one of its peers.

    """
    for box, value in values.items():
        if len(value) == 1: 
            for peer in peers[box]:
                assign_value(values, peer, values[peer].replace(value,""))
    return values

"""
    Only choice - Every unit must contain exactly one occurrence of every number 
"""
def only_choice(values):
    """

    This function will go through all the units, with a digit that only fits in one possible 
    box, it will assing that digit to that box.

    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
                #values[dplaces[0]] = digit
    return values

"""
    Constraint propagation - Is all about using local constraints in a space to dramatically reduce the search space.
       As we enforce each constraint, we see how it introduces new constraints for other parts of the board that can 
       help us further reduce the number of possibilities.
"""
def reduce_puzzle(values): # def reduce_puzzle(values, is_diagonal):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value 
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Apply constraints 
        values = naked_twins(only_choice(eliminate(values)))
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False # This means probably that the sudoku is not a X Sudoku (diagonal)
    return values

"""
    Search using Depth-First Search algorithm - without this strategy, we didn't solve hard tests. It seemed to reduce 
       every box to a number of possibilities, but it won't go further than that.
"""
def search(values): 
    # First reduce the puzzle using constraint propagation function
    values = reduce_puzzle(values)
    if values == False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values ## That means Soduku was solved!

    # Select one of the unfilled squares with the fewest posibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # Now use recursion to solve each one of the resulting Sudokus, and if one returns a value (not False) return that answer 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = search(grid_values(grid))
    if not values:
        return False # No solution

    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')






"""def three_line(values):
    for digit in '123456789':
        print("searching digit: ", digit)
        cont = 0
        for i in range(0,3):
            ocurrences = 0
            for j in range(0,3):
                #print("set: ", i, " row: ",j, " boxes: ", row_units[cont])
                
                # Here we scan 3 rows 
                #vals = [values[box] for box in row_units[cont] ]
                for box in row_units[cont]:
                    if digit == values[box]:
                        ocurrences += 1
                        print(box)

                cont += 1
            if ocurrences == 3:
                break # The digit is "solved"
                #
                
            print('\n')
        print('\n')
    return values"""