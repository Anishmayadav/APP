import pygame
import sys

# Initialize Pygame
pygame.init()

# Window size
WIDTH, HEIGHT = 600, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Color Display")

# Choose a color (R, G, B)
color = (100, 150, 255)  # Light Blue

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:       # Window close
            running = False
        if event.type == pygame.KEYDOWN:    # Any key press
            running = False

    window.fill(color)  # Fill the screen with the chosen color
    pygame.display.update()

# Quit
pygame.quit()
sys.exit()
