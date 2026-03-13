from typing import List, Tuple, Set
from collections import deque


def solve_maze(
        maze: List[List[int]],
        start: Tuple[int, int],
        end: Tuple[int, int]) -> str:
    """Solve the maze using BFS and return the path as a string.

    Args:
        maze: 2D grid where each cell is a bitmask of walls
        start: Starting coordinates (x, y)
        end: Ending coordinates (x, y)

    Returns:
        String of directions (N, E, S, W) or empty string if no path
    """
    height: int = len(maze)
    width: int = len(maze[0])

    queue: deque[Tuple[Tuple[int, int], str]] = deque([(start, "")])
    visited: Set[Tuple[int, int]] = set([start])

    directions: List[Tuple[int, int, int, str]] = [
        (0, -1, 1, "N"),
        (1, 0, 2, "E"),
        (0, 1, 4, "S"),
        (-1, 0, 8, "W")
    ]

    while queue:

        (x, y), path = queue.popleft()

        if (x, y) == end:
            return path

        for dx, dy, wall, letter in directions:

            if maze[y][x] & wall:
                continue

            nx: int = x + dx
            ny: int = y + dy

            if (0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in visited):

                visited.add((nx, ny))
                queue.append(((nx, ny), path + letter))

    return ""
