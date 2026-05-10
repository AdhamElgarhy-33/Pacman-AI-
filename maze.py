"""
maze.py
-------
The maze layout and a helper that converts it into:
    - a 2D grid where 1 = wall, 0 = open path
    - a set of (row, col) tiles where food pellets sit
Member 1 (Game Engine) owns this file.

Symbols:
    '#' = wall
    '.' = open path with a food pellet on it
    ' ' = open path with no food (used for spawn tiles)
"""

RAW_MAZE = [
    "########################",
    "#..........##..........#",
    "#.####.###.##.###.####.#",
    "#......................#",
    "#.##.###.######.###.##.#",
    "#....##............##..#",
    "######.##.####.##.######",
    "#......##......##......#",
    "#.##.###.######.###.##.#",
    "#......................#",
    "#.####.###.##.###.####.#",
    "#..........##..........#",
    "########################",
]


def parse_maze():
    """
    Returns:
        grid           : 2D list of ints (1 = wall, 0 = path)
        food_positions : set of (row, col) tuples where pellets are placed
    """
    grid = []
    food_positions = set()

    for r, row in enumerate(RAW_MAZE):
        grid_row = []
        for c, ch in enumerate(row):
            if ch == '#':
                grid_row.append(1)
            else:
                grid_row.append(0)
                if ch == '.':
                    food_positions.add((r, c))
        grid.append(grid_row)

    return grid, food_positions
