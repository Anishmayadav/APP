import os
os.environ["SDL_VIDEODRIVER"] = "dummy"





import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Simple Color Window")

    # Set color here (R, G, B)
    color = (135, 206, 250)   # Light sky blue

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(color)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
