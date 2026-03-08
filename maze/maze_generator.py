import sys
import random
from collections import deque

# Each cell stores which walls are closed as 4 bits
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

MOVES = [
    (0, -1, NORTH),
    (1,  0, EAST),
    (0,  1, SOUTH),
    (-1, 0, WEST),
]


def generate_maze(width, height, entry, exit_, seed=None):
    """Generate a maze using DFS (recursive backtracker).

    Every cell starts with all 4 walls closed (value 15).
    The algorithm carves passages by removing shared walls.
    Returns a 2D grid where each cell is a bitmask (0-15).
    """
    rng = random.Random(seed)

    maze    = [[15] * width for _ in range(height)]
    visited = [[False] * width for _ in range(height)]

    def carve(x, y):
        visited[y][x] = True
        dirs = MOVES[:]
        rng.shuffle(dirs)
        for dx, dy, wall in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                maze[y][x]   &= ~wall
                maze[ny][nx] &= ~OPPOSITE[wall]
                carve(nx, ny)

    sys.setrecursionlimit(width * height * 2 + 100)
    carve(0, 0)

    # Open the outer border wall at entry and exit
    ex, ey = entry
    fx, fy = exit_
    if ey == 0:
        maze[ey][ex] &= ~NORTH
    elif ey == height - 1:
        maze[ey][ex] &= ~SOUTH
    if fy == 0:
        maze[fy][fx] &= ~NORTH
    elif fy == height - 1:
        maze[fy][fx] &= ~SOUTH

    return maze


def find_shortest_path(maze, entry, exit_):
    """Find the shortest path from entry to exit using BFS.

    Returns a list of (x, y) cells, or None if no path exists.
    """
    height = len(maze)
    width  = len(maze[0])
    ex, ey = entry
    fx, fy = exit_

    visited = [[False] * width for _ in range(height)]
    parent  = {(ex, ey): None}
    queue   = deque([(ex, ey)])
    visited[ey][ex] = True

    while queue:
        cx, cy = queue.popleft()

        if (cx, cy) == (fx, fy):
            # Rebuild path by following parent links
            path = []
            cur  = (fx, fy)
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path

        for dx, dy, wall in MOVES:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and not visited[ny][nx]
                and not (maze[cy][cx] & wall)
            ):
                visited[ny][nx] = True
                parent[(nx, ny)] = (cx, cy)
                queue.append((nx, ny))

    return None


def get_42_cells(width, height):
    """Return the cells that form '42' centered in the maze.

    Returns [] if the maze is too small to fit the pattern.
    """
    if width < 9 or height < 7:
        return []

    # Center the 7x5 pattern in the maze
    ox = (width  - 7) // 2
    oy = (height - 5) // 2

    four = [
        (0, 0), (0, 1), (0, 2),
        (1, 2),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
    ]
    two = [
        (0, 0), (1, 0), (2, 0),
        (2, 1),
        (0, 2), (1, 2), (2, 2),
        (0, 3),
        (0, 4), (1, 4), (2, 4),
    ]

    cells = []
    for dx, dy in four:
        cells.append((ox + dx, oy + dy))
    for dx, dy in two:
        cells.append((ox + 4 + dx, oy + dy))  # '2' is 4 columns right of '4'

    return [(x, y) for x, y in cells if 0 <= x < width and 0 <= y < height]


def embed_42_pattern(maze, width, height, entry, exit_):
    """Stamp '42' into the maze and fix the path if it got broken.

    Returns True if placed, False if the maze is too small.
    """
    cells = get_42_cells(width, height)
    if not cells:
        return False

    blocked = set(cells)

    # Close all 4 walls of every '42' cell and sync its neighbours
    for x, y in cells:
        maze[y][x] = 15
        if y > 0:          maze[y-1][x] |= SOUTH
        if y < height - 1: maze[y+1][x] |= NORTH
        if x > 0:          maze[y][x-1] |= EAST
        if x < width - 1:  maze[y][x+1] |= WEST

    # If the path still exists, we are done
    if find_shortest_path(maze, entry, exit_) is not None:
        return True

    # Path is broken — carve a guaranteed bypass using column 0
    # (the leftmost column is never part of the '42' block)
    entry_x, entry_y = entry
    exit_x,  exit_y  = exit_

    # 1. Open the full left column top to bottom
    for r in range(height - 1):
        maze[r][0]     &= ~SOUTH
        maze[r + 1][0] &= ~NORTH

    # 2. Open the entry row from column 0 to the entry cell
    for x in range(entry_x):
        if (x, entry_y) not in blocked and (x + 1, entry_y) not in blocked:
            maze[entry_y][x]     &= ~EAST
            maze[entry_y][x + 1] &= ~WEST

    # 3. Open the exit row from column 0 to the exit cell
    for x in range(exit_x):
        if (x, exit_y) not in blocked and (x + 1, exit_y) not in blocked:
            maze[exit_y][x]     &= ~EAST
            maze[exit_y][x + 1] &= ~WEST

    return True


class MazeGenerator:
    """Simple class to generate and solve a maze.

    Example:
        gen  = MazeGenerator(20, 15, seed=42)
        maze = gen.generate(entry=(0, 0), exit_=(19, 14))
        path = gen.get_solution()
    """

    def __init__(self, width, height, seed=None):
        self.width  = width
        self.height = height
        self.seed   = seed
        self.maze   = None
        self.entry  = (0, 0)
        self.exit_  = (width - 1, height - 1)

    def generate(self, entry=(0, 0), exit_=None, perfect=True):
        """Generate a new maze and embed the '42' pattern."""
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)
        self.entry = entry
        self.exit_ = exit_
        self.maze  = generate_maze(self.width, self.height, entry, exit_, self.seed)
        embed_42_pattern(self.maze, self.width, self.height, entry, exit_)
        return self.maze

    def get_solution(self):
        """Return the shortest path in the current maze."""
        if self.maze is None:
            return None
        return find_shortest_path(self.maze, self.entry, self.exit_)