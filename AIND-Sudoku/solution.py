import collections

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

diagonal_units = [[rows[i]+cols[i] for i in range(0,len(rows))]] + \
                 [[rows[i]+cols[-i-1] for i in range(0, len(rows))]] 

#diagonal_units = [['A1','B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'],
#                  ['A9','B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]

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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    """
    naked_pairs = []
    for unit in unitlist:
        unfilled = [box for box in unit if len(values[box]) == 2] # Get all unfilled boxes that have 2 posibilities
        if len(unfilled) == 2:
            naked_pairs.append(unfilled) #Have almost 2 unfilled boxes
        
    for pair in naked_pairs:
        if values[pair[0]] == values[pair[1]]:
            #print("Naked pair true - ", pair, " values: ", values[pair[0]], " ", values[pair[1]])

            for peer in peers[pair[0]]:
                if peer != pair[1] and len(values[peer]) > 1:
                    #print(values[peer])
                    for digit in values[pair[0]]:
                        assign_value(values, peer, values[peer].replace(digit,""))
        #else:
        #    print(pair) """
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

def eliminate(values):
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                assign_value(values, peer, values[peer].replace(value,""))
                #values[peer] = values[peer].replace(value,"")
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
                #values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = only_choice(eliminate(values))

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

"""
def search(values):
    values = reduce_puzzle(values)
    if not values:
        return False

    unfilled = [box for box in boxes if len(values[box]) > 1]

    if len(unfilled) == 0:
        return values

    minimum = len(values[unfilled[0]])
    boxselected = unfilled[0]

    for box in unfilled:
        if minimum > len(values[box]):
            minimum = len(values[box])
            boxselected = box

    for digit in values[boxselected]:
        new_sudoku = values.copy()
        new_sudoku[boxselected] = digit

        if search(new_sudoku):
            return search(new_sudoku)"""
def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier 
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!! 

    # Choose one of the unfilled squares with the fewest possibilities 
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
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
    #values = search(grid_values(grid))
    values = only_choice(eliminate(grid_values(grid)))
    if not values:
        return False # No solutio

    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
    

    """try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')"""
