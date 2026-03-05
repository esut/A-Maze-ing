import sys

from maze.config_parser import parse_config
from maze.maze_generator import MazeGenerator
from maze.maze_solver import solve_maze
from maze.maze_writer import write_maze
from maze.display import display_maze


def main():

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config = parse_config(sys.argv[1])

    gen = MazeGenerator(config["WIDTH"], config["HEIGHT"])

    maze = gen.generate()

    path = solve_maze(maze, config["ENTRY"], config["EXIT"])

    write_maze(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"],
        path
    )

    display_maze(maze)


if __name__ == "__main__":
    main()