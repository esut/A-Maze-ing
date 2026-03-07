"""Maze generation, '42' pattern embedding, and shortest path solver."""

import sys
import random
from collections import deque
from typing import List, Tuple, Optional

# Wall bit flags (bitmask per cell)
NORTH = 1   # bit 0
EAST  = 2   # bit 1
SOUTH = 4   # bit 2
WEST  = 8   # bit 3

OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
DIRECTIONS = [
    (0, -1, NORTH),
    (1,  0, EAST),
    (0,  1, SOUTH),
    (-1, 0, WEST),
]


# ---------------------------------------------------------------------------
# Maze generation
# ---------------------------------------------------------------------------

def generate_maze(
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
    perfect: bool = True,
    seed: Optional[int] = None,
) -> List[List[int]]:
    """Generate a maze using the recursive backtracker (DFS) algorithm.

    Every cell starts with all 4 walls closed (value 15).
    The DFS carves passages by removing shared walls between neighbours,
    guaranteeing full connectivity.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) entry cell — its outer border wall is opened.
        exit_: (x, y) exit cell  — its outer border wall is opened.
        perfect: Unused for now (DFS always produces a perfect maze).
        seed: Random seed for reproducibility. None = random each run.

    Returns:
        2D list[row][col] of integers; each integer is a 4-bit wall mask.
    """
    rng = random.Random(seed)

    # All walls closed
    maze: List[List[int]] = [[15] * width for _ in range(height)]
    visited: List[List[bool]] = [[False] * width for _ in range(height)]

    def carve(cx: int, cy: int) -> None:
        """DFS: visit cx,cy then recurse into unvisited neighbours."""
        visited[cy][cx] = True
        dirs = DIRECTIONS[:]
        rng.shuffle(dirs)
        for dx, dy, wall in dirs:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                maze[cy][cx]  &= ~wall             # open wall on this side
                maze[ny][nx]  &= ~OPPOSITE[wall]   # open matching wall on neighbour
                carve(nx, ny)

    sys.setrecursionlimit(width * height * 2 + 100)
    carve(0, 0)

    # Open the outer border walls at entry and exit
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


# ---------------------------------------------------------------------------
# Shortest path (BFS)
# ---------------------------------------------------------------------------

def find_shortest_path(
    maze: List[List[int]],
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """Return the shortest path from entry to exit using BFS.

    Moves between cells are allowed only when the shared wall is open
    (the corresponding bit in the cell's bitmask is 0).

    Args:
        maze: 2D wall bitmask grid.
        entry: Start cell (x, y).
        exit_: Goal cell (x, y).

    Returns:
        Ordered list of (x, y) cells from entry to exit,
        or None if no path exists.
    """
    height = len(maze)
    width  = len(maze[0]) if height else 0
    ex, ey = entry
    fx, fy = exit_

    visited: List[List[bool]] = [[False] * width for _ in range(height)]
    parent: dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
    queue: deque[Tuple[int, int]] = deque([(ex, ey)])
    visited[ey][ex] = True
    parent[(ex, ey)] = None

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == (fx, fy):
            # Reconstruct path by following parent pointers
            path: List[Tuple[int, int]] = []
            cur: Optional[Tuple[int, int]] = (fx, fy)
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path

        cell = maze[cy][cx]
        for dx, dy, wall in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < width and 0 <= ny < height
                and not visited[ny][nx]
                and not (cell & wall)   # wall is open
            ):
                visited[ny][nx] = True
                parent[(nx, ny)] = (cx, cy)
                queue.append((nx, ny))

    return None


# ---------------------------------------------------------------------------
# '42' pattern
# ---------------------------------------------------------------------------

def get_42_cells(width: int, height: int) -> List[Tuple[int, int]]:
    """Return the list of cells that form the '42' pattern, centered in maze.

    Pattern layout (each letter = one cell):
        4 4 . 4 4   .   2 2 2
        4 . . . 4   .   . . 2
        4 4 . 4 4   .   2 2 2
        . . . . 4   .   2 . .
        . . . . 4   .   2 2 2

    Total bounding box: 7 wide x 5 tall.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        List of (x, y) cells, or [] if the maze is too small.
    """
    pat_w, pat_h = 7, 5
    if width < pat_w + 2 or height < pat_h + 2:
        return []

    # Top-left corner that centers the pattern
    ox = (width  - pat_w) // 2
    oy = (height - pat_h) // 2

    four: List[Tuple[int, int]] = [
        (0, 0), (0, 1), (0, 2),
        (1, 2),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
    ]
    two: List[Tuple[int, int]] = [
        (0, 0), (1, 0), (2, 0),
        (2, 1),
        (0, 2), (1, 2), (2, 2),
        (0, 3),
        (0, 4), (1, 4), (2, 4),
    ]

    cells: List[Tuple[int, int]] = []
    for dx, dy in four:
        cells.append((ox + dx, oy + dy))
    for dx, dy in two:
        cells.append((ox + 4 + dx, oy + dy))   # '2' starts 4 cols after '4'

    return [(x, y) for x, y in cells if 0 <= x < width and 0 <= y < height]


def _close_cell(maze: List[List[int]], x: int, y: int) -> None:
    """Close all 4 walls of cell (x, y) and keep neighbours coherent.

    Args:
        maze: Maze grid modified in-place.
        x: Cell column.
        y: Cell row.
    """
    h, w = len(maze), len(maze[0])
    maze[y][x] = 15                              # close all walls
    if y > 0:          maze[y-1][x] |= SOUTH    # neighbour north
    if y < h - 1:      maze[y+1][x] |= NORTH    # neighbour south
    if x > 0:          maze[y][x-1] |= EAST     # neighbour west
    if x < w - 1:      maze[y][x+1] |= WEST     # neighbour east


