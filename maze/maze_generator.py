import sys
import random
from collections import deque
from typing import List, Tuple, Optional, Dict, Set

# Each cell stores which walls are closed as 4 bits
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

OPPOSITE: Dict[int, int] = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}

MOVES: List[Tuple[int, int, int]] = [
    (0, -1, NORTH),
    (1,  0, EAST),
    (0,  1, SOUTH),
    (-1, 0, WEST),
]


def generate_maze(width: int, height: int, entry: Tuple[int, int], exit_: Tuple[int, int], seed: Optional[int] = None) -> List[List[int]]:
    """Generate a maze using DFS (recursive backtracker).

    Every cell starts with all 4 walls closed (value 15).
    The algorithm carves passages by removing shared walls.
    Returns a 2D grid where each cell is a bitmask (0-15).
    
    Args:
        width: Maze width in cells
        height: Maze height in cells
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        seed: Random seed for reproducibility
    
    Returns:
        2D list of integers representing wall bitmasks
    """
    rng: random.Random = random.Random(seed)

    maze: List[List[int]] = [[15] * width for _ in range(height)]
    visited: List[List[bool]] = [[False] * width for _ in range(height)]

    def carve(x: int, y: int) -> None:
        visited[y][x] = True
        dirs: List[Tuple[int, int, int]] = MOVES[:]
        rng.shuffle(dirs)
        for dx, dy, wall in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                maze[y][x]   &= ~wall
                maze[ny][nx] &= ~OPPOSITE[wall]
                carve(nx, ny)

    sys.setrecursionlimit(width * height * 2 + 100)
    carve(0, 0)

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


def find_shortest_path(maze: List[List[int]], entry: Tuple[int, int], exit_: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Find the shortest path from entry to exit using BFS.

    Args:
        maze: 2D grid where each cell is a bitmask of walls
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
    
    Returns:
        List of (x, y) cells forming the path, or None if no path exists
    """
    height: int = len(maze)
    width: int = len(maze[0])
    ex, ey = entry
    fx, fy = exit_

    visited: List[List[bool]] = [[False] * width for _ in range(height)]
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(ex, ey): None}
    queue: deque[Tuple[int, int]] = deque([(ex, ey)])
    visited[ey][ex] = True

    while queue:
        cx, cy = queue.popleft()

        if (cx, cy) == (fx, fy):
            path: List[Tuple[int, int]] = []
            cur: Optional[Tuple[int, int]] = (fx, fy)
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


def get_42_cells(width: int, height: int) -> List[Tuple[int, int]]:
    """Return the cells that form '42' centered in the maze.

    Args:
        width: Maze width in cells
        height: Maze height in cells
    
    Returns:
        List of (x, y) coordinates, or empty list if maze is too small
    """
    if width < 9 or height < 7:
        return []

    ox: int = (width  - 7) // 2
    oy: int = (height - 5) // 2

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
        cells.append((ox + 4 + dx, oy + dy))  # '2' is 4 columns right of '4'

    return [(x, y) for x, y in cells if 0 <= x < width and 0 <= y < height]


def embed_42_pattern(maze: List[List[int]], width: int, height: int, entry: Tuple[int, int], exit_: Tuple[int, int]) -> bool:
    """Stamp '42' into the maze and fix the path if it got broken.

    Args:
        maze: 2D grid where each cell is a bitmask of walls
        width: Maze width in cells
        height: Maze height in cells
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
    
    Returns:
        True if pattern was placed, False if maze is too small
    """
    cells: List[Tuple[int, int]] = get_42_cells(width, height)
    if not cells:
        return False

    blocked: Set[Tuple[int, int]] = set(cells)

    for x, y in cells:
        maze[y][x] = 15
        if y > 0:          maze[y-1][x] |= SOUTH
        if y < height - 1: maze[y+1][x] |= NORTH
        if x > 0:          maze[y][x-1] |= EAST
        if x < width - 1:  maze[y][x+1] |= WEST

    if find_shortest_path(maze, entry, exit_) is not None:
        return True


    entry_x, entry_y = entry
    exit_x,  exit_y  = exit_

    for r in range(height - 1):
        maze[r][0]     &= ~SOUTH
        maze[r + 1][0] &= ~NORTH

    for x in range(entry_x):
        if (x, entry_y) not in blocked and (x + 1, entry_y) not in blocked:
            maze[entry_y][x]     &= ~EAST
            maze[entry_y][x + 1] &= ~WEST

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

    def __init__(self, width: int, height: int, seed: Optional[int] = None) -> None:
        """Initialize the maze generator.
        
        Args:
            width: Maze width in cells
            height: Maze height in cells
            seed: Random seed for reproducibility
        """
        self.width: int = width
        self.height: int = height
        self.seed: Optional[int] = seed
        self.maze: Optional[List[List[int]]] = None
        self.entry: Tuple[int, int] = (0, 0)
        self.exit_: Tuple[int, int] = (width - 1, height - 1)

    def generate(self, entry: Tuple[int, int] = (0, 0), exit_: Optional[Tuple[int, int]] = None, perfect: bool = True) -> List[List[int]]:
        """Generate a new maze and embed the '42' pattern.
        
        Args:
            entry: Entry coordinates (x, y)
            exit_: Exit coordinates (x, y), defaults to bottom-right
            perfect: Whether to generate a perfect maze
        
        Returns:
            2D list of integers representing wall bitmasks
        """
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)
        self.entry = entry
        self.exit_ = exit_
        self.maze = generate_maze(self.width, self.height, entry, exit_, self.seed)
        embed_42_pattern(self.maze, self.width, self.height, entry, exit_)
        return self.maze

    def get_solution(self) -> Optional[List[Tuple[int, int]]]:
        """Return the shortest path in the current maze.
        
        Returns:
            List of (x, y) cells forming the path, or None if no maze generated
        """
        if self.maze is None:
            return None
        return find_shortest_path(self.maze, self.entry, self.exit_)