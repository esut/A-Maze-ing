"""
Maze package
Provides tools to generate, solve and display mazes.
"""

from typing import List
from .maze_generator import (
    MazeGenerator,
    generate_maze,
    embed_42_pattern,
    find_shortest_path
)
from .maze_solver import solve_maze

__all__: List[str] = [
    "MazeGenerator",
    "generate_maze",
    "embed_42_pattern",
    "find_shortest_path",
    "solve_maze",
]
