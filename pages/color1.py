import os
os.environ["SDL_VIDEODRIVER"] = "dummy"





import os
import pygame
import numpy as np
import cv2
import time
from collections import defaultdict
import math

# Set dummy video driver for headless environments like some servers
# os.environ["SDL_VIDEODRIVER"] = "dummy" 

# ---------------------------
# CONFIG
# ---------------------------
# IMPORTANT: Update OUTPUT_FILE path if running in a real environment
OUTPUT_FILE = "colorresult.txt"
WEBCAM_INDEX = 0
WIDTH, HEIGHT = 1300, 600
WEBCAM_SIZE = (200, 150)
WEBCAM_POS = (10, 10)
TIME_LIMIT = 25              # total test duration in seconds
PROMPT_DURATION = 3.0        # how long each color is prompted before switching (sec)

# ---------------------------
# PYGAME INIT
# ---------------------------
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    # audio may fail in headless envs - ignore
    pass

FONT = pygame.font.SysFont('Arial', 30)
LARGE_FONT = pygame.font.SysFont('Arial', 72, bold=True)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ---------------------------
# ZONES
# ---------------------------
ZONE_WIDTH = WIDTH // 4

zones = [
    {'color': (255, 0, 0),   'rect': pygame.Rect(0 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Red'},
    {'color': (0, 255, 0),   'rect': pygame.Rect(1 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Green'},
    {'color': (0, 0, 255),   'rect': pygame.Rect(2 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Blue'},
    {'color': (255, 255, 0), 'rect': pygame.Rect(3 * ZONE_WIDTH, 0, ZONE_WIDTH, HEIGHT), 'name': 'Yellow'},
]

# ---------------------------
# STATE
# ---------------------------
# Records how long each color was the active prompt.
prompt_time = defaultdict(float)    
current_zone_index = 0

# ---------------------------
# UTILS
# ---------------------------
def cvimage_to_pygame(image, size=(200,150)):
    """Convert an OpenCV BGR image to a Pygame surface (RGB)."""
    image = cv2.resize(image, size)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.rot90(image)
    return pygame.surfarray.make_surface(image)

# ---------------------------
# ZONE DRAWING (Simplified)
# ---------------------------
def draw_zones(surface):
    """Draws only the colored rectangles, removing all face/gaze elements."""
    for z in zones:
        pygame.draw.rect(surface, z['color'], z['rect'])

# ---------------------------
# FINAL SCREEN & REPORT
# ---------------------------
def display_final(screen, name, rgb):
    """Displays the final dominant color preference."""
    bg = rgb if name != "N/A" else (150,150,150)
    # Determine text color for readability based on background
    text_color = WHITE if sum(bg) < 380 else BLACK 
    screen.fill(bg)
    
    txt = LARGE_FONT.render(f"Preference: {name}", True, text_color)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 80))
    
    # Draw a sample block of the preferred color
    pygame.draw.rect(screen, rgb, (WIDTH//2 - 100, HEIGHT//2, 200, 100))
    
    instr = FONT.render("Press any key or close window to exit.", True, text_color)
    screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT - 60))
    pygame.display.update()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                waiting = False
            if ev.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.Clock().tick(15)

def write_report(output_path, prompt_time, total_duration):
    """Writes the final time-spent report."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    except Exception:
        # Ignore issues with path creation if running in restricted env
        pass

    total_recorded = sum(prompt_time.values())
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("Color Prompting Summary (Time-Based Presentation)\n")
            f.write(f"Test Duration (configured): {total_duration:.1f} s\n")
            f.write(f"Total Prompted Time (measured): {total_recorded:.2f} s\n\n")
            if total_recorded > 0:
                dominant = max(prompt_time, key=prompt_time.get)
                f.write(f"--- DOMINANT PROMPT: {dominant} ---\n\n")
                f.write("--- TIME SPENT PER COLOR ---\n")
                for z in zones:
                    t = prompt_time.get(z['name'], 0.0)
                    perc = (t / total_recorded * 100) if total_recorded > 0 else 0.0
                    f.write(f"{z['name']}: {t:.2f} s ({perc:.1f}%)\n")
            else:
                f.write("No prompt time recorded.\n")
    except Exception as e:
        print(f"Error writing report: {e}")

# ---------------------------
# MAIN
# ---------------------------
def main():
    global current_zone_index

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Preference (Timed Presentation)")
    clock = pygame.time.Clock()

    webcam = cv2.VideoCapture(WEBCAM_INDEX)
    cam_available = webcam.isOpened()

    start_time = time.time()
    last_switch_time = start_time
    
    # We don't need speak_color or animation logic anymore

    run = True
    while run:
        dt = clock.tick(30) / 1000.0
        elapsed = time.time() - start_time

        # Accumulate prompt time for the currently active color
        current_name = zones[current_zone_index]['name']
        prompt_time[current_name] += dt

        # End when TIME_LIMIT reached
        if elapsed >= TIME_LIMIT:
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Optional: allow user to press 1-4 to jump to that color prompt immediately
            if event.type == pygame.KEYDOWN:
                key_index = -1
                if event.key == pygame.K_1: key_index = 0
                elif event.key == pygame.K_2: key_index = 1
                elif event.key == pygame.K_3: key_index = 2
                elif event.key == pygame.K_4: key_index = 3
                
                if key_index != -1 and key_index < len(zones):
                    current_zone_index = key_index
                    last_switch_time = time.time()

        # Automatic prompt switching every PROMPT_DURATION seconds
        if time.time() - last_switch_time >= PROMPT_DURATION:
            current_zone_index = (current_zone_index + 1) % len(zones)
            last_switch_time = time.time()

        # DRAW
        win.fill(WHITE)
        draw_zones(win)

        # Highlight current prompting zone with a white border
        pygame.draw.rect(win, WHITE, zones[current_zone_index]['rect'], 5)

        # Webcam small preview (if available)
        if cam_available:
            ret, frame = webcam.read()
            if ret:
                frame = cv2.flip(frame, 1)
                cam_surf = cvimage_to_pygame(frame, WEBCAM_SIZE)
                win.blit(cam_surf, WEBCAM_POS)
                pygame.draw.rect(win, BLACK, (*WEBCAM_POS, *WEBCAM_SIZE), 2)
        else:
            # draw a placeholder rectangle
            pygame.draw.rect(win, (200,200,200), (*WEBCAM_POS, *WEBCAM_SIZE))
            no_cam_txt = FONT.render("No Camera", True, (100,100,100))
            win.blit(no_cam_txt, (WEBCAM_POS[0] + 10, WEBCAM_POS[1] + 10))
            pygame.draw.rect(win, BLACK, (*WEBCAM_POS, *WEBCAM_SIZE), 2)

        # Timer
        tleft = max(0.0, TIME_LIMIT - elapsed)
        ttxt = FONT.render(f"Time Left: {tleft:.1f}s", True, BLACK)
        win.blit(ttxt, (WIDTH - ttxt.get_width() - 10, HEIGHT - 40))

        # Current prompt label
        current_label = FONT.render(f"Prompting: {zones[current_zone_index]['name']}", True, BLACK)
        win.blit(current_label, (10, HEIGHT - 40))

        pygame.display.update()

    # cleanup
    try:
        if cam_available:
            webcam.release()
    except Exception:
        pass

    # determine dominant
    total_prompted = sum(prompt_time.values())
    if total_prompted > 0:
        dominant_name = max(prompt_time, key=prompt_time.get)
        dominant_rgb = next((z['color'] for z in zones if z['name'] == dominant_name), (150,150,150))
    else:
        dominant_name = "N/A"
        dominant_rgb = (150,150,150)

    # show final screen and write report
    display_final(win, dominant_name, dominant_rgb)
    write_report(OUTPUT_FILE, prompt_time, TIME_LIMIT)

    pygame.quit()

if __name__ == "__main__":
    main()
