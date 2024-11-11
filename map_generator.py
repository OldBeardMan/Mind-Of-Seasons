import random
import os

def generate_path(grid, width, height, path_length, level):

    #początek scieżki
    x, y = random.randint(0,width), random.randint(0,height)

    #licznik długosci fragmentu sciezki
    count_vertical = 0
    count_horizontal = 0

    vertical = True #pionowo
    horizontal = False #poziomo

    direction = 1

    for _ in range(path_length):
        if vertical:
            newx, newy = x + direction, y
            try:
                grid[newx][newy - 1] = "1"
                grid[newx][newy] = "1"
                grid[newx][newy + 1] = "1"
            except IndexError:
                break

            count_vertical += 1
            x, y = newx, random.randint(newy -1, newy + 1)
        else:
            newx, newy = x, y + direction
            try:
                grid[newx - 1][newy] = "1"
                grid[newx][newy] = "1"
                grid[newx + 1][newy] = "1"
            except IndexError:
                break

            count_horizontal += 1
            x, y = random.randint(newx - 1, newx + 1), newy

        #zmiana z pionowo na poziomo
        if vertical and count_vertical >= level:
            rand = random.randint(0, 1)
            if rand == 0:
                way = -1
            else:
                way = 1
            # z pionowo na poziomo naroznik
            try:
                grid[x][newy - 1] = "1"
                grid[x][newy] = "1"
                grid[x][newy + 1] = "1"
                grid[x + direction][newy] = "1"
                grid[x + direction][newy + way] = "1"
                grid[x + 2*direction][newy + way] = "1"
                x,y= x+direction, newy+way
            except IndexError:
                break
            direction = way
            vertical = False
            horizontal = True
            count_vertical = 0

        if horizontal and count_horizontal >= level:
            rand = random.randint(0, 1)
            if rand == 0:
                way = -1
            else:
                way = 1
            # z poziomo na pionowo naroznik
            try:
                grid[newx - 1][y] = "1"
                grid[newx][y] = "1"
                grid[newx + 1][y] = "1"
                grid[newx][y + direction] = "1"
                grid[newx + way][y + direction] = "1"
                grid[newx + way][y + 2 * direction] = "1"
                x, y = newx + way, y + direction
            except IndexError:
                break
            direction = way
            vertical = True
            horizontal = False
            count_horizontal = 0
    return grid

def save_map_to_file(grid, filename):
    with open(filename, "w") as file:
        for row in grid:
            line = ''.join(str(cell) for cell in row)
            file.write(line + "\n")

def map_initialization(width, height, file="map.txt" , path_length=30, path_level=10, paths_number=6):
    if not os.path.isfile(file):
        layout = [["0" for _ in range(width)] for _ in range(height)]

        for _ in range(paths_number):
            layout = generate_path(layout, width, height, path_length, path_level)

        save_map_to_file(layout, file)