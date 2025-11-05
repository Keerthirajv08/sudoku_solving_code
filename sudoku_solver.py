import random 
import time

def cross(items_a, items_b):
    """
    Cross product of elements in a and elements in b

    cross('ABC', '123') -> ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
    """
    #return [a + b for a in items_a for b in items_b]
    result = []     #empty list
    for a in items_a:
        for b in items_b:
            result.append(a + b)
    return result

digits = "123456789"    
rows = "ABCDEFGHI"
cols = digits
squares = cross(rows, cols)     #['A1', 'A2', ... 'I9']- defined in function cross 

unitlist = []
# Part 1: All columns (9 units)
for c in cols:      #For each column '1' to  '9'  
    column = cross(rows, c)     #['A1', 'A2', ... 'A9']
    unitlist.append(column) 

for r in rows:
    row = cross(r, cols)
    unitlist.append(row)

for rs in ("ABC", "DEF", "GHI"):
    for cs in ("123", "456", "789"):
        box = cross(rs, cs)
        unitlist.append(box)

# {} - dictionary (key-value pairs - {key: value}), sets - {1, 2, 3}, f"{var}" - changable string
#() - functions - func(), tuples-(1,2), generators - (x for x in range(10)) -
# [] - lists - [1, 2, 3], indexing- list[0], slicing- list[0:2]

units = {}      #dictionary of units 
for s in squares:       #For each square ('A1' to 'I9')
    units_for_this_square = []
    for u in unitlist:      #Check each unit
        if s in u:      #If this square is in this unit
            units_for_this_square.append(u)
    units[s] = units_for_this_square

peers = {}
for s in squares:       #For each square
    all_related_squares = set()
    for u in units[s]:  #For each unit this square belongs to
        for x in u:     #For each square in this unit
            all_related_squares.add(x)

#Remove the square itself (can't be its own peer)
    all_related_squares.remove(s)
    peers[s] = all_related_squares

