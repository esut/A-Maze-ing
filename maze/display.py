
import curses
from typing import List

def display_maze(maze: List[List[int]]):

    def main(stdscr):
        curses.curs_set(0)  
        stdscr.clear()
        height = len(maze)
        width = len(maze[0])

        for y in range(height):
            top = ""
            mid = ""
            for x in range(width):
                cell = maze[y][x]
                top += "+---" if cell & 1 else "+   "
                mid += "|   " if cell & 8 else "    "

          
            stdscr.addstr(y*2, 0, top + "+")
            stdscr.addstr(y*2 + 1, 0, mid + "|")

        
        stdscr.addstr(height*2, 0, "+---" * width + "+")
        stdscr.refresh()
        stdscr.getch() 

    curses.wrapper(main)