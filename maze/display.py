import curses
import random
from typing import List, Tuple, Set, Any, Optional

from .maze_generator import (
    NORTH, EAST, SOUTH, WEST,
    generate_maze,
    embed_42_pattern,
    find_shortest_path,
    get_42_cells,
)

# Color pair IDs
WALL: int = 1
PATH: int = 2
ENTRY: int = 3
EXIT: int = 4
C42: int = 5
MENU: int = 6
BG: int = 7

# Wall color themes (foreground, background)
THEMES: List[Tuple[int, int]] = [
    (curses.COLOR_WHITE, curses.COLOR_BLACK),
    (curses.COLOR_YELLOW, curses.COLOR_BLACK),
    (curses.COLOR_GREEN, curses.COLOR_BLACK),
    (curses.COLOR_CYAN, curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_RED, curses.COLOR_BLACK),
    (curses.COLOR_BLUE, curses.COLOR_BLACK),
]
THEME_NAMES: List[str] = [
    "White", "Yellow", "Green", "Cyan", "Magenta", "Red", "Blue"
]

# BONUS 1: Color options for the '42' pattern
C42_COLORS: List[Tuple[int, int]] = [
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_YELLOW, curses.COLOR_BLACK),
    (curses.COLOR_RED, curses.COLOR_BLACK),
    (curses.COLOR_CYAN, curses.COLOR_BLACK),
    (curses.COLOR_GREEN, curses.COLOR_BLACK),
    (curses.COLOR_BLUE, curses.COLOR_BLACK),
    (curses.COLOR_WHITE, curses.COLOR_BLACK),
]
C42_COLOR_NAMES: List[str] = [
    "Magenta", "Yellow", "Red", "Cyan", "Green", "Blue", "White"
]


def init_colors(theme: int, c42_theme: int) -> None:
    """Set up curses colors for the chosen wall theme and '42' color.

    Args:
        theme: Wall color theme index
        c42_theme: '42' pattern color index
    """
    fg, bg = THEMES[theme % len(THEMES)]
    c42_fg, c42_bg = C42_COLORS[c42_theme % len(C42_COLORS)]
    curses.init_pair(WALL, fg, bg)
    curses.init_pair(PATH, curses.COLOR_CYAN, bg)
    curses.init_pair(ENTRY, curses.COLOR_GREEN, bg)
    curses.init_pair(EXIT, curses.COLOR_RED, bg)
    curses.init_pair(C42, c42_fg, c42_bg)
    curses.init_pair(MENU, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(BG, curses.COLOR_BLACK, bg)


def draw_maze(
        scr: Any,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_set: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> None:
    """Draw the maze on the terminal screen.

    Args:
        scr: Curses screen object
        maze: 2D grid where each cell is a bitmask of walls
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        path_set: Set of cells in the solution path
        cells_42: Set of cells forming the '42' pattern
    """
    height: int = len(maze)
    width: int = len(maze[0])
    wall_col: int = curses.color_pair(WALL)
    bg_col: int = curses.color_pair(BG)

    for y in range(height):
        for x in range(width):
            cell: int = maze[y][x]
            row: int = y * 2
            col: int = x * 4

            pos: Tuple[int, int] = (x, y)
            ch: str
            color: int
            if pos == entry:
                ch = "E"
                color = curses.color_pair(ENTRY) | curses.A_BOLD
            elif pos == exit_:
                ch = "X"
                color = curses.color_pair(EXIT) | curses.A_BOLD
            elif pos in path_set:
                ch, color = ".", curses.color_pair(PATH)
            elif pos in cells_42:
                ch = "#"
                color = curses.color_pair(C42) | curses.A_BOLD
            else:
                ch, color = " ", bg_col

            top: str = "---" if (cell & NORTH) else "   "
            left: str = "|" if (cell & WEST) else " "

            try:
                scr.addstr(row, col, "+", wall_col)
                scr.addstr(row, col + 1, top, wall_col)
                scr.addstr(row + 1, col, left, wall_col)
                scr.addstr(row + 1, col + 1, f" {ch} ", color)
            except curses.error:
                pass

        try:
            right: str = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2, width * 4, "+", wall_col)
            scr.addstr(y * 2 + 1, width * 4, right, wall_col)
        except curses.error:
            pass

    for x in range(width):
        bot: str = "---" if (maze[height - 1][x] & SOUTH) else "   "
        try:
            scr.addstr(height * 2, x * 4, "+", wall_col)
            scr.addstr(height * 2, x * 4 + 1, bot, wall_col)
        except curses.error:
            pass
    try:
        scr.addstr(height * 2, width * 4, "+", wall_col)
    except curses.error:
        pass


def draw_menu(
        scr: Any,
        row: int,
        show_path: bool,
        show_42: bool,
        theme: int,
        c42_theme: int,
        path_len: int,
        width: int,
        height: int,
        seed: Optional[int],
        maze_count: int) -> None:
    """Draw the keyboard controls and info below the maze.

    Args:
        scr: Curses screen object
        row: Row position to draw the menu
        show_path: Whether path is currently shown
        show_42: Whether '42' pattern is currently shown
        theme: Current wall theme index
        c42_theme: Current '42' color index
        path_len: Length of the shortest path (0 = no path)
        width: Maze width in cells
        height: Maze height in cells
        seed: Current random seed (None if not set)
        maze_count: How many mazes have been generated so far
    """
    p: str = "Hide" if show_path else "Show"
    f42: str = "Hide 42" if show_42 else "Show 42"
    col_name: str = THEME_NAMES[theme % len(THEME_NAMES)]
    c42_name: str = C42_COLOR_NAMES[c42_theme % len(C42_COLOR_NAMES)]

    try:
        scr.addstr(row, 0, " === A-Maze-ing === ",
                   curses.color_pair(MENU))

        # Line 1: main controls
        line1 = (
            f" [R]New  [P]{p}Path  [C]Color:{col_name}"
            f"  [4]{f42}  [K]42Color:{c42_name}  [Q]Quit "
        )
        scr.addstr(row + 1, 0, line1, curses.color_pair(WALL))

        # BONUS 2: maze info line (size, seed, generation count)
        seed_str = str(seed) if seed is not None else "random"
        info = (
            f" Size:{width}x{height}  Seed:{seed_str}"
            f"  Maze#{maze_count}"
        )
        # BONUS 3: path length
        if path_len > 0:
            info += f"  PathLen:{path_len}"
        else:
            info += "  PathLen:N/A"

        scr.addstr(row + 2, 0, info, curses.color_pair(WALL))

        # BONUS 4: save hint
        scr.addstr(row + 3, 0,
                   " [S]Save maze to file ",
                   curses.color_pair(WALL))
    except curses.error:
        pass


def save_maze_to_file(
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        seed: Optional[int],
        maze_count: int) -> str:
    """Save the current maze as a text file.

    The file is named 'maze_<seed>_<count>.txt'.

    Args:
        maze: 2D grid of wall bitmasks
        entry: Entry coordinates
        exit_: Exit coordinates
        seed: Current seed value
        maze_count: Generation counter

    Returns:
        The filename that was written
    """
    seed_str = str(seed) if seed is not None else "rnd"
    filename: str = f"maze_{seed_str}_{maze_count}.txt"

    from .maze_writer import write_maze
    from .maze_solver import solve_maze

    path_str: str = solve_maze(maze, entry, exit_)
    write_maze(filename, maze, entry, exit_, path_str)
    return filename


def display_maze(
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        width: int,
        height: int,
        perfect: bool = True,
        seed: Optional[int] = None) -> None:
    """Show the maze in the terminal with keyboard controls.

    Keys:
        R = generate a new random maze
        P = show / hide the shortest path
        C = cycle wall color theme
        4 = show / hide the '42' pattern
        K = cycle the '42' pattern color  (BONUS 1)
        S = save current maze to a .txt file  (BONUS 4)
        Q = quit

    The status bar shows maze size, seed, generation counter,
    and path length.  (BONUS 2 & 3)

    Args:
        maze: 2D grid where each cell is a bitmask of walls
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        width: Maze width in cells
        height: Maze height in cells
        perfect: Whether maze should be perfect
        seed: Random seed for reproducibility
    """
    def run(scr: Any) -> None:
        nonlocal maze, seed

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        theme: int = 0
        c42_theme: int = 0          # BONUS 1: '42' color index
        show_path: bool = False
        show_42: bool = False
        maze_count: int = 1         # BONUS 2: generation counter
        init_colors(theme, c42_theme)

        path: Optional[List[Tuple[int, int]]]
        path = find_shortest_path(maze, entry, exit_)
        path_len: int = len(path) if path else 0  # BONUS 3

        status_msg: str = ""        # BONUS 4: save feedback message

        while True:
            scr.clear()
            max_y: int
            _: int
            max_y, _ = scr.getmaxyx()

            path_set: Set[Tuple[int, int]]
            if path and show_path:
                path_set = set(path)
            else:
                path_set = set()

            c42_set: Set[Tuple[int, int]]
            if show_42:
                c42_set = set(get_42_cells(width, height))
            else:
                c42_set = set()

            draw_maze(scr, maze, entry, exit_, path_set, c42_set)

            menu_row: int = height * 2 + 2
            if menu_row + 4 < max_y:
                draw_menu(
                    scr, menu_row,
                    show_path, show_42,
                    theme, c42_theme,
                    path_len, width, height,
                    seed, maze_count
                )

            # Show save feedback message (BONUS 4)
            if status_msg and menu_row + 5 < max_y:
                try:
                    scr.addstr(menu_row + 4, 0,
                               f" {status_msg} ",
                               curses.color_pair(ENTRY))
                except curses.error:
                    pass

            scr.refresh()

            key: int = scr.getch()
            ch: str = chr(key).upper() if 0 <= key < 256 else ""
            status_msg = ""  # clear previous message

            if ch == "Q":
                break

            elif ch == "R":
                seed = random.randint(0, 999999)
                maze = generate_maze(width, height, entry, exit_, seed)
                embed_42_pattern(maze, width, height, entry, exit_)
                path = find_shortest_path(maze, entry, exit_)
                path_len = len(path) if path else 0
                maze_count += 1

            elif ch == "P":
                show_path = not show_path

            elif ch == "C":
                theme = (theme + 1) % len(THEMES)
                init_colors(theme, c42_theme)

            elif ch == "4":
                show_42 = not show_42

            elif ch == "K":
                # BONUS 1: cycle '42' pattern color
                c42_theme = (c42_theme + 1) % len(C42_COLORS)
                init_colors(theme, c42_theme)

            elif ch == "S":
                # BONUS 4: save maze to file
                filename = save_maze_to_file(
                    maze, entry, exit_, seed, maze_count
                )
                status_msg = f"Saved to {filename}"

    curses.wrapper(run)