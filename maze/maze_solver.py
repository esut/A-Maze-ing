from collections import deque


def solve_maze(maze, start, end):

    height = len(maze)
    width = len(maze[0])

    queue = deque([(start, "")])
    visited = set([start])

    directions = [
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

            nx = x + dx
            ny = y + dy

            if (nx, ny) not in visited:

                visited.add((nx, ny))
                queue.append(((nx, ny), path + letter))

    return ""