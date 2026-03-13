import curses
import random
from typing import List, Tuple, Set, Any

from .maze_generator import (
    NORTH, EAST, SOUTH, WEST,
    generate_maze,
    embed_42_pattern,
    find_shortest_path,
    get_42_cells,
)

WALL: int = 1
PATH: int = 2
ENTRY: int = 3
EXIT: int = 4
C42: int = 5
MENU: int = 6
BG: int = 7

THEMES: List[Tuple[int, int]] = [
    (curses.COLOR_WHITE,   curses.COLOR_BLACK),
    (curses.COLOR_YELLOW,  curses.COLOR_BLACK),
    (curses.COLOR_GREEN,   curses.COLOR_BLACK),
    (curses.COLOR_CYAN,    curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_RED,     curses.COLOR_BLACK),
    (curses.COLOR_BLUE,    curses.COLOR_BLACK),
]
THEME_NAMES: List[str] = ["White", "Yellow", "Green", "Cyan", "Magenta", "Red", "Blue"]


def init_colors(theme: int) -> None:
    """Set up curses colors for the chosen theme.
    
    Args:
        theme: Theme index to apply
    """
    fg, bg = THEMES[theme % len(THEMES)]
    curses.init_pair(WALL,  fg,                   bg)
    curses.init_pair(PATH,  curses.COLOR_CYAN,    bg)
    curses.init_pair(ENTRY, curses.COLOR_GREEN,   bg)
    curses.init_pair(EXIT,  curses.COLOR_RED,     bg)
    curses.init_pair(C42,   curses.COLOR_MAGENTA, bg)
    curses.init_pair(MENU,  curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(BG,    curses.COLOR_BLACK,   bg)


def draw_maze(scr: Any, maze: List[List[int]], entry: Tuple[int, int], exit_: Tuple[int, int], path_set: Set[Tuple[int, int]], cells_42: Set[Tuple[int, int]]) -> None:
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
                ch, color = "E", curses.color_pair(ENTRY) | curses.A_BOLD
            elif pos == exit_:
                ch, color = "X", curses.color_pair(EXIT)  | curses.A_BOLD
            elif pos in path_set:
                ch, color = ".", curses.color_pair(PATH)
            elif pos in cells_42:
                ch, color = "#", curses.color_pair(C42)   | curses.A_BOLD
            else:
                ch, color = " ", bg_col

            top: str = "---" if (cell & NORTH) else "   "
            left: str = "|"   if (cell & WEST)  else " "

            try:
                scr.addstr(row,     col,     "+",       wall_col)
                scr.addstr(row,     col + 1, top,       wall_col)
                scr.addstr(row + 1, col,     left,      wall_col)
                scr.addstr(row + 1, col + 1, f" {ch} ", color)
            except curses.error:
                pass

        try:
            right: str = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2,     width * 4, "+",   wall_col)
            scr.addstr(y * 2 + 1, width * 4, right, wall_col)
        except curses.error:
            pass

    for x in range(width):
        bot: str = "---" if (maze[height - 1][x] & SOUTH) else "   "
        try:
            scr.addstr(height * 2, x * 4,     "+", wall_col)
            scr.addstr(height * 2, x * 4 + 1, bot, wall_col)
        except curses.error:
            pass
    try:
        scr.addstr(height * 2, width * 4, "+", wall_col)
    except curses.error:
        pass


def draw_menu(scr: Any, row: int, show_path: bool, show_42: bool, theme: int) -> None:
    """Draw the keyboard controls below the maze.
    
    Args:
        scr: Curses screen object
        row: Row position to draw the menu
        show_path: Whether path is currently shown
        show_42: Whether '42' pattern is currently shown
        theme: Current theme index
    """
    p: str = "Hide Path" if show_path else "Show Path"
    f42: str = "Hide 42"   if show_42   else "Show 42"
    col: str = THEME_NAMES[theme % len(THEME_NAMES)]
    try:
        scr.addstr(row, 0, " === A-Maze-ing === ", curses.color_pair(MENU))
        scr.addstr(row + 1, 0,
                   f" [R] New maze  [P] {p}  [C] Color:{col}  [4] {f42}  [Q] Quit ",
                   curses.color_pair(WALL))
    except curses.error:
        pass


def display_maze(maze: List[List[int]], entry: Tuple[int, int], exit_: Tuple[int, int], width: int, height: int, perfect: bool = True, seed: int | None = None) -> None:
    """Show the maze in the terminal with keyboard controls.

    Keys: R=new maze, P=show/hide path, C=change color, 4=show/hide 42, Q=quit
    
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
        show_path: bool = False
        show_42: bool = False
        init_colors(theme)

        path: List[Tuple[int, int]] | None = find_shortest_path(maze, entry, exit_)

        while True:
            scr.clear()
            max_y: int
            _: int
            max_y, _ = scr.getmaxyx()

            path_set: Set[Tuple[int, int]] = set(path) if path and show_path else set()
            c42_set: Set[Tuple[int, int]] = set(get_42_cells(width, height)) if show_42 else set()

            draw_maze(scr, maze, entry, exit_, path_set, c42_set)

            menu_row: int = height * 2 + 2
            if menu_row + 2 < max_y:
                draw_menu(scr, menu_row, show_path, show_42, theme)

            scr.refresh()

            key: int = scr.getch()
            ch: str = chr(key).upper() if 0 <= key < 256 else ""

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