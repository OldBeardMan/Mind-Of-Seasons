import random


def generate_pattern(width=50, height=50, path_length=40,path_width=3, level = 10):
    # Inicjalizacja siatki
    grid = [["0" for _ in range(width)] for _ in range(height)]

    x, y = 10,10
    count_vertical = 0
    count_horizontal = 0

    vertical = True #pionowo
    horizontal = False #poziomo
    direction = 0 # 0-pionowo, 1-poziomo

    for _ in range(path_length):
        if vertical:
            newx, newy = x + 1, y
            seg = random.randint(0, path_width-1)
            if newx in range(width) and newy + path_width in range(height):
                grid[newx][newy - 1] = "1"
                grid[newx][newy] = "1"
                grid[newx][newy + 1] = "1"

            count_vertical += 1
            x, y = newx, random.randint(newy +1 - seg, newy + path_width-2 - seg)
        else:
            newx, newy = x, y + 1
            seg = random.randint(0, path_width - 1)
            if newx + path_width in range(width) and newy in range(height):
                grid[newx - 1][newy] = "1"
                grid[newx][newy] = "1"
                grid[newx + 1][newy] = "1"

            count_horizontal += 1
            x, y = random.randint(newx + 1 - seg, newx + path_width - 2 - seg), newy

        direction = random.randint(0, 1)
        #zmiana z pionowo na poziomo
        if direction == 1 and vertical and count_vertical >= level:
            # z pionowo na poziomo w prawo
            if newy + 2 in range(height):
                grid[x][newy - 1] = "1"
                grid[x][newy] = "1"
                grid[x][newy + 1] = "1"
                grid[x+1][newy] = "1"
                grid[x + 1][newy + 1] = "1"
                grid[x + 2][newy +1] = "1"
                x,y= x+1, newy+1
            vertical = False
            horizontal = True
            count_vertical = 0

        if direction == 0 and horizontal and count_horizontal >= level:
            print("koniec")
            break

    for i in range(height):
        for j in range(width):
            print(grid[i][j], end="")
        print()

generate_pattern()