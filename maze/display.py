import curses
import random
from typing import List, Tuple, Optional
from collections import deque



NORTH = 1  
EAST = 2   
SOUTH = 4  
WEST = 8   


COLOR_WALL = 1
COLOR_PATH = 2
COLOR_ENTRY = 3
COLOR_EXIT = 4
COLOR_42 = 5
COLOR_MENU = 6
COLOR_BACKGROUND = 7


WALL_COLOR_THEMES = [
    (curses.COLOR_WHITE, curses.COLOR_BLACK),   
    (curses.COLOR_YELLOW, curses.COLOR_BLACK),   
    (curses.COLOR_GREEN, curses.COLOR_BLACK),   
    (curses.COLOR_CYAN, curses.COLOR_BLACK),    
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK), 
    (curses.COLOR_RED, curses.COLOR_BLACK),      
    (curses.COLOR_BLUE, curses.COLOR_BLACK),    
]

THEME_NAMES = [
    "White", "Yellow", "Green", "Cyan", "Magenta", "Red", "Blue"
]


def find_shortest_path(
    maze: List[List[int]],
    entry: Tuple[int, int],
    exit_: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """Find shortest path using BFS.

    Args:
        maze: 2D list of cell wall bitmasks.
        entry: (x, y) start coordinates.
        exit_: (x, y) end coordinates.

    Returns:
        List of (x, y) cells on the shortest path, or None if unreachable.
    """
    height = len(maze)
    width = len(maze[0]) if height > 0 else 0
    ex, ey = entry
    fx, fy = exit_

    visited: List[List[bool]] = [
        [False] * width for _ in range(height)
    ]
    parent: dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
    queue: deque[Tuple[int, int]] = deque()

    queue.append((ex, ey))
    visited[ey][ex] = True
    parent[(ex, ey)] = None

    directions = [
        (0, -1, NORTH),   
        (1,  0, EAST),    
        (0,  1, SOUTH),  
        (-1, 0, WEST),    
    ]

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == (fx, fy):
           
            path: List[Tuple[int, int]] = []
            cur: Optional[Tuple[int, int]] = (fx, fy)
            while cur is not None:
                path.append(cur)
                cur = parent.get(cur)
            path.reverse()
            return path

        cell = maze[cy][cx]
        for dx, dy, wall_bit in directions:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and not visited[ny][nx]
                and not (cell & wall_bit)
            ):
                visited[ny][nx] = True
                parent[(nx, ny)] = (cx, cy)
                queue.append((nx, ny))

    return None


def generate_maze(
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
    perfect: bool = True,
    seed: Optional[int] = None
) -> List[List[int]]:
    """Generate a maze using recursive backtracker algorithm.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) entry cell.
        exit_: (x, y) exit cell.
        perfect: If True, generate a perfect maze.
        seed: Random seed for reproducibility.

    Returns:
        2D list of cell wall bitmasks.
    """
    rng = random.Random(seed)

    
    maze: List[List[int]] = [[15] * width for _ in range(height)]

    visited: List[List[bool]] = [
        [False] * width for _ in range(height)
    ]

    opposite = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
    directions_map = [
        (0, -1, NORTH),
        (1,  0, EAST),
        (0,  1, SOUTH),
        (-1, 0, WEST),
    ]

    def carve(cx: int, cy: int) -> None:
        """Carve passages using DFS."""
        visited[cy][cx] = True
        dirs = directions_map[:]
        rng.shuffle(dirs)
        for dx, dy, wall_bit in dirs:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and not visited[ny][nx]
            ):
                
                maze[cy][cx] &= ~wall_bit
                maze[ny][nx] &= ~opposite[wall_bit]
                carve(nx, ny)

    import sys
    sys.setrecursionlimit(width * height * 2 + 100)
    carve(0, 0)

    
    ex, ey = entry
    fx, fy = exit_
    
    if ey == 0:
        maze[ey][ex] &= ~NORTH
    elif ey == height - 1:
        maze[ey][ex] &= ~SOUTH
    if fy == 0:
        maze[fy][fx] &= ~NORTH
    elif fy == height - 1:
        maze[fy][fx] &= ~SOUTH

    return maze


def init_colors(theme_index: int) -> None:
    """Initialize curses color pairs for current theme.

    Args:
        theme_index: Index into WALL_COLOR_THEMES.
    """
    fg, bg = WALL_COLOR_THEMES[theme_index]
    curses.init_pair(COLOR_WALL, fg, bg)
    curses.init_pair(COLOR_PATH, curses.COLOR_CYAN, bg)
    curses.init_pair(COLOR_ENTRY, curses.COLOR_GREEN, bg)
    curses.init_pair(COLOR_EXIT, curses.COLOR_RED, bg)
    curses.init_pair(COLOR_42, curses.COLOR_MAGENTA, bg)
    curses.init_pair(COLOR_MENU, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_BACKGROUND, curses.COLOR_BLACK, bg)


def get_42_cells(
    width: int,
    height: int
) -> List[Tuple[int, int]]:
    """Return cells that form a visible '42' pattern centered in the maze.

    The '4' occupies a 3x5 bounding box and '2' occupies a 3x5 bounding box,
    separated by 1 column gap. Total pattern width = 7, height = 5.
    The pattern is placed so its center aligns with the maze center.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        List of (x, y) cells belonging to the '42' pattern.
    """
    
    pat_w = 7
    pat_h = 5

    if width < pat_w + 2 or height < pat_h + 2:
        return []

   
    cx = (width - pat_w) // 2
    cy = (height - pat_h) // 2

    
    four: List[Tuple[int, int]] = [
        (0, 0), (0, 1), (0, 2),          
        (1, 2),                            
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),  
    ]
    
    two: List[Tuple[int, int]] = [
        (0, 0), (1, 0), (2, 0),           
        (2, 1),                            
        (0, 2), (1, 2), (2, 2),           
        (0, 3),                            
        (0, 4), (1, 4), (2, 4),           
    ]

    cells: List[Tuple[int, int]] = []
    for dx, dy in four:
        cells.append((cx + dx, cy + dy))

    ox = cx + 4 
    for dx, dy in two:
        cells.append((ox + dx, cy + dy))

    return [(x, y) for x, y in cells if 0 <= x < width and 0 <= y < height]


def close_cell_walls(
    maze: List[List[int]],
    x: int,
    y: int
) -> None:
    """Fully close all walls of a cell and sync neighbors.

    Args:
        maze: Maze grid.
        x: Cell column.
        y: Cell row.
    """
    h = len(maze)
    w = len(maze[0]) if h > 0 else 0
    maze[y][x] = 15  

    
    if y > 0:
        maze[y - 1][x] |= SOUTH
    if y < h - 1:
        maze[y + 1][x] |= NORTH
    if x > 0:
        maze[y][x - 1] |= EAST
    if x < w - 1:
        maze[y][x + 1] |= WEST


def _open_wall(
    maze: List[List[int]],
    x: int,
    y: int,
    direction: int,
    width: int,
    height: int,
) -> None:
    """Open one wall between cell (x,y) and its neighbour in direction.

    Args:
        maze: Maze grid.
        x: Cell column.
        y: Cell row.
        direction: NORTH, EAST, SOUTH, or WEST flag.
        width: Maze width.
        height: Maze height.
    """
    opposite = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
    dx_map = {NORTH: 0, SOUTH: 0, EAST: 1, WEST: -1}
    dy_map = {NORTH: -1, SOUTH: 1, EAST: 0, WEST: 0}
    nx, ny = x + dx_map[direction], y + dy_map[direction]
    if 0 <= nx < width and 0 <= ny < height:
        maze[y][x] &= ~direction
        maze[ny][nx] &= ~opposite[direction]


def _restore_path_around_42(
    maze: List[List[int]],
    blocked: set,
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
) -> None:
    """Restore connectivity after embedding the '42' block.

    Instead of carving wide open corridors (which look wrong and make
    paths identical), this function uses a minimal BFS-based check:
    if a path still exists, do nothing.  If not, open only the walls
    of the single narrowest detour around the blocked rectangle.

    The detour goes:
      - straight down the column just LEFT of the block
        (from the row above the block to the row below the block)
      - one step left at the top and bottom to enter/leave that column

    This adds at most 2*(block_height+2) opened walls, preserving
    maze variety.

    Args:
        maze: Maze grid to modify in-place.
        blocked: Set of (x, y) cells in the '42' pattern.
        width: Maze width.
        height: Maze height.
        entry: Entry cell (x, y).
        exit_: Exit cell (x, y).
    """
    if not blocked:
        return

  
    def path_exists() -> bool:
        """Return True if entry→exit reachable via open walls."""
        h, w = height, width
        ex, ey = entry
        fx, fy = exit_
        seen: set = {(ex, ey)}
        queue: deque = deque([(ex, ey)])
        dirs = [(0, -1, NORTH), (1, 0, EAST), (0, 1, SOUTH), (-1, 0, WEST)]
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (fx, fy):
                return True
            cell = maze[cy][cx]
            for ddx, ddy, wb in dirs:
                nx2, ny2 = cx + ddx, cy + ddy
                if (
                    0 <= nx2 < w and 0 <= ny2 < h
                    and (nx2, ny2) not in seen
                    and not (cell & wb)     
                ):
                    seen.add((nx2, ny2))
                    queue.append((nx2, ny2))
        return False

    if path_exists():
        return  

    
    ys = [y for (_, y) in blocked]
    xs = [x for (x, _) in blocked]
    block_top = min(ys)
    block_bot = max(ys)
    block_left = min(xs)
    block_right = max(xs)

    
    if block_left > 0:
        bypass_col = block_left - 1
    else:
        bypass_col = block_right + 1

    row_above = block_top - 1 if block_top > 0 else 0
    row_below = block_bot + 1 if block_bot < height - 1 else height - 1

    
    for r in range(row_above, row_below):
        maze[r][bypass_col] &= ~SOUTH
        maze[r + 1][bypass_col] &= ~NORTH

 
    for row in (row_above, row_below):
        
        if bypass_col + 1 < width and (bypass_col + 1, row) not in blocked:
            maze[row][bypass_col] &= ~EAST
            maze[row][bypass_col + 1] &= ~WEST
       
        if bypass_col - 1 >= 0 and (bypass_col - 1, row) not in blocked:
            maze[row][bypass_col] &= ~WEST
            maze[row][bypass_col - 1] &= ~EAST

    if not path_exists():
        safe_col = 0 if block_left > 0 else width - 1
        for r in range(height - 1):
            maze[r][safe_col] &= ~SOUTH
            maze[r + 1][safe_col] &= ~NORTH
        for r in (0, height - 1):
            for x in range(width - 1):
                if (x, r) not in blocked and (x + 1, r) not in blocked:
                    maze[r][x] &= ~EAST
                    maze[r][x + 1] &= ~WEST


def embed_42_pattern(
    maze: List[List[int]],
    width: int,
    height: int,
    entry: Tuple[int, int] = (0, 0),
    exit_: Optional[Tuple[int, int]] = None,
) -> bool:
    """Embed '42' pattern into the maze and guarantee a path still exists.

    Closes all walls of the '42' cells, then restores bypass corridors
    around the block so entry→exit remains reachable.

    Args:
        maze: Maze grid to modify in-place.
        width: Maze width.
        height: Maze height.
        entry: Entry cell coordinates.
        exit_: Exit cell coordinates (defaults to bottom-right).

    Returns:
        True if pattern was embedded, False if maze too small.
    """
    if exit_ is None:
        exit_ = (width - 1, height - 1)

    cells = get_42_cells(width, height)
    if not cells:
        return False

    blocked: set = set(cells)

    for x, y in cells:
        close_cell_walls(maze, x, y)

    _restore_path_around_42(maze, blocked, width, height, entry, exit_)

    return True


def draw_maze(
    stdscr: "curses._CursesWindow",
    maze: List[List[int]],
    entry: Tuple[int, int],
    exit_: Tuple[int, int],
    path: Optional[List[Tuple[int, int]]],
    show_path: bool,
    show_42: bool,
    width: int,
    height: int,
    offset_y: int = 0,
    offset_x: int = 0
) -> None:
    """Draw the maze using curses.

    Args:
        stdscr: Curses screen.
        maze: 2D wall bitmask grid.
        entry: Entry (x, y).
        exit_: Exit (x, y).
        path: Shortest path cell list.
        show_path: Whether to highlight the path.
        show_42: Whether to highlight '42' cells.
        width: Maze width.
        height: Maze height.
        offset_y: Row offset for drawing.
        offset_x: Column offset for drawing.
    """
    path_set = set(path) if path and show_path else set()
    cells_42 = set(get_42_cells(width, height)) if show_42 else set()

    wall_attr = curses.color_pair(COLOR_WALL)
    bg_attr = curses.color_pair(COLOR_BACKGROUND)

    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            draw_y = offset_y + y * 2
            draw_x = offset_x + x * 4

            pos = (x, y)
            if pos == entry:
                cell_attr = curses.color_pair(COLOR_ENTRY) | curses.A_BOLD
                cell_char = "E"
            elif pos == exit_:
                cell_attr = curses.color_pair(COLOR_EXIT) | curses.A_BOLD
                cell_char = "X"
            elif pos in path_set:
                cell_attr = curses.color_pair(COLOR_PATH)
                cell_char = "·"
            elif pos in cells_42:
                cell_attr = curses.color_pair(COLOR_42) | curses.A_BOLD
                cell_char = "▪"
            else:
                cell_attr = bg_attr
                cell_char = " "

            top_wall = "---" if (cell & NORTH) else "   "
            try:
                stdscr.addstr(draw_y, draw_x, "+", wall_attr)
                stdscr.addstr(draw_y, draw_x + 1, top_wall, wall_attr)
            except curses.error:
                pass

            left_wall = "|" if (cell & WEST) else " "
            try:
                stdscr.addstr(draw_y + 1, draw_x, left_wall, wall_attr)
                stdscr.addstr(draw_y + 1, draw_x + 1, f" {cell_char} ", cell_attr)
            except curses.error:
                pass

        last_cell = maze[y][width - 1]
        draw_y = offset_y + y * 2
        draw_x_end = offset_x + width * 4
        right_wall = "|" if (last_cell & EAST) else " "
        try:
            stdscr.addstr(draw_y, draw_x_end, "+", wall_attr)
            stdscr.addstr(draw_y + 1, draw_x_end, right_wall, wall_attr)
        except curses.error:
            pass

    bottom_y = offset_y + height * 2
    for x in range(width):
        cell = maze[height - 1][x]
        draw_x = offset_x + x * 4
        bot_wall = "---" if (cell & SOUTH) else "   "
        try:
            stdscr.addstr(bottom_y, draw_x, "+", wall_attr)
            stdscr.addstr(bottom_y, draw_x + 1, bot_wall, wall_attr)
        except curses.error:
            pass
    try:
        stdscr.addstr(bottom_y, offset_x + width * 4, "+", wall_attr)
    except curses.error:
        pass


def draw_menu(
    stdscr: "curses._CursesWindow",
    menu_y: int,
    show_path: bool,
    show_42: bool,
    theme_index: int
) -> None:
    """Draw the interactive menu below the maze.

    Args:
        stdscr: Curses screen.
        menu_y: Row to start drawing menu.
        show_path: Current path visibility state.
        show_42: Current '42' highlight state.
        theme_index: Current wall color theme index.
    """
    menu_attr = curses.color_pair(COLOR_MENU)
    hint_attr = curses.color_pair(COLOR_WALL)

    path_label = "Hide Path" if show_path else "Show Path"
    color42_label = "Hide 42 Color" if show_42 else "Show 42 Color"
    theme_name = THEME_NAMES[theme_index % len(THEME_NAMES)]

    try:
        stdscr.addstr(menu_y, 0, " ==== A-Maze-ing ==== ", menu_attr)
        stdscr.addstr(menu_y + 1, 0,
                      f" [R] Re-generate   [P] {path_label}   "
                      f"[C] Wall Color ({theme_name})   "
                      f"[4] {color42_label}   [Q] Quit ",
                      hint_attr)
    except curses.error:
        pass


def display_maze(
    maze: List[List[int]],
    entry: Tuple[int, int] = (0, 0),
    exit_: Optional[Tuple[int, int]] = None,
    maze_width: Optional[int] = None,
    maze_height: Optional[int] = None,
    perfect: bool = True,
    seed: Optional[int] = None
) -> None:
    """Display maze interactively with full user controls.

    Supports:
        - R: Re-generate maze
        - P: Show/hide shortest path
        - C: Cycle wall colors
        - 4: Show/hide '42' pattern highlight
        - Q: Quit

    Args:
        maze: Initial 2D wall bitmask grid.
        entry: Entry (x, y) coordinates.
        exit_: Exit (x, y) coordinates.
        maze_width: Width for re-generation (uses current if None).
        maze_height: Height for re-generation (uses current if None).
        perfect: Use perfect maze for re-generation.
        seed: Initial seed (None = random).
    """
    height = len(maze)
    width = len(maze[0]) if height > 0 else 0
    mw = maze_width if maze_width is not None else width
    mh = maze_height if maze_height is not None else height

    if exit_ is None:
        exit_ = (width - 1, height - 1)

    def main(stdscr: "curses._CursesWindow") -> None:
        """Main curses loop."""
        nonlocal maze, width, height, seed

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        theme_index = 0
        init_colors(theme_index)

        show_path = False
        show_42 = False
        current_seed = seed

        path = find_shortest_path(maze, entry, exit_)

        while True:
            stdscr.clear()
            max_y, max_x = stdscr.getmaxyx()

            draw_maze(
                stdscr, maze, entry, exit_, path,
                show_path, show_42, width, height
            )

            menu_y = height * 2 + 2
            if menu_y + 2 < max_y:
                draw_menu(stdscr, menu_y, show_path, show_42, theme_index)

            stdscr.refresh()

            key = stdscr.getch()
            ch = chr(key).upper() if 0 <= key < 256 else ""

            if ch == "Q":
                break

            elif ch == "R":
                current_seed = (
                    random.randint(0, 999999)
                    if current_seed is None
                    else current_seed + 1
                )
                maze = generate_maze(
                    mw, mh, entry, exit_, perfect, current_seed
                )
                embed_42_pattern(maze, mw, mh, entry, exit_)
                width = mw
                height = mh
                path = find_shortest_path(maze, entry, exit_)

            elif ch == "P":
                show_path = not show_path

            elif ch == "C":
                theme_index = (theme_index + 1) % len(WALL_COLOR_THEMES)
                init_colors(theme_index)

            elif ch == "4":
                show_42 = not show_42

    curses.wrapper(main)