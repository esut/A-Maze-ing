import curses
import random

from .maze_generator import (
    NORTH, EAST, SOUTH, WEST,
    generate_maze,
    embed_42_pattern,
    find_shortest_path,
    get_42_cells,
)

# Color pair IDs
WALL  = 1
PATH  = 2
ENTRY = 3
EXIT  = 4
C42   = 5
MENU  = 6
BG    = 7

# Wall color themes: (foreground, background)
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


def init_colors(theme):
    """Set up curses colors for the chosen theme."""
    fg, bg = THEMES[theme % len(THEMES)]
    curses.init_pair(WALL,  fg,                   bg)
    curses.init_pair(PATH,  curses.COLOR_CYAN,    bg)
    curses.init_pair(ENTRY, curses.COLOR_GREEN,   bg)
    curses.init_pair(EXIT,  curses.COLOR_RED,     bg)
    curses.init_pair(C42,   curses.COLOR_MAGENTA, bg)
    curses.init_pair(MENU,  curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.init_pair(BG,    curses.COLOR_BLACK,   bg)


def draw_maze(scr, maze, entry, exit_, path_set, cells_42):
    """Draw the maze on the terminal screen."""
    height   = len(maze)
    width    = len(maze[0])
    wall_col = curses.color_pair(WALL)
    bg_col   = curses.color_pair(BG)

    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            row  = y * 2
            col  = x * 4

            pos = (x, y)
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

            top  = "---" if (cell & NORTH) else "   "
            left = "|"   if (cell & WEST)  else " "

            try:
                scr.addstr(row,     col,     "+",       wall_col)
                scr.addstr(row,     col + 1, top,       wall_col)
                scr.addstr(row + 1, col,     left,      wall_col)
                scr.addstr(row + 1, col + 1, f" {ch} ", color)
            except curses.error:
                pass

        # Right border
        try:
            right = "|" if (maze[y][width - 1] & EAST) else " "
            scr.addstr(y * 2,     width * 4, "+",   wall_col)
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


def draw_menu(scr, row, show_path, show_42, theme):
    """Draw the keyboard controls below the maze."""
    p   = "Hide Path" if show_path else "Show Path"
    f42 = "Hide 42"   if show_42   else "Show 42"
    col = THEME_NAMES[theme % len(THEME_NAMES)]
    try:
        scr.addstr(row, 0, " === A-Maze-ing === ", curses.color_pair(MENU))
        scr.addstr(row + 1, 0,
                   f" [R] New maze  [P] {p}  [C] Color:{col}  [4] {f42}  [Q] Quit ",
                   curses.color_pair(WALL))
    except curses.error:
        pass


def display_maze(maze, entry, exit_, width, height, perfect=True, seed=None):
    """Show the maze in the terminal with keyboard controls.

    Keys: R=new maze, P=show/hide path, C=change color, 4=show/hide 42, Q=quit
    """
    def run(scr):
        nonlocal maze, seed

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        theme     = 0
        show_path = False
        show_42   = False
        init_colors(theme)

        path = find_shortest_path(maze, entry, exit_)

        while True:
            scr.clear()
            max_y, _ = scr.getmaxyx()

            path_set = set(path) if path and show_path else set()
            c42_set  = set(get_42_cells(width, height)) if show_42 else set()

            draw_maze(scr, maze, entry, exit_, path_set, c42_set)

            menu_row = height * 2 + 2
            if menu_row + 2 < max_y:
                draw_menu(scr, menu_row, show_path, show_42, theme)

            scr.refresh()

            key = scr.getch()
            ch  = chr(key).upper() if 0 <= key < 256 else ""

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