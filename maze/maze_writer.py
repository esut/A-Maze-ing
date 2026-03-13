from typing import List, Tuple


def write_maze(
        filename: str,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        path: str) -> None:
    """Write the maze to a file in hexadecimal format.

    Args:
        filename: Output file path
        maze: 2D grid where each cell is a bitmask of walls
        entry: Entry coordinates (x, y)
        exit: Exit coordinates (x, y)
        path: Solution path as a string of directions
    """
    with open(filename, "w") as f:

        for row in maze:
            line: str = "".join(format(cell, "x") for cell in row)
            f.write(line + "\n")

        f.write("\n")

        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write(path + "\n")
