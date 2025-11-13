import os
import streamlit as st
import pygame
import numpy as np
from PIL import Image
import time

# --- Important: Run Pygame in headless mode ---
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
screen = pygame.Surface((600, 400))
color = (255, 0, 0)

st.title("🎮 Pygame Color Game inside Streamlit")

start_button = st.button("Start Game")

if start_button:
    placeholder = st.empty()
    running = True
    frame_rate = 30
    clock = pygame.time.Clock()
    start_time = time.time()

    while running:
        # Fill the screen with color
        screen.fill(color)

        # Convert to NumPy array for display
        image_array = pygame.surfarray.array3d(screen)
        image_array = np.rot90(image_array)
        img = Image.fromarray(image_array)

        placeholder.image(img, caption="Color Game Running...", use_container_width=True)

        clock.tick(frame_rate)

        # Run for ~10 seconds as demo
        if time.time() - start_time > 10:
            running = False

pygame.quit()
