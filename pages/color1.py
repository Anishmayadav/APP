import pygame
import sys
import asyncio # <--- ADD THIS

pygame.init()
WIDTH, HEIGHT = 600, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Tracker 1")
color = (100, 150, 255)

# 1. CHANGE: Define the main loop as an asynchronous function
async def main(): 
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Note: KEYDOWN is often not captured correctly in the web environment 
            # as the browser handles those events differently.

        window.fill(color)
        pygame.display.update()

        # 2. ADD THIS: Yield control back to the event loop
        await asyncio.sleep(0) 

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    # 3. CHANGE: Run the main loop using asyncio
    asyncio.run(main())
