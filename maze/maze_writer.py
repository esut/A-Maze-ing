from typing import List


def write_maze(
    maze: List[List[int]],
    filename: str,
    path: str,
) -> None:

    with open(filename, "w") as f:

        for row in maze:
            line = " ".join(format(cell, "x") for cell in row)
            f.write(line + "\n")

        f.write("\nPATH=" + path + "\n")