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
    (curses.COLOR_WHITE,   curses.COLOR_BLACK),
    (curses.COLOR_YELLOW,  curses.COLOR_BLACK),
    (curses.COLOR_GREEN,   curses.COLOR_BLACK),
    (curses.COLOR_CYAN,    curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_RED,     curses.COLOR_BLACK),
    (curses.COLOR_BLUE,    curses.COLOR_BLACK),
]
THEME_NAMES: List[str] = [
    "White", "Yellow", "Green", "Cyan", "Magenta", "Red", "Blue"
]


def init_colors(theme: int) -> None:
    """Set up curses color pairs for the chosen theme.

    Args:
        theme: Index into THEMES list
    """
    fg, bg = THEMES[theme % len(THEMES)]
    curses.init_pair(WALL,  fg,                    bg)
    curses.init_pair(PATH,  curses.COLOR_YELLOW,   bg)
    curses.init_pair(ENTRY, curses.COLOR_BLACK,    curses.COLOR_GREEN)
    curses.init_pair(EXIT,  curses.COLOR_BLACK,    curses.COLOR_RED)
    curses.init_pair(C42,   curses.COLOR_MAGENTA,  bg)
    curses.init_pair(MENU,  curses.COLOR_BLACK,    curses.COLOR_WHITE)
    curses.init_pair(BG,    curses.COLOR_BLACK,    bg)


def get_cell_char(
        pos: Tuple[int, int],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_set: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> Tuple[str, int]:
    """Return the character and color to display inside a cell.

    Args:
        pos: Current cell coordinates (x, y)
        entry: Entry coordinates
        exit_: Exit coordinates
        path_set: Set of path cells
        cells_42: Set of 42 pattern cells

    Returns:
        Tuple of (character, curses color attribute)
    """
    if pos in cells_42:
        return "#", curses.color_pair(C42) | curses.A_BOLD
    if pos == entry:
        return "E", curses.color_pair(ENTRY) | curses.A_BOLD
    if pos == exit_:
        return "X", curses.color_pair(EXIT) | curses.A_BOLD
    if pos in path_set:
        return "*", curses.color_pair(PATH) | curses.A_BOLD
    return " ", curses.color_pair(BG)


def draw_cell(
        scr: Any,
        row: int,
        col: int,
        cell: int,
        ch: str,
        color: int,
        wall_col: int,
        is_42: bool) -> None:
    """Draw a single maze cell at the given screen position.

    Each cell occupies 2 rows x 4 columns on screen:
        +---+
        | E |

    Args:
        scr: Curses screen object
        row: Screen row (maze_y * 2)
        col: Screen column (maze_x * 4)
        cell: Bitmask of walls for this cell
        ch: Character to display inside the cell
        color: Curses color attribute for the character
        wall_col: Curses color attribute for walls
        is_42: True if this cell is part of the 42 pattern
    """
    top = "---" if (cell & NORTH) and not is_42 else "   "
    left = "|" if (cell & WEST) and not is_42 else " "
    try:
        scr.addstr(row,     col,     "+",       wall_col)
        scr.addstr(row,     col + 1, top,       wall_col)
        scr.addstr(row + 1, col,     left,      wall_col)
        scr.addstr(row + 1, col + 1, f" {ch} ", color)
    except curses.error:
        pass


def draw_maze(
        scr: Any,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_set: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> None:
    """Draw the full maze grid on the terminal screen.

    Args:
        scr: Curses screen object
        maze: 2D grid of wall bitmasks
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        path_set: Set of cells on the solution path
        cells_42: Set of cells forming the 42 pattern
    """
    height: int = len(maze)
    width: int = len(maze[0])
    wall_col: int = curses.color_pair(WALL)

    for y in range(height):
        for x in range(width):
            pos = (x, y)
            ch, color = get_cell_char(
                pos, entry, exit_, path_set, cells_42
            )
            draw_cell(
                scr, y * 2, x * 4,
                maze[y][x], ch, color, wall_col,
                pos in cells_42
            )

        # Right border of each row
        try:
            right = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2,     width * 4, "+", wall_col)
            scr.addstr(y * 2 + 1, width * 4, right, wall_col)
        except curses.error:
            pass

    # Bottom border
    for x in range(width):
        bot = "---" if (maze[height - 1][x] & SOUTH) else "   "
        try:
            scr.addstr(height * 2, x * 4,     "+", wall_col)
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
        theme: int) -> None:
    """Draw the keyboard controls bar below the maze.

    Args:
        scr: Curses screen object
        row: Screen row to draw the menu at
        show_path: Whether path is currently visible
        show_42: Whether 42 pattern is currently visible
        theme: Current theme index
    """
    p = "Hide Path" if show_path else "Show Path"
    f42 = "Hide 42" if show_42 else "Show 42"
    col = THEME_NAMES[theme % len(THEME_NAMES)]
    try:
        scr.addstr(row, 0, " === A-Maze-ing === ",
                   curses.color_pair(MENU))
        menu = (
            f" [R] New maze  [P] {p}  "
            f"[C] Color:{col}  [4] {f42}  [Q] Quit "
        )
        scr.addstr(row + 1, 0, menu, curses.color_pair(WALL))
    except curses.error:
        pass


def display_maze(
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        width: int,
        height: int,
        perfect: bool = True,
        seed: Optional[int] = None) -> None:
    """Launch the interactive terminal display.

    Keys: R=new maze, P=show/hide path, C=change color,
          4=show/hide 42, Q=quit

    Args:
        maze: 2D grid of wall bitmasks
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        width: Maze width in cells
        height: Maze height in cells
        perfect: Whether maze is perfect
        seed: Random seed used for generation
    """
    def run(scr: Any) -> None:
        nonlocal maze, seed

        # Terminal setup
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        theme: int = 0
        show_path: bool = False
        show_42: bool = False
        init_colors(theme)

        path: Optional[List[Tuple[int, int]]]
        path = find_shortest_path(maze, entry, exit_)

        while True:
            scr.clear()
            max_y, _ = scr.getmaxyx()

            # Build sets to pass to draw_maze
            path_set = set(path) if path and show_path else set()
            c42_set = set(get_42_cells(width, height)) if show_42 else set()

            draw_maze(scr, maze, entry, exit_, path_set, c42_set)

            menu_row = height * 2 + 2
            if menu_row + 2 < max_y:
                draw_menu(scr, menu_row, show_path, show_42, theme)

            scr.refresh()

            # Handle keyboard input
            key = scr.getch()
            ch = chr(key).upper() if 0 <= key < 256 else ""

            if ch == "Q":
                break
            elif ch == "R":
                seed = random.randint(0, 999999)
                maze = generate_maze(width, height, entry, exit_, seed)
                embed_42_pattern(maze, width, height, entry, exit_)
                path = find_shortest_path(maze, entry, exit_)
            elif ch == "P":
                show_path = not show_path
            elif ch == "C":
                theme = (theme + 1) % len(THEMES)
                init_colors(theme)
            elif ch == "4":
                show_42 = not show_42

    curses.wrapper(run)
