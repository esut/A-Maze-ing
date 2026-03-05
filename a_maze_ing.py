import sys

from maze import (
    parse_config,
    MazeGenerator,
    solve_maze,
    write_maze,
)

from maze.display import display_maze


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config = parse_config(sys.argv[1])

    width = config["WIDTH"]
    height = config["HEIGHT"]
    seed = config["SEED"]

    entry = config["ENTRY"]
    exit = config["EXIT"]

    generator = MazeGenerator(width, height, seed)

    maze = generator.generate()

    path = solve_maze(maze, entry, exit)

    write_maze(maze, config["OUTPUT_FILE"], path)

    display_maze(maze)


if __name__ == "__main__":
    main()