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

# Each element on screen has a color "slot" (just a number curses uses)
WALL = 1   # color for walls  ( + --- | )
PATH = 2   # color for path   ( * )
ENTRY = 3   # color for entry  ( E )
EXIT = 4   # color for exit   ( X )
C42 = 5   # color for 42 pattern ( # )
MENU = 6   # color for the menu bar
BG = 7   # color for empty cells

# Available wall color themes  (foreground color, background color)
THEMES = [
    (curses.COLOR_WHITE,   curses.COLOR_BLACK),
    (curses.COLOR_YELLOW,  curses.COLOR_BLACK),
    (curses.COLOR_GREEN,   curses.COLOR_BLACK),
    (curses.COLOR_CYAN,    curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_RED,     curses.COLOR_BLACK),
    (curses.COLOR_BLUE,    curses.COLOR_BLACK),
]
THEME_NAMES = ["White", "Yellow", "Green", "Cyan", "Magenta", "Red", "Blue"]


# FUNCTION 1 – set up colors
# Called once at start and every time the user presses C
def init_colors(theme: int) -> None:
    fg, bg = THEMES[theme % len(THEMES)]  # pick the theme colors
    curses.init_pair(WALL,  fg,                   bg)   # walls use theme color
    curses.init_pair(PATH,  curses.COLOR_YELLOW,  bg)   # path dots are yellow
    curses.init_pair(ENTRY, curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(EXIT,  curses.COLOR_BLACK,   curses.COLOR_RED)
    curses.init_pair(C42,   curses.COLOR_MAGENTA, bg)
    curses.init_pair(MENU,  curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(BG,    curses.COLOR_BLACK,   bg)   # empty cells


# FUNCTION 2 – decide what character goes inside one cell
# Returns a (character, color) pair
# Priority: 42 block > E > X > path dot > empty space
def get_char(
        pos: Tuple[int, int],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_cells: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> Tuple[str, int]:

    if pos in cells_42:
        return "#", curses.color_pair(C42) | curses.A_BOLD
    if pos == entry:
        return "E", curses.color_pair(ENTRY) | curses.A_BOLD
    if pos == exit_:
        return "X", curses.color_pair(EXIT) | curses.A_BOLD
    if pos in path_cells:
        return "*", curses.color_pair(PATH) | curses.A_BOLD
    return " ", curses.color_pair(BG)


# draws ONE cell on screen (the +, walls, and character inside)

# On screen every maze cell takes 2 rows and 4 columns:
#
#   col  col+1 col+2 col+3
#    +    -     -     -       ← top row:  corner + top wall
#    |    (space ch space)    ← bot row:  left wall + character inside
#
# The right wall and bottom wall are added later by draw_maze()
def draw_cell(
        scr: Any,
        row: int, col: int,
        walls: int,
        ch: str, color: int,
        wall_color: int,
        is_42: bool) -> None:

    # hide walls for 42 cells so they look like solid filled blocks
    top = "---" if (walls & NORTH) and not is_42 else "   "
    left = "|" if (walls & WEST) and not is_42 else " "

    try:
        scr.addstr(row,     col,     "+",       wall_color)  # corner
        scr.addstr(row,     col + 1, top,       wall_color)  # top wall
        scr.addstr(row + 1, col,     left,      wall_color)  # left wall
        scr.addstr(row + 1, col + 1, f" {ch} ", color)       # cell interior
    except curses.error:
        pass  # cell is outside the terminal window, just skip it


# FUNCTION 4 – draw the whole maze
# Loops over every cell, draws it, then adds the missing right and bottom edges
def draw_maze(
        scr: Any,
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        path_cells: Set[Tuple[int, int]],
        cells_42: Set[Tuple[int, int]]) -> None:

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

        # draw the right border of this row (draw_cell only draws left walls)
        try:
            right = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2,     width * 4, "+",    wall_color)
            scr.addstr(y * 2 + 1, width * 4, right,  wall_color)
        except curses.error:
            pass

    # draw the bottom border (draw_cell only draws top walls)
    for x in range(width):
        bot = "---" if (maze[height - 1][x] & SOUTH) else "   "
        try:
            scr.addstr(height * 2, x * 4,     "+",  wall_color)
            scr.addstr(height * 2, x * 4 + 1, bot,  wall_color)
        except curses.error:
            pass
    try:
        scr.addstr(height * 2, width * 4, "+", wall_color)
    except curses.error:
        pass


# FUNCTION 5 – draw the menu bar below the maze
# Shows which keys are available and their current state
def draw_menu(
        scr: Any,
        row: int,
        show_path: bool,
        show_42: bool,
        theme: int) -> None:

    p = "Hide Path" if show_path else "Show Path"
    f42 = "Hide 42" if show_42 else "Show 42"
    color_name = THEME_NAMES[theme % len(THEME_NAMES)]

    try:
        scr.addstr(row,     0, " === A-Maze-ing === ",
                   curses.color_pair(MENU))
        scr.addstr(row + 1, 0,
                   f" [R] New maze  [P] {p}  "
                   f"[C] Color:{color_name}  [4] {f42}  [Q] Quit ",
                   curses.color_pair(WALL))
    except curses.error:
        pass


# FUNCTION 6 – main display loop  (entry point called from a_maze_ing.py)
#
# Flow:
#   1. set up terminal
#   2. loop forever:
#        - clear screen
#        - draw maze + menu
#        - wait for a key
#        - react to the key  (Q / R / P / C / 4)
def display_maze(
        maze: List[List[int]],
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        width: int,
        height: int,
        perfect: bool = True,
        seed: Optional[int] = None) -> None:

    def run(scr: Any) -> None:
        nonlocal maze, seed  # allow R key to replace maze and seed

        # terminal setup
        curses.curs_set(0)        # hide blinking cursor
        curses.start_color()
        curses.use_default_colors()

        theme = 0
        show_path = False
        show_42 = False
        init_colors(theme)

        path = find_shortest_path(maze, entry, exit_)

        # main loop
        while True:
            scr.clear()
            max_y, _ = scr.getmaxyx()  # current terminal height

            # only pass non-empty sets when the feature is toggled on
            path_cells = set(path) if path and show_path else set()
            cells_42 = set(get_42_cells(width, height)) if show_42 else set()

            draw_maze(scr, maze, entry, exit_, path_cells, cells_42)

            menu_row = height * 2 + 2          # 2 rows below the maze
            if menu_row + 2 < max_y:           # only draw if it fits
                draw_menu(scr, menu_row, show_path, show_42, theme)

            scr.refresh()  # push everything to the screen

            # read one key
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

<<<<<<< HEAD
    curses.wrapper(run)
=======
    # curses.wrapper handles terminal setup/teardown safely
    curses.wrapper(run)
>>>>>>> 5962f05 (fix path display)
