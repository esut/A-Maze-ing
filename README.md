# A-Maze-ing

*This project has been created as part of the 42 curriculum by mosiraj-, yafakihi.*

## Description

A-Maze-ing is a Python maze generator that creates random, perfect mazes using the DFS recursive backtracker algorithm. It outputs mazes in hexadecimal format and provides interactive terminal visualization with curses. The project includes a "42" pattern embedded in each maze and offers a reusable module for integration into other projects.

## Instructions

### Prerequisites

- Python 3.10+
- Unix-like terminal with curses support

### Installation

```bash
make install
```

### Running

```bash
make run
# or
python3 a_maze_ing.py config.txt
```

### Interactive Controls

- **R**: Generate new maze
- **P**: Show/hide path
- **C**: Change color theme
- **4**: Show/hide "42" pattern
- **Q**: Quit

### Other Commands

```bash
make debug      # Run with debugger
make clean      # Remove temporary files
make lint       # Run code quality checks
make lint-strict # Run strict type checking
```

## Configuration File Format

The configuration file uses `KEY=VALUE` format. Lines starting with `#` are comments.

### Required Keys

```ini
WIDTH=20              # Maze width in cells
HEIGHT=20             # Maze height in cells
ENTRY=0,0             # Entry coordinates (x,y)
EXIT=19,19            # Exit coordinates (x,y)
OUTPUT_FILE=maze.txt  # Output file path
PERFECT=True          # Generate perfect maze (True/False)
```

### Optional Keys

```ini
SEED=42               # Random seed for reproducibility
```

### Output File Format

Each cell is encoded as a hexadecimal digit (0-F) representing walls:
- Bit 0 (1): North wall
- Bit 1 (2): East wall
- Bit 2 (4): South wall
- Bit 3 (8): West wall

Example: `f` = all walls closed, `0` = all walls open

File structure:
1. Maze grid (hex digits, one row per line)
2. Empty line
3. Entry coordinates
4. Exit coordinates
5. Solution path (N/E/S/W directions)

## Maze Generation Algorithm

### Algorithm: DFS Recursive Backtracker

The algorithm starts with all walls closed and carves passages by:
1. Starting at a random cell
2. Randomly selecting an unvisited neighbor
3. Removing the wall between cells
4. Recursively visiting the neighbor
5. Backtracking when no unvisited neighbors remain

### Why This Algorithm?

**Advantages:**
- Naturally generates perfect mazes (one path between any two points)
- Simple and elegant implementation
- Creates long, winding corridors
- Memory efficient
- Deterministic with seeds

**Trade-offs:**
- Biased toward long corridors
- Can hit recursion limits on very large mazes
- Not uniformly random

**Alternatives considered:** Prim's (more uniform but slower), Kruskal's (better for parallel processing), Recursive Division (faster but more regular patterns).

## Package Installation

### Install via pip

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Run after installation

```bash
mazegen
# or with a custom config
mazegen config.txt
```

## Code Reusability

### Reusable Module

The `maze` package can be imported into other projects:

```python
from maze import MazeGenerator

# Basic usage
gen = MazeGenerator(width=20, height=15, seed=42)
maze = gen.generate(entry=(0, 0), exit_=(19, 14))
path = gen.get_solution()  # Returns list of (x, y) tuples
```

### Available Functions

- `MazeGenerator` class: Main interface
- `generate_maze()`: Low-level maze generation
- `find_shortest_path()`: BFS pathfinding
- `solve_maze()`: Returns path as direction string
- `embed_42_pattern()`: Embeds the 42 pattern
- `get_42_cells()`: Returns 42 pattern coordinates

### Maze Data Structure

Maze is a 2D list of integers (bitmasks):

```python
has_north_wall = maze[y][x] & 1
has_east_wall = maze[y][x] & 2
has_south_wall = maze[y][x] & 4
has_west_wall = maze[y][x] & 8
```

## Team and Project Management

### Team

**yafakihi** (solo developer): All aspects of the project

### Planning

**Initial Plan:**
1. Week 1: Research algorithms and design
2. Week 2: Implement DFS algorithm
3. Week 3: Add file I/O
4. Week 4: Implement visualization
5. Week 5: Add 42 pattern and documentation

**Evolution:**
- Extra time spent on algorithm research
- Additional work on 42 pattern path connectivity
- Added comprehensive type hints (not initially planned)
- Enhanced error handling in config parser

### What Worked Well

- Modular design made development easier
- Incremental development allowed thorough testing
- Type hints caught bugs early
- External configuration simplified testing
- Interactive display aided debugging

### What Could Be Improved

- Should have written unit tests earlier
- Could add more maze validation (corridor width, open areas)
- Performance issues on large mazes (>100x100)
- Could automate package building

### Tools Used

- Python 3.10+, mypy, flake8, curses, pdb, Git, Make

## Resources

### Classic References

- **"Mazes for Programmers" by Jamis Buck**: https://pragprog.com/titles/jbmaze/
- **Think Labyrinth**: http://www.astrolog.org/labyrnth/algrithm.htm
- **Wikipedia - Maze Generation**: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- **Python curses**: https://docs.python.org/3/library/curses.html
- **Python typing**: https://docs.python.org/3/library/typing.html
- **PEP 257 - Docstrings**: https://peps.python.org/pep-0257/

### AI Usage

**Tasks AI Assisted With:**
- Algorithm research and comparison
- Adding comprehensive type hints for mypy strict checking
- Error handling improvements in config parser
- Code review for bugs and best practices
- README structure and formatting
- Writing docstrings following PEP 257
- Identifying edge cases for testing

**What Was NOT AI-Generated:**
- Core algorithm implementation (DFS, BFS)
- 42 pattern design and embedding logic
- Architecture and design decisions
- Problem-solving and bug fixes

**AI Tools Used:**
- Amazon Q Developer (primary assistant)
- GitHub Copilot (code completion)

All AI-generated content was reviewed, understood, tested, and modified to fit project requirements. The developer takes full responsibility for all code.

## License

This project is part of the 42 school curriculum.