def _path_exists(
    maze: List[List[int]],
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
) -> bool:
    """Quick BFS reachability check (no path reconstruction).

    Args:
        maze: Maze grid.
        entry: Start cell.
        exit_: Goal cell.

    Returns:
        True if exit_ is reachable from entry.
    """
    height = len(maze)
    width  = len(maze[0]) if height else 0
    ex, ey = entry
    fx, fy = exit_
    seen: set[Tuple[int, int]] = {(ex, ey)}
    queue: deque[Tuple[int, int]] = deque([(ex, ey)])

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == (fx, fy):
            return True
        cell = maze[cy][cx]
        for dx, dy, wall in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < width and 0 <= ny < height
                and (nx, ny) not in seen
                and not (cell & wall)
            ):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return False


def _fix_connectivity(
    maze: List[List[int]],
    blocked: set[Tuple[int, int]],
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
) -> None:
    """Open a minimal bypass column alongside the '42' block if needed.

    Called only when the '42' block has cut the entry→exit path.
    Opens the south wall of each cell in the bypass column between the
    row above the block and the row below, then links the column
    horizontally to both sides so paths can flow around the block.

    Args:
        maze: Maze grid modified in-place.
        blocked: Set of (x, y) cells in the '42' pattern.
        width: Maze width.
        height: Maze height.
        entry: Entry cell.
        exit_: Exit cell.
    """
    if _path_exists(maze, entry, exit_):
        return   # nothing to fix

    ys = [y for _, y in blocked]
    xs = [x for x, _ in blocked]
    top    = min(ys) - 1 if min(ys) > 0 else max(ys) + 1
    bot    = max(ys) + 1 if max(ys) < height - 1 else min(ys) - 1
    col    = min(xs) - 1 if min(xs) > 0 else max(xs) + 1

    # Carve vertical passage through bypass column
    for r in range(top, bot):
        maze[r][col]     &= ~SOUTH
        maze[r + 1][col] &= ~NORTH

    # Link bypass column eastward and westward at top and bottom rows
    for row in (top, bot):
        if col + 1 < width and (col + 1, row) not in blocked:
            maze[row][col]     &= ~EAST
            maze[row][col + 1] &= ~WEST
        if col - 1 >= 0 and (col - 1, row) not in blocked:
            maze[row][col]     &= ~WEST
            maze[row][col - 1] &= ~EAST

    # Last resort: open the full left or right border column
    if not _path_exists(maze, entry, exit_):
        safe = 0 if min(xs) > 0 else width - 1
        for r in range(height - 1):
            maze[r][safe]     &= ~SOUTH
            maze[r + 1][safe] &= ~NORTH
        for r in (0, height - 1):
            for x in range(width - 1):
                if (x, r) not in blocked and (x + 1, r) not in blocked:
                    maze[r][x]     &= ~EAST
                    maze[r][x + 1] &= ~WEST


class MazeGenerator:
    """Wraps generate_maze() and embed_42_pattern() in a reusable class.

    Example:
        gen = MazeGenerator(20, 15, seed=42)
        maze = gen.generate(entry=(0, 0), exit_=(19, 14))

    Args:
        width: Number of columns.
        height: Number of rows.
        seed: Random seed for reproducibility (None = random).
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
    ) -> None:
        """Initialise the generator with maze dimensions and optional seed."""
        self.width  = width
        self.height = height
        self.seed   = seed
        self.maze:  Optional[List[List[int]]] = None

    def generate(
        self,
        entry: Tuple[int, int] = (0, 0),
        exit_: Optional[Tuple[int, int]] = None,
        perfect: bool = True,
    ) -> List[List[int]]:
        """Generate a new maze, embed '42', and store it in self.maze.

        Args:
            entry: Entry cell (x, y).
            exit_: Exit cell (x, y) — defaults to bottom-right corner.
            perfect: If True, use DFS for a perfect maze.

        Returns:
            2D wall bitmask grid.
        """
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)

        self.maze = generate_maze(
            self.width, self.height, entry, exit_, perfect, self.seed
        )
        embed_42_pattern(self.maze, self.width, self.height, entry, exit_)
        return self.maze

    def get_solution(
        self,
        entry: Tuple[int, int] = (0, 0),
        exit_: Optional[Tuple[int, int]] = None,
    ) -> Optional[List[Tuple[int, int]]]:
        """Return the shortest path in the last generated maze.

        Args:
            entry: Start cell (x, y).
            exit_: Goal cell (x, y) — defaults to bottom-right corner.

        Returns:
            List of (x, y) cells, or None if no maze generated yet.
        """
        if self.maze is None:
            return None
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)
        return find_shortest_path(self.maze, entry, exit_)


def embed_42_pattern(
    maze: List[List[int]],
    width: int,
    height: int,
    entry: Tuple[int, int] = (0, 0),
    exit_: Optional[Tuple[int, int]] = None,
) -> bool:
    """Stamp the '42' pattern into the maze and guarantee a path still exists.

    Steps:
        1. Identify the '42' cells (centered in the maze).
        2. Close all 4 walls of every '42' cell.
        3. If the entry→exit path is now broken, open a narrow bypass.

    Args:
        maze: Maze grid modified in-place.
        width: Maze width.
        height: Maze height.
        entry: Entry cell (default top-left).
        exit_: Exit cell (default bottom-right).

    Returns:
        True if the pattern was placed, False if the maze is too small.
    """
    if exit_ is None:
        exit_ = (width - 1, height - 1)

    cells = get_42_cells(width, height)
    if not cells:
        return False

    blocked: set[Tuple[int, int]] = set(cells)

    for x, y in cells:
        _close_cell(maze, x, y)

    _fix_connectivity(maze, blocked, width, height, entry, exit_)
    return True