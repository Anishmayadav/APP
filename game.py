import streamlit as st
import pygame
import numpy as np
from PIL import Image
import time

# Initialize Pygame (no visible window)
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

    while running:
        # Handle events (simulate quit on stop button)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill screen with color
        screen.fill(color)

        # Convert Pygame surface to displayable image
        image_array = pygame.surfarray.array3d(screen)
        image_array = np.rot90(image_array)
        img = Image.fromarray(image_array)

        # Show frame in Streamlit
        placeholder.image(img)

        # Maintain frame rate
        clock.tick(frame_rate)

        # Stop after 10 seconds for demo
        if time.time() - st.session_state.get("start_time", time.time()) > 10:
            running = False

pygame.quit()
