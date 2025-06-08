from django.shortcuts import render

def parse_grid(request):
    """Parse the grid from POST data"""
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            val = request.POST.get(f'cell_{i}_{j}', '').strip()
            if val.isdigit() and 1 <= int(val) <= 9:
                row.append(int(val))
            else:
                row.append(0)
        grid.append(row)
    return grid

def has_duplicates_in_unit(unit):
    """Check if a unit (row, column, or box) has duplicate non-zero values"""
    seen = set()
    for val in unit:
        if val != 0:
            if val in seen:
                return True
            seen.add(val)
    return False

def is_valid_grid(grid):
    """Check if the current grid state is valid"""
    # Check all rows for duplicates
    for row in grid:
        if has_duplicates_in_unit(row):
            return False
    
    # Check all columns for duplicates
    for col in range(9):
        column = [grid[row][col] for row in range(9)]
        if has_duplicates_in_unit(column):
            return False
    
    # Check all 3x3 boxes for duplicates
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = []
            for r in range(box_row, box_row + 3):
                for c in range(box_col, box_col + 3):
                    box.append(grid[r][c])
            if has_duplicates_in_unit(box):
                return False
    
    return True

def is_valid_placement(grid, row, col, num):
    """Check if placing num at (row, col) is valid"""
    # Check row - exclude the current cell
    for c in range(9):
        if c != col and grid[row][c] == num:
            return False
    
    # Check column - exclude the current cell
    for r in range(9):
        if r != row and grid[r][col] == num:
            return False
    
    # Check 3x3 box - exclude the current cell
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r != row or c != col) and grid[r][c] == num:
                return False
    
    return True

def get_possible(grid, row, col):
    """Get possible numbers for a cell"""
    if grid[row][col] != 0:
        return set()
    
    possible = set()
    for num in range(1, 10):
        if is_valid_placement(grid, row, col, num):
            possible.add(num)
    
    return possible

def find_mrv(grid):
    """Find cell with minimum remaining values (MRV heuristic)"""
    min_possibilities = 10
    best_cell = None
    
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                possibilities = get_possible(grid, i, j)
                if len(possibilities) == 0:
                    # No valid moves for this cell - unsolvable
                    return None
                if len(possibilities) < min_possibilities:
                    min_possibilities = len(possibilities)
                    best_cell = (i, j, possibilities)
                    if min_possibilities == 1:
                        return best_cell
    
    return best_cell

def solve(grid):
    """Solve the Sudoku puzzle using backtracking with MRV heuristic"""
    mrv = find_mrv(grid)
    
    # No empty cells found - puzzle is solved
    if mrv is None:
        # Check if this is because we're done or because we hit a dead end
        if not has_empty_cells(grid):
            return True
        else:
            # We found a cell with no possibilities - dead end
            return False
    
    row, col, candidates = mrv
    
    for num in candidates:
        grid[row][col] = num
        if solve(grid):
            return True
        grid[row][col] = 0
    
    return False

def has_empty_cells(grid):
    """Check if grid has any empty cells"""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return True
    return False

def sudoku_view(request):
    """Main view for Sudoku solver"""
    # Initialize empty grid for display
    grid_for_display = [['' for _ in range(9)] for _ in range(9)]
    original_cells = set()
    
    context = {
        "grid": grid_for_display,
        "original_cells": original_cells,
        "error": None,
        "is_solved": False
    }
    
    # Handle new puzzle request
    if request.GET.get('new') == '1':
        return render(request, "sudoku_form.html", context)
    
    if request.method == "POST":
        try:
            # Parse the grid from form data
            grid = parse_grid(request)
            
            # Create display grid with original values
            for i in range(9):
                for j in range(9):
                    if grid[i][j] != 0:
                        grid_for_display[i][j] = grid[i][j]
                        original_cells.add(f"{i}_{j}")
                    else:
                        grid_for_display[i][j] = ''
            
            # Check if the initial grid is valid
            if not is_valid_grid(grid):
                context.update({
                    "grid": grid_for_display,
                    "original_cells": original_cells,
                    "error": "Invalid Sudoku! Please check for duplicate numbers in rows, columns, or 3x3 boxes."
                })
                return render(request, "sudoku_form.html", context)
            
            # Check if puzzle has any empty cells
            if not has_empty_cells(grid):
                # Grid is completely filled and valid
                context.update({
                    "grid": grid_for_display,
                    "original_cells": original_cells,
                    "is_solved": True
                })
                return render(request, "sudoku_form.html", context)
            
            # Try to solve the puzzle
            grid_copy = [row[:] for row in grid]
            
            if solve(grid_copy):
                # Solution found - update display grid with solved values
                for i in range(9):
                    for j in range(9):
                        grid_for_display[i][j] = grid_copy[i][j]
                
                context.update({
                    "grid": grid_for_display,
                    "original_cells": original_cells,
                    "is_solved": True
                })
            else:
                # No solution exists - keep original input displayed
                context.update({
                    "grid": grid_for_display,
                    "original_cells": original_cells,
                    "error": "This Sudoku puzzle has no solution. Please check your input and try again."
                })
                
        except Exception as e:
            context["error"] = f"Error processing puzzle: {str(e)}"
    
    return render(request, "sudoku_form.html", context)

def sudoku_explanation_view(request):
    return render(request, 'sudoku_explanation.html')