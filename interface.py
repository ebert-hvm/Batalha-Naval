import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 800
GRID_SIZE = 10
CELL_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 80
BUTTON_COLOR = (50, 50, 50)
BUTTON_TEXT_COLOR = WHITE
BUTTON_TEXT = "Clear Grid"

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")

# Main game loop
running = True
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Function to clear the grid
def clear_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            grid[row][col] = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (1)
                x, y = event.pos
                if x < CELL_SIZE * GRID_SIZE and y < CELL_SIZE * GRID_SIZE:
                    grid_x = x // CELL_SIZE
                    grid_y = y // CELL_SIZE
                    grid[grid_y][grid_x] = 1
                elif CELL_SIZE * GRID_SIZE <= x <= CELL_SIZE * GRID_SIZE + BUTTON_WIDTH and HEIGHT - BUTTON_HEIGHT <= y <= HEIGHT:
                    # Clicked on the "Clear Grid" button
                    clear_grid()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the grid
    for i in range(0, CELL_SIZE * (GRID_SIZE + 1), CELL_SIZE):
        pygame.draw.line(screen, BLACK, (i, 0), (i, CELL_SIZE * GRID_SIZE))
        pygame.draw.line(screen, BLACK, (0, i), (CELL_SIZE * GRID_SIZE, i))

    # Fill cells in the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 1:
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw the "Clear Grid" button
    clear_button_rect = pygame.Rect(CELL_SIZE * GRID_SIZE, HEIGHT - BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, BUTTON_COLOR, clear_button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render(BUTTON_TEXT, True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=clear_button_rect.center)
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
