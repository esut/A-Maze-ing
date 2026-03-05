from collections import deque
from typing import List, Tuple


def solve_maze(
    maze: List[List[int]],
    start: Tuple[int, int],
    end: Tuple[int, int],
) -> str:

    width = len(maze[0])
    height = len(maze)

    moves = {
        "N": (0, -1, 1),
        "E": (1, 0, 2),
        "S": (0, 1, 4),
        "W": (-1, 0, 8),
    }

    queue = deque([(start, "")])
    visited = set()

    while queue:

        (x, y), path = queue.popleft()

        if (x, y) == end:
            return path

        if (x, y) in visited:
            continue

        visited.add((x, y))

        for direction, (dx, dy, wall) in moves.items():

            if maze[y][x] & wall == 0:
                continue

            nx = x + dx
            ny = y + dy

            if 0 <= nx < width and 0 <= ny < height:
                queue.append(((nx, ny), path + direction))

    return ""