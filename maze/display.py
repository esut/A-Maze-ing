import curses
import random
import time
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

# 42 pattern color themes (cycles when user presses 4)
C42_COLORS: List[int] = [
    curses.COLOR_MAGENTA,
    curses.COLOR_CYAN,
    curses.COLOR_YELLOW,
    curses.COLOR_RED,
    curses.COLOR_GREEN,
]
C42_NAMES: List[str] = ["Magenta", "Cyan", "Yellow", "Red", "Green"]


def init_colors(theme: int, c42_theme: int) -> None:
    """Set up curses color pairs for the chosen themes.

    Args:
        theme: Index into THEMES for wall color
        c42_theme: Index into C42_COLORS for 42 pattern color
    """
    fg, bg = THEMES[theme % len(THEMES)]
    curses.init_pair(WALL,  fg,                              bg)
    curses.init_pair(PATH,  curses.COLOR_YELLOW,  curses.COLOR_BLUE)
    curses.init_pair(ENTRY, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(EXIT,  curses.COLOR_BLACK,   curses.COLOR_RED)
    curses.init_pair(C42,   C42_COLORS[c42_theme % len(C42_COLORS)], bg)
    curses.init_pair(MENU,  curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(BG,    curses.COLOR_BLACK,   bg)


def get_char(
        pos: Tuple[int, int],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_cells: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> Tuple[str, int]:
    """Return the character and color to display inside a cell.

    Priority: 42 > entry > exit > path > empty

    Args:
        pos: Current cell (x, y)
        entry: Entry coordinates
        exit_: Exit coordinates
        path_cells: Set of path cells
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
    if pos in path_cells:
        return "*", curses.color_pair(PATH) | curses.A_BOLD
    return " ", curses.color_pair(BG)


def draw_cell(
        scr: Any,
        row: int,
        col: int,
        walls: int,
        ch: str,
        color: int,
        wall_color: int,
        is_42: bool) -> None:
    """Draw one maze cell at the given screen position.

    Each cell takes 2 rows x 4 columns on screen:
        +---+
        | E |

    Args:
        scr: Curses screen object
        row: Screen row (maze_y * 2)
        col: Screen column (maze_x * 4)
        walls: Bitmask of walls for this cell
        ch: Character to show inside the cell
        color: Color attribute for the character
        wall_color: Color attribute for walls
        is_42: If True, skip drawing walls (42 cells show clean)
    """
    top = "---" if (walls & NORTH) and not is_42 else "   "
    left = "|" if (walls & WEST) and not is_42 else " "
    try:
        scr.addstr(row,     col,     "+",       wall_color)
        scr.addstr(row,     col + 1, top,       wall_color)
        scr.addstr(row + 1, col,     left,      wall_color)
        scr.addstr(row + 1, col + 1, f" {ch} ", color)
    except curses.error:
        pass


def draw_maze(
        scr: Any,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_cells: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> None:
    """Draw the full maze grid on screen.

    Args:
        scr: Curses screen object
        maze: 2D grid of wall bitmasks
        entry: Entry coordinates (x, y)
        exit_: Exit coordinates (x, y)
        path_cells: Set of cells on the solution path
        cells_42: Set of cells forming the 42 pattern
    """
    height = len(maze)
    width = len(maze[0])
    wall_color = curses.color_pair(WALL)

    for y in range(height):
        for x in range(width):
            pos = (x, y)
            ch, color = get_char(pos, entry, exit_, path_cells, cells_42)
            draw_cell(scr, y * 2, x * 4,
                      maze[y][x], ch, color, wall_color,
                      pos in cells_42)

        # right border of this row
        try:
            right = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2,     width * 4, "+",   wall_color)
            scr.addstr(y * 2 + 1, width * 4, right, wall_color)
        except curses.error:
            pass

    # bottom border
    for x in range(width):
        bot = "---" if (maze[height - 1][x] & SOUTH) else "   "
        try:
            scr.addstr(height * 2, x * 4,     "+", wall_color)
            scr.addstr(height * 2, x * 4 + 1, bot, wall_color)
        except curses.error:
            pass
    try:
        scr.addstr(height * 2, width * 4, "+", wall_color)
    except curses.error:
        pass


def draw_slow_path(
        scr: Any,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path: List[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> None:
    """Animate the path step by step with a delay between each cell.

    Args:
        scr: Curses screen object
        maze: 2D grid of wall bitmasks
        entry: Entry coordinates
        exit_: Exit coordinates
        path: Ordered list of cells from entry to exit
        cells_42: Set of 42 pattern cells
    """
    revealed: Set[Tuple[int, int]] = set()

    for pos in path:
        revealed.add(pos)
        x, y = pos
        ch, color = get_char(pos, entry, exit_, revealed, cells_42)
        try:
            scr.addstr(y * 2 + 1, x * 4 + 1, f" {ch} ", color)
        except curses.error:
            pass
        scr.refresh()
        time.sleep(0.05)  # 50ms delay between each step


def draw_menu(
        scr: Any,
        row: int,
        show_path: bool,
        slow_mode: bool,
        show_42: bool,
        theme: int,
        c42_theme: int) -> None:
    """Draw the table-style menu below the maze.

    Args:
        scr: Curses screen object
        row: Screen row to start drawing
        show_path: Whether path is currently visible
        slow_mode: Whether slow path mode is active
        show_42: Whether 42 pattern is visible
        theme: Current wall color theme index
        c42_theme: Current 42 color theme index
    """
    menu_color = curses.color_pair(MENU)
    wall_color = curses.color_pair(WALL)

    p = "ON " if show_path else "OFF"
    s = "ON " if slow_mode else "OFF"
    c = THEME_NAMES[theme % len(THEME_NAMES)]
    c42 = C42_NAMES[c42_theme % len(C42_NAMES)]
    f42 = "ON " if show_42 else "OFF"

    lines = [
        "=====================",
        "|   A-Maze-ing      |",
        "=====================",
        "| R | New Maze      |",
        f"| P | Path    [{p}] |",
        f"| S | Slow    [{s}] |",
        f"| C | {c:<13}  |",
        f"| 4 | 42[{f42}] {c42:<5} |",
        "| Q | Quit          |",
        "=====================",
    ]

    for i, line in enumerate(lines):
        try:
            if i in (0, 2, 9):
                scr.addstr(row + i, 0, line, menu_color)
            elif i == 1:
                scr.addstr(row + i, 0, line, menu_color | curses.A_BOLD)
            else:
                scr.addstr(row + i, 0, line, wall_color)
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

    Keys:
        R = new maze
        P = show/hide path
        S = slow motion path animation
        C = change wall color theme
        4 = toggle 42 pattern / cycle its color
        Q = quit

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

        # terminal setup
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        theme: int = 0
        c42_theme: int = 0
        show_path: bool = False
        slow_mode: bool = False
        show_42: bool = False
        init_colors(theme, c42_theme)

        path = find_shortest_path(maze, entry, exit_)

        while True:
            scr.clear()
            max_y, _ = scr.getmaxyx()

            path_cells = set(path) if path and show_path else set()
            cells_42 = set(get_42_cells(width, height)) if show_42 else set()

            draw_maze(scr, maze, entry, exit_, path_cells, cells_42)

            menu_row = height * 2 + 2
            draw_menu(
                scr, menu_row, show_path,
                slow_mode, show_42, theme, c42_theme
            )

            scr.refresh()

            key = scr.getch()
            ch = chr(key).upper() if 0 <= key < 256 else ""

            if ch == "Q":
                break

            elif ch == "R":
                seed = random.randint(0, 999999)
                maze = generate_maze(width, height, entry, exit_, seed)
                embed_42_pattern(maze, width, height, entry, exit_)
                path = find_shortest_path(maze, entry, exit_)
                show_path = False

            elif ch == "P":
                show_path = not show_path
                # if slow mode is on, animate the path step by step
                if show_path and slow_mode and path:
                    cells_42 = set(
                        get_42_cells(width, height)
                    ) if show_42 else set()
                    draw_slow_path(
                        scr, maze, entry, exit_, path, cells_42
                    )
                    continue

            elif ch == "S":
                slow_mode = not slow_mode

            elif ch == "C":
                theme = (theme + 1) % len(THEMES)
                init_colors(theme, c42_theme)

            elif ch == "4":
                if show_42:
                    # already visible → cycle its color
                    c42_theme = (c42_theme + 1) % len(C42_COLORS)
                    init_colors(theme, c42_theme)
                else:
                    show_42 = True

<<<<<<< HEAD
<<<<<<< HEAD
    curses.wrapper(run)
=======
    # curses.wrapper handles terminal setup/teardown safely
=======
>>>>>>> afb66ee (Add bonus features: 42 color cycle, slow path, new menu UI)
    curses.wrapper(run)
>>>>>>> 5962f05 (fix path display)