def test():
    """A set of unit tests to verify the sudoku is correct."""
    assert len(squares) == 81   #test1: Check we have 81 squares (9x9 grid)
    assert len(unitlist) == 27      #test2: Check we have 27 units (9 rows + 9 cols + 9 boxes)
    for square in squares:
        assert len(units[square]) == 3, f"{square} should be part of 3 units"
    for square in squares:
        assert len(peers[square]) == 20, f"{square} should have 20 peers"
    expected_units = [
        ['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
        ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
        ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'],
    ]
    assert units["C2"] == expected_units, "C2's units are incorrect"
    #fmt: off
    expected_peers = {
        'A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
        'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
        'A1', 'A3', 'B1', 'B3'
    }
    assert peers["C2"] == expected_peers, "C2's peers are incorrect"
    #fmt: on
    print('All tests pass! ✅')


def parse_grid(grid):
    """Convert grid to a dict of possible values,  {squares: digits}, or
    return False if a contradiction is detected."""
    values = {}
    for square in squares:
        values[square] = digits

    grid_dict = grid_values(grid)

    #For each square that has a given digit, assign it
    for square, digit in grid_dict.items():
        if digit in digits:
            success = assign(values, square, digit)
            if not success:
                return False           
    return values    

def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = []          #empty list
    for c in grid:
        if  c in digits or c in "0.":
            chars.append(c)
    assert len(chars) == 81
    #dictionary pairing each square with its character
    result = {}
    for i in range(81):
        square = squares[i]
        char = chars[i]
        result[square] = char
    return result

def assign(values, s, d):
    """Assign digit d to square s by eliminating all other digits.
    Return values if successful, or False if a contradiction is detected.
    """
    other_values = values[s].replace(d, "")
    for digit_to_remove in other_values:
        success = eliminate(values, s, digit_to_remove)
        if not success:
            return False
    return values

def eliminate(values, s, d):
    """Eliminate digit d from square s and propogate constraints.
    Return values if successful, or False if a contradiction is detected.
    """
    #Check if d is already eliminated from square s
    if d not in values[s]:
        return values   #Already eliminated
    #Remove d from the possible values for square s 
    values[s] = values[s].replace(d, "")
    # Check if we created a contradiction (no values left)
    if len(values[s]) == 0:
        return False    #Contradiction: this square has no possible values!
    #Rule-1: If square s now has only one possible value,
    #eliminate this value from the peers
    if len(values[s]) == 1:
        only_value = values[s]
        for peer_square in peers[s]:
            success = eliminate(values, peer_square, only_value)
            if not success:
                return False    #Propagation caused a contradiction
    
    #Rule-2: For each units 
    for unit in units[s]:
        possible_places = []
        for square in unit:
            if d in values[square]:
                possible_places.append(square)

        #Check for contradictions or forced placements
        if len(possible_places) == 0:
            return False    #Contradiction - d has nowhere to go in this unit
        
        elif len(possible_places) == 1:
            #d can only go in one place, so assign it there
            only_place = possible_places[0]
            success = assign(values, only_place,d)
            if not success:
                return False           
    return values


def display(values):
    """Display these values as a 2-D grid."""
    #Find the width needed for each cell
    max_width = 0
    for square in squares:
        cell_width = len(values[square])
        if cell_width > max_width:
            max_width = cell_width

    width = max_width + 1       #add 1 for spacing

    #Create the horizontal line that seperates boxes
    box_width = "-" * (width * 3)
    line = "+".join([box_width, box_width, box_width])

    #Print each row
    for row in rows:
        row_string = ""
        #Build the string for this row
        for col in cols:
            square = row + col
            cell_value = values[square]

            #Center the values in the cell width
            centered_value = cell_value.center(width)
            row_string += centered_value

            #Add vertical seperator after columns 3 and 6
            if col in "36":
                row_string += "|"

        print(row_string)

        #Add horizontal line after rows C and F
        if row in "CF":
            print(line)    
    print()     #Empty line at the end



def solve(grid):
    return search(parse_grid(grid))

def some(seq):
    """Return some element of seq that is true."""
    for e in seq:
        if e:
            return e
    return False

def search(values):
    """Using depth-first search and propagation, try all possible values.
    This is the backtracking algorithm.
    1. If the puzzle is already solved, return it
    2. Pick the square with the fewest possibilities    
    3. Try each possibility and recursively search
    4. Return the first solution that works
    """
    #Check if the puzzle is already solved/failed
    if values is False:
        return False    #Puzzle is impossible
    #Check if puzzle is solved (every square has exactly one value)
    all_solved = True
    for square in squares:
        if len(values[square]) != 1:
            all_solved = False
            break
    if all_solved:
        return values   #Success! Puzzle is solved!
    
    #Find the unfilled square with the fewest possibilities
    #(This makes the search more efficient)
    best_square = None
    fewest_possibilities = 10   #Start witht more than 9
    
    for square in squares:
        num_possibilites = len(values[square])

        # Only consider squares that aren't solved yet
        if num_possibilites > 1:
            if num_possibilites < fewest_possibilities:
                best_square = square
                fewest_possibilities = num_possibilites

    #Try each possible digit for the chosen square
    for digit in values[best_square]:
        #Make a copy so we can backtrack if this doesn't work
        values_copy = values.copy()
        #Try assigning this digit
        new_values = assign(values_copy, best_square, digit)

        #Recursively search
        result = search(new_values)
        if result is not False:
            return result
     # None of the possiblite worked   
    return False    #This puzzle is unsolvable


def solve_all(grids, name="", showif=0.0):
    """Attempt to solve a sequence of grids report results."""
    def time_solve(grid):
        start = time.monotonic()
        values = solve(grid)
        t = time.monotonic() - start 
        #Display puzzles that take longer than n seconds
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values:
                display(values)
            print(f"({t:.2f} seconds)\n")
        return (t, solved(values))
    
    #Solve each puzzle and collect timing/result data
    timing_data = []
    for grid in grids:
        timing_data.append(time_solve(grid))

    
    #seperate times and results into two lists
    times = []
    results = []
    for time_taken, success in timing_data:
        times.append(time_taken)
        results.append(success)

    #Print statistics if we solved multiple puzzles
    num_puzzles = len(grids)

    if num_puzzles > 1:
        #Calculate statistics
        num_solved = sum(results)
        total_time = sum(times)
        average_time = total_time / num_puzzles
        puzzles_per_second = num_puzzles / total_time
        slowest_time = max(times)

        #Print statistics
        print(f"{name} {num_puzzles} puzzles ({num_solved} solved)")
        print(f"Average time: {average_time:.2f} seconds")
        print(f"Puzzles per second: {puzzles_per_second:.0f} Hz")
        print(f"Slowest time: {slowest_time:.2f} seconds")
        print()
    

def solved(values):
    """A puzzle is solved if each unit is a permutation of the digits 1 to 9."""
    #Check if the puzzle failed earlier
    if values is False:
        return False
    
    required_digits = set(digits)
    #Check each unit (row, column, and box)
    for unit in unitlist:
        #Get all the values in this unit
        unit_values = []
        for square in unit:
            unit_values.append(values[square])
        
        #Convert to a set to remote duplicates
        unique_values = set(unit_values)
        #Check if the unit is a permutation of the digits
        
        if unique_values != required_digits:
            return False        #THis unit is missing a digit or has duplicates
    #all units are valid!
    return True

def from_file(filename, sep="\n"):
    """Parse a file into a """
    with open(filename) as file:
        return file.read().strip().split(sep)

def random_puzzle(assignments=17):
    #Start with an empty grid (all squares can be any digit)
    values = {}
    for square in squares:
        values[square] = digits 
    #Randomly assign digits to squares
    random_squares = shuffled(squares)  #randomly order the squares

    for square in random_squares:
        #Pick a random digit from the possible values for this square
        possible_digits = values[square]
        random_digit = random.choice(possible_digits)

        #Try to assign this digit
        success = assign(values, square, random_digit)

        #If assignment causes a contradiction, give up and start over
        if not success:
            break

        #check if we have enough assignments yet
        #Count how many squares have been solved (only one possible value)
        solved_squares = []
        for s in squares:
            if len(values[s]) == 1:
                solved_squares.append(values[s])
        
        num_solved = len(solved_squares)
        num_unique_digits = len(set(solved_squares))

        #We need atleast 'assignments' clues and atleast 8 different digits
        if num_solved >= assignments and num_unique_digits >= 8:
            #Build the puzzle string
            puzzle_string = ""
            for s in squares:
                if len(values[s]) == 1:
                    #This square is solved, use its digit
                    puzzle_string += values[s]
                else:
                    #This square is empty, usea dot
                    puzzle_string += "."
            
            return puzzle_string 
     #try again recursively   
    return random_puzzle(assignments)


def shuffled(seq):
    """Return a randomly shuffled copy of the input sequence."""
    seq = list(seq)
    random.shuffle(seq)
    return seq

grid1 = (
    "003020600"
    "900305001"
    "001806400"
    "008102900"
    "700000008"
    "006708200"
    "002609500"
    "800203009"
    "005010300"
)

grid2 = (
    "400000805"
    "030000000"
    "000700000"
    "020000060"
    "000080400"
    "000010000"
    "000603070"
    "500200000"
    "104000000"
)

hard1 = (
    ".....6....59.....82....8....45........3........6..3.54...325..6.................."
)

if __name__ == "__main__":
    test()
    print("\n--- Solving Random Puzzles ---")
    random_puzzles = []
    for i in range(99):
        random_puzzles.append(random_puzzle())
    solve_all(random_puzzles, "random", 100.0)

    print("\n---solving Example puzzles---")
    example_puzzles = [ grid1,grid2 , hard1]

    for puzzle in example_puzzles:
        #Display the starting puzzle
        print("\nStarting puzzle:")
        display(parse_grid(puzzle))

        #Solve and time it
        start_time = time.monotonic()
        solve(puzzle)
        end_time = time.monotonic()
        print("Solved in", end_time - start_time, "seconds")




