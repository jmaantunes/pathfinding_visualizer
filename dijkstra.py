import heapq
import math
import pygame
import sys

# pygame
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30
SQUARE_WIDTH = WIDTH // GRID_SIZE
SQUARE_HEIGHT = HEIGHT // GRID_SIZE

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dijkstra visualization")

# dijkstra
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (79, 158, 82)
LGREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (125, 125, 125)

BG = 0
WALL = 1
START = 2
END = 3
EXPLORING = 4
EXPLORED = 5
PATH = 6

colors = {
    BG: WHITE,
    WALL: BLACK,
    START: CYAN,
    END: BLUE,
    EXPLORING: LGREEN,
    EXPLORED: GREEN,
    PATH: RED
}

grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
start_x = start_y = 3
end_x = end_y = GRID_SIZE - 3

grid[start_x][start_y] = START
grid[end_x][end_y] = END


def dijkstra():
    adj_only = False
    if adj_only:
        neighbor_pos = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # adjacent nodes only
        distance_to_neighbor = [10, 10, 10, 10]
    else:
        neighbor_pos = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]  # adj and diagonal
        distance_to_neighbor = [10, 14, 10, 14, 10, 14, 10, 14]

    queue = [(0, (start_x, start_y))]  # create a priority queue
    distances = [[math.inf] * GRID_SIZE for _ in range(GRID_SIZE)]  # distances set to infinity
    visited = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]  # visited nodes
    distances[start_x][start_y] = 0

    while queue:
        current_distance, (x, y) = heapq.heappop(queue)  # Pop the node with the shortest distance
        if visited[x][y]:
            continue

        visited[x][y] = True

        # Check if the end node is reached, reconstruct the path from end to start
        if x == end_x and y == end_y:
            print("End node reached!")

            path = [(x, y)]
            while (x, y) != (start_x, start_y):
                for i, (neighbor_x, neighbor_y) in enumerate(neighbor_pos):
                    nx = x + neighbor_x
                    ny = y + neighbor_y
                    dist_to_neighbor = distance_to_neighbor[i]
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and visited[nx][ny] \
                            and distances[nx][ny] + dist_to_neighbor == distances[x][y]:
                        x, y = nx, ny
                        path.append((x, y))

            print("Shortest path:", path)
            for path_x, path_y in path:
                # color final path
                grid[path_x][path_y] = PATH

                # update the display
                draw_grid()
                pygame.display.update()
                pygame.time.delay(40)
            return

        # explore node
        for i, (neighbor_x, neighbor_y) in enumerate(neighbor_pos):
            nx = x + neighbor_x
            ny = y + neighbor_y
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[nx][ny] != WALL and not visited[nx][ny]:

                dist_to_neighbor = distance_to_neighbor[i]
                new_distance = current_distance + dist_to_neighbor
                if new_distance < distances[nx][ny]:
                    # color as exploring
                    grid[nx][ny] = EXPLORING

                    distances[nx][ny] = new_distance
                    heapq.heappush(queue, (new_distance, (nx, ny)))

        # color as explored
        grid[x][y] = EXPLORED

        # update the display
        draw_grid()
        pygame.display.update()
        pygame.time.delay(10)

    # if this point is reached without finding the end node, no sol was found.
    print("No solution found.")


def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            color = colors[grid[x][y]]
            pygame.draw.rect(window, color, (x * SQUARE_WIDTH, y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    # always draw start and end
    pygame.draw.rect(window, CYAN, (start_x * SQUARE_WIDTH, start_y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))
    pygame.draw.rect(window, BLUE, (end_x * SQUARE_WIDTH, end_y * SQUARE_HEIGHT, SQUARE_WIDTH, SQUARE_HEIGHT))

    for x in range(GRID_SIZE):
        pygame.draw.line(window, BLACK, (x * SQUARE_WIDTH, 0), (x * SQUARE_WIDTH, HEIGHT))
    for y in range(GRID_SIZE):
        pygame.draw.line(window, BLACK, (0, y * SQUARE_HEIGHT), (WIDTH, y * SQUARE_HEIGHT))


# Main loop
running = True
drawing_wall = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                print("Running dijkstra algo.")
                dijkstra()
            elif event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                drawing_wall = True

        if event.type == pygame.MOUSEMOTION:
            if drawing_wall:
                x, y = pygame.mouse.get_pos()
                x //= SQUARE_WIDTH
                y //= SQUARE_HEIGHT
                grid[x][y] = 1

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                drawing_wall = False

    window.fill(WHITE)
    draw_grid()
    pygame.display.flip()

pygame.quit()
sys.exit()
