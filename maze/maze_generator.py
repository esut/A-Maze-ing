import random
from typing import List


class MazeGenerator:

    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width = width
        self.height = height
        random.seed(seed)

    def generate(self) -> List[List[int]]:
        maze = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):

                if x < self.width - 1:
                    if random.choice([True, False]):
                        maze[y][x] |= 2
                        maze[y][x + 1] |= 8

                if y < self.height - 1:
                    if random.choice([True, False]):
                        maze[y][x] |= 4
                        maze[y + 1][x] |= 1

        return maze