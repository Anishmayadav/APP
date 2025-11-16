import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 600, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Tracker 1")
color = (100, 150, 255)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            running = False

    window.fill(color)
    pygame.display.update()

pygame.quit()
sys.exit()
