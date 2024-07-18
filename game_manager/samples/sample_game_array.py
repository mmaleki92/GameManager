import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pygame with NumPy Surface and Transparency')

# Create a NumPy array to represent the surface
width, height = 100, 100
surface_array = np.zeros((height, width, 4), dtype=np.uint8)
surface_array[..., :3] = (255, 0, 0)  # Red color
surface_array[..., 3] = np.random.randint(0, 256, (height, width), dtype=np.uint8)  # Random alpha values

# Convert NumPy array to Pygame surface
rgb_surface = pygame.surfarray.make_surface(surface_array[..., :3].transpose((1, 0, 2)))
rgb_surface = rgb_surface.convert_alpha()  # Ensure the surface supports alpha

sizex, sizey = rgb_surface.get_size()
for y in range(sizex):
    for x in range(sizey):
        rgb_surface.set_at((x, y), (*surface_array[y, x, :3], surface_array[y, x, 3]))

# Main game loop
running = True
clock = pygame.time.Clock()
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
dx, dy = 5, 5  # Speed of the rectangle

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the rectangle
    x += dx
    y += dy

    # Bounce off the edges
    if x < 0 or x + width > SCREEN_WIDTH:
        dx = -dx
    if y < 0 or y + height > SCREEN_HEIGHT:
        dy = -dy

    # Fill the screen with white
    screen.fill(WHITE)

    # Blit the NumPy surface onto the screen
    screen.blit(rgb_surface, (x, y))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
