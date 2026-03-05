from typing import List


def display_maze(maze: List[List[int]]) -> None:

    height = len(maze)
    width = len(maze[0])

    for y in range(height):

        line = ""

        for x in range(width):
            line += "[]"

        print(line)