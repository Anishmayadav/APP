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

st.title("🎮 Mini Pygame Demo in Streamlit")

if st.button("Start Game"):
    placeholder = st.empty()
    color = (255, 0, 0)
    clock = pygame.time.Clock()
    start = time.time()

    while time.time() - start < 5:  # Run for 5 seconds
        screen.fill(color)

        # Convert pygame surface → numpy → PIL image
        frame = pygame.surfarray.array3d(screen)
        frame = np.rot90(frame)
        img = Image.fromarray(frame)

        placeholder.image(img, use_container_width=True)

        clock.tick(30)  # 30 FPS

pygame.quit()
