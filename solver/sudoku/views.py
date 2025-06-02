from django.shortcuts import render

def parse_grid(request):
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            val = request.POST.get(f'cell_{i}_{j}', '')
            row.append(int(val) if val.isdigit() else 0)
        grid.append(row)
    return grid

def get_possible(grid, row, col):
    return set(range(1, 10)) - {
        *grid[row],
        *[grid[i][col] for i in range(9)],
        *[grid[r][c] for r in range(row//3*3, row//3*3+3) for c in range(col//3*3, col//3*3+3)]
    }

def find_mrv(grid):
    min_possibilities = 10
    best_cell = None
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                possibilities = get_possible(grid, i, j)
                if len(possibilities) < min_possibilities:
                    min_possibilities = len(possibilities)
                    best_cell = (i, j, possibilities)
                    if min_possibilities == 1:
                        return best_cell
    return best_cell

def solve(grid):
    mrv = find_mrv(grid)
    if not mrv:
        return True
    row, col, candidates = mrv
    for num in candidates:
        grid[row][col] = num
        if solve(grid):
            return True
        grid[row][col] = 0
    return False

def flatten_grid(grid):             
    #2D to grid format
    return {f"cell_{i}_{j}": grid[i][j] if grid[i][j] != 0 else '' for i in range(9) for j in range(9)}

def sudoku_view(request):
    #empty grid
    grid_for_display = [['' for _ in range(9)] for _ in range(9)]
    original_cells = set()
    
    context = {
        "grid": grid_for_display,
        "original_cells": original_cells,
        "error": None,
        "is_solved": False
    }

    if request.method == "POST":
        try:
            grid = parse_grid(request)
            original_grid = [row[:] for row in grid]
            
            # Track which cells had original values
            for i in range(9):
                for j in range(9):
                    if grid[i][j] != 0:
                        original_cells.add(f"{i}_{j}")
            
            grid_copy = [row[:] for row in grid]

            if solve(grid_copy):
                for i in range(9):
                    for j in range(9):
                        grid_for_display[i][j] = grid_copy[i][j] if grid_copy[i][j] != 0 else ''
                
                context["grid"] = grid_for_display
                context["original_cells"] = original_cells
                context["is_solved"] = True
            else:
                # Show original puzzle on failure
                for i in range(9):
                    for j in range(9):
                        grid_for_display[i][j] = original_grid[i][j] if original_grid[i][j] != 0 else ''
                
                context["grid"] = grid_for_display
                context["error"] = "This Sudoku puzzle is unsolvable!"
        except Exception as e:
            context["error"] = f"Error processing puzzle: {str(e)}"

    return render(request, "sudoku_form.html", context)