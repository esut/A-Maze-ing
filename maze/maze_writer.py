def write_maze(filename, maze, entry, exit, path):

    with open(filename, "w") as f:

        for row in maze:
            line = " ".join(format(cell, "x") for cell in row)
            f.write(line + "\n")

        f.write("\n")

        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write(path + "\n")