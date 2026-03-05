def display_maze(maze):

    height = len(maze)
    width = len(maze[0])

    for y in range(height):

        top = ""
        mid = ""

        for x in range(width):

            cell = maze[y][x]

            top += "+---" if cell & 1 else "+   "

            mid += "|   " if cell & 8 else "    "

        print(top + "+")
        print(mid + "|")

    print("+---" * width + "+")