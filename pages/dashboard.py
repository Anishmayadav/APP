import os
os.environ["SDL_VIDEODRIVER"] = "dummy"   # Run pygame headless

import streamlit as st
import pygame
import numpy as np
from PIL import Image
import time

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 400, 300
screen = pygame.Surface((WIDTH, HEIGHT))

st.title("🎨 Simple Color Game")

colors = [
    (255, 0, 0),   # red
    (0, 255, 0),   # green
    (0, 0, 255),   # blue
    (255, 255, 0), # yellow
    (255, 0, 255), # magenta
    (0, 255, 255)  # cyan
]

if st.button("Start Game"):
    ph = st.empty()
    clock = pygame.time.Clock()

    for c in colors:     # Change color every loop
        screen.fill(c)

        # Convert pygame frame → Streamlit image
        frame = pygame.surfarray.array3d(screen)
        frame = np.rot90(frame)
        img = Image.fromarray(frame)

        ph.image(img, use_container_width=True)

        time.sleep(1)    # show each color for 1 sec
        clock.tick(30)

pygame.quit()
