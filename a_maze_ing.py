import sys
from maze.config_parser import parse_config
from maze.maze_generator import MazeGenerator
from maze.maze_solver import solve_maze
from maze.maze_writer import write_maze
from maze.display import display_maze


def validate_config(config: dict) -> None:
    """
    Validate configuration values.
    """

    width = config["WIDTH"]
    height = config["HEIGHT"]

    entry = config["ENTRY"]
    exit = config["EXIT"]

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive integers")

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError("ENTRY coordinates are outside the maze")

    if not (0 <= exit[0] < width and 0 <= exit[1] < height):
        raise ValueError("EXIT coordinates are outside the maze")

    if entry == exit:
        raise ValueError("ENTRY and EXIT must be different")


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        config = parse_config(config_file)

        validate_config(config)

        seed = config.get("SEED", None)

        generator = MazeGenerator(
            config["WIDTH"],
            config["HEIGHT"],
            seed
        )

        maze = generator.generate()

        path = solve_maze(
            maze,
            config["ENTRY"],
            config["EXIT"]
        )

        write_maze(
            config["OUTPUT_FILE"],
            maze,
            config["ENTRY"],
            config["EXIT"],
            path
        )

        print("\nMaze generated successfully\n")

        display_maze(maze)

        print("\nShortest path:", path)

    except FileNotFoundError:
        print(f"Error: file '{config_file}' not found")

    except ValueError as e:
        print("Configuration error:", e)

    except KeyError as e:
        print(f"Missing configuration key: {e}")

    except Exception as e:
        print("Unexpected error:", e)


if __name__ == "__main__":
    main()