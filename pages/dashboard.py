import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import streamlit as st
import pygame
import numpy as np
import time

def run():
    pygame.init()
    WIDTH, HEIGHT = 400, 300
    screen = pygame.Surface((WIDTH, HEIGHT))

    st.subheader("Simple Color Game")

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255)
    ]

    if st.button("Start Game"):
        ph = st.empty()
        clock = pygame.time.Clock()

        for c in colors:
            screen.fill(c)

            frame = pygame.surfarray.array3d(screen)
            frame = np.swapaxes(frame, 0, 1)

            ph.image(frame)

            time.sleep(1)
            clock.tick(30)

    pygame.quit()
