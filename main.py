import pygame
from queue import PriorityQueue


pygame.init()

WIDTH = 800
ROWS = 50
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Pathfinding algorithm')

RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Cell:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.colour = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.colour == BLACK

    def reset(self):
        self.colour = WHITE

    def make_closed(self):
        self.colour = RED

    def make_open(self):
        self.colour = GREEN

    def make_barrier(self):
        self.colour = BLACK

    def make_start(self):
        self.colour = ORANGE

    def make_end(self):
        self.colour = TURQUOISE

    def make_path(self):
        self.colour = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def is_inside(self, x, y):
        return 0 <= min(x, y) and max(x, y) < self.total_rows

    def update_neighbours(self, grid):
        di = [-1, 0, 1, 0]
        dj = [0, 1, 0, -1]

        for k in range(4):
            other_row, other_col = self.row + di[k], self.col + dj[k]

            if self.is_inside(other_row, other_col) and not grid[other_row][other_col].is_barrier():
                self.neighbours.append(grid[other_row][other_col])


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, curr, draw):
    while curr in came_from:
        curr = came_from[curr]
        curr.make_path()
        draw()


def a_star(draw, grid, start, end):
    dist = {cell: float('inf') for row in grid for cell in row}
    dist[start] = 0
    total_dist = {cell: float('inf') for row in grid for cell in row}
    total_dist[start] = h(start.get_pos(), end.get_pos())

    cnt = 0
    came_from = {}
    pq = PriorityQueue()
    pq.put((total_dist[start], cnt, start))
    in_pq = {start}

    while not pq.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        curr = pq.get()[2]
        in_pq.remove(curr)

        if curr == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        if curr != start:
            curr.make_closed()

        for neighbour in curr.neighbours:
            if dist[curr] + 1 < dist[neighbour]:
                dist[neighbour] = dist[curr] + 1
                total_dist[neighbour] = dist[neighbour] + h(neighbour.get_pos(), end.get_pos())
                came_from[neighbour] = curr

                if neighbour not in in_pq:
                    cnt += 1
                    pq.put((total_dist[neighbour], cnt, neighbour))
                    in_pq.add(neighbour)
                    neighbour.make_open()

        draw()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])

        for j in range(rows):
            cell = Cell(i, j, gap, rows)
            grid[i].append(cell)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))


def update_grid(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for cell in row:
            cell.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, rows, width):
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True

    while run:
        update_grid(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                cell: Cell = grid[row][col]

            if pygame.mouse.get_pressed()[0]:
                if not start and cell != end:
                    start = cell
                    start.make_start()
                elif not end and cell != start:
                    end = cell
                    end.make_end()
                elif cell != start and cell != end:
                    cell.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                cell.reset()

                if cell == start:
                    start = None
                elif cell == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for cell in row:
                            cell.update_neighbours(grid)

                    a_star(lambda: update_grid(win, grid, rows, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    pygame.quit()


if __name__ == '__main__':
    main(WIN, ROWS, WIDTH)
