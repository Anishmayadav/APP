import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import numpy as np
import cv2
import time
import threading
from collections import defaultdict
import math

# ---------------------------
# CONFIG
# ---------------------------
OUTPUT_FILE = r"D:/Streamlite/colorresult.txt"
WEBCAM_INDEX = 0
WIDTH, HEIGHT = 1300, 600
WEBCAM_SIZE = (200, 150)
WEBCAM_POS = (10, 10)
TIME_LIMIT = 25  

# ---------------------------
# PYGAME INIT
# ---------------------------
pygame.init()
try:
    pygame.mixer.init()
except:
    pass

FONT = pygame.font.SysFont('Arial', 30)
LARGE_FONT = pygame.font.SysFont('Arial', 72, bold=True)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ---------------------------
# ZONES
# ---------------------------
ZONE_WIDTH = WIDTH // 4
CENTER_Y = HEIGHT // 2
EYE_RADIUS = 30
PUPIL_RADIUS = 10
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (0, 0, 0)
EYE_OFFSET = 50
MOUTH_SIZE = 15

zones = [
    {'color': (255, 0, 0), 'rect': pygame.Rect(0 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Red'},
    {'color': (0, 255, 0), 'rect': pygame.Rect(1 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Green'},
    {'color': (0, 0, 255), 'rect': pygame.Rect(2 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Blue'},
    {'color': (255, 255, 0), 'rect': pygame.Rect(3 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Yellow'},
]

# ---------------------------
# STATE
# ---------------------------
hover_time = defaultdict(float)
speech_animation_end_time = 0
speaking_zone_name = None
current_zone_index = 0

# ---------------------------
# UTILS
# ---------------------------
def cvimage_to_pygame(image, size=(200,150)):
    image = cv2.resize(image, size)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.rot90(image)
    return pygame.surfarray.make_surface(image)

# ---------------------------
# AUDIO
# ---------------------------
def speak_color(name):
    global speaking_zone_name, speech_animation_end_time
    try:
        pygame.mixer.music.stop()
        speech_animation_end_time = time.time() + 2.2
        speaking_zone_name = name
    except:
        speaking_zone_name = name
        speech_animation_end_time = time.time() + 2

# ---------------------------
# FACE DRAWING
# ---------------------------
def draw_eye(surface, x, y, openness=1.0):
    pygame.draw.circle(surface, EYE_COLOR, (x, y), EYE_RADIUS)
    pygame.draw.circle(surface, PUPIL_COLOR, (x, y), PUPIL_RADIUS)

def draw_mouth(surface, x, y, speaking):
    my = y + EYE_RADIUS + MOUTH_SIZE
    if speaking:
        pygame.draw.ellipse(surface, PUPIL_COLOR, (x - MOUTH_SIZE//2, my - 5, MOUTH_SIZE, MOUTH_SIZE))
    else:
        pygame.draw.line(surface, PUPIL_COLOR, (x - MOUTH_SIZE, my), (x + MOUTH_SIZE, my), 3)

def draw_zones(surface):
    for z in zones:
        pygame.draw.rect(surface, z['color'], z['rect'])

    for z in zones:
        cx = z['rect'].left + z['rect'].width//2
        cy = CENTER_Y
        draw_eye(surface, cx - EYE_OFFSET, cy)
        draw_eye(surface, cx + EYE_OFFSET, cy)
        draw_mouth(surface, cx, cy, z['name'] == speaking_zone_name)

# ---------------------------
# FINAL SCREEN
# ---------------------------
def display_final(screen, name, rgb):
    screen.fill(WHITE)
    txt = LARGE_FONT.render(f"Preference: {name}", True, BLACK)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 80))

    pygame.draw.rect(screen, rgb, (WIDTH//2 - 100, HEIGHT//2, 200, 100))

    pygame.display.update()
    time.sleep(5)

# ---------------------------
# MAIN
# ---------------------------
def main():

    global current_zone_index, speaking_zone_name, speech_animation_end_time

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Preference (No Gaze, No Emotion)")
    clock = pygame.time.Clock()

    webcam = cv2.VideoCapture(WEBCAM_INDEX)

    start = time.time()
    speak_color(zones[current_zone_index]['name'])

    run = True
    while run:

        dt = clock.tick(30) / 1000
        elapsed = time.time() - start

        if elapsed >= TIME_LIMIT:
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        ret, frame = webcam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # switch color every 3 seconds
        if speaking_zone_name is None or time.time() > speech_animation_end_time:
            speaking_zone_name = None
            current_zone_index = (current_zone_index + 1) % len(zones)
            speak_color(zones[current_zone_index]['name'])

        # DRAW
        win.fill(WHITE)
        draw_zones(win)

        # highlight current prompting zone
        pygame.draw.rect(win, WHITE, zones[current_zone_index]['rect'], 5)

        # webcam
        cam = cvimage_to_pygame(frame, WEBCAM_SIZE)
        win.blit(cam, WEBCAM_POS)
        pygame.draw.rect(win, BLACK, (*WEBCAM_POS, *WEBCAM_SIZE), 2)

        # timer
        tleft = TIME_LIMIT - elapsed
        ttxt = FONT.render(f"Time Left: {tleft:.1f}s", True, BLACK)
        win.blit(ttxt, (WIDTH - ttxt.get_width() - 10, HEIGHT - 40))

        pygame.display.update()

    # END TEST
    webcam.release()

    # Dominant color (here all 0 — you can add manual input later)
    name = zones[current_zone_index]['name']
    rgb = zones[current_zone_index]['color']

    display_final(win, name, rgb)

    pygame.quit()


main()
