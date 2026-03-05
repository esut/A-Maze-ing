import random


class MazeGenerator:
    """
    Generate a maze using recursive backtracking.
    """

    def __init__(self, width: int, height: int, seed: int | None = None):
        self.width = width
        self.height = height

        if seed is not None:
            random.seed(seed)

        self.maze = [[15 for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]

    def generate(self) -> list[list[int]]:
        self._dfs(0, 0)
        return self.maze

    def _dfs(self, x: int, y: int):

        self.visited[y][x] = True

        directions = [
            (0, -1, 1, 4),   # N
            (1, 0, 2, 8),    # E
            (0, 1, 4, 1),    # S
            (-1, 0, 8, 2)    # W
        ]

        random.shuffle(directions)

        for dx, dy, wall, opposite in directions:

            nx = x + dx
            ny = y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height:

                if not self.visited[ny][nx]:

                    self.maze[y][x] &= ~wall
                    self.maze[ny][nx] &= ~opposite

                    self._dfs(nx, ny)