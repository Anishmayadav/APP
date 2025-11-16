import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import streamlit as st
import pygame
import numpy as np
import time

import pygame
import time
from collections import defaultdict
import math
import numpy as np
import threading

# ---------------------------
# CONFIG
# ---------------------------
OUTPUT_FILE = r"D:/Streamlite/colorresult.txt" # change if needed
WEBCAM_INDEX = 0
WIDTH, HEIGHT = 1300, 600
WEBCAM_SIZE = (200, 150)
WEBCAM_POS = (10, 10)
TIME_LIMIT = 25 # seconds for the test
EMOTION_INTERVAL = 5 # analyze one frame every N frames
GAZE_SMOOTHING_SIZE = 8
MIN_GAZE_CONFIDENCE = 0.3 # Unused in current code, but kept for context

# ---------------------------
# PYGAME INIT
# ---------------------------
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    # mixer may fail on some headless machines; proceed without audio playback
    pass

FONT = pygame.font.SysFont('Arial', 30)
LARGE_FONT = pygame.font.SysFont('Arial', 72, bold=True)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# ---------------------------
# ZONES
# ---------------------------
ZONE_WIDTH = WIDTH // 4
CENTER_Y = HEIGHT // 2
EYE_RADIUS = 30
PUPIL_RADIUS = 10
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (0, 0, 0)
BLINK_SPEED = 2.0
EYE_OFFSET = 50
MOUTH_SIZE = 15
GAZE_DOT_RADIUS = 8

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
emotion_data_log = defaultdict(lambda: defaultdict(float)) # emotion_data_log[color][emotion] = time
gaze_history = []
current_time = 0.0
gaze_point = None
current_gazed_zone_name = None
speech_animation_end_time = 0.0
speaking_zone_name = None
last_zone_change_time = 0
current_zone_index = 0

# Emotion thread variables
emotion_detection_queue = []
emotion_thread_running = False
emotion_lock = threading.Lock()
current_emotion = "Loading..."
emotion_frame_counter = 0

# ---------------------------
# UTILS
# ---------------------------
def cvimage_to_pygame(image, size=(200, 150)):
    """Convert OpenCV BGR image to Pygame surface."""
    image = cv2.resize(image, size)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.rot90(image) # rotate so surfarray makes correct orientation
    surface = pygame.surfarray.make_surface(image)
    return surface

def get_gaze_coordinates(gaze):
    """Map gaze library output to screen coordinates (best-effort)."""
    try:
        horizontal_ratio = gaze.horizontal_ratio()
    except Exception:
        horizontal_ratio = None

    if horizontal_ratio is not None:
        screen_x = int(horizontal_ratio * WIDTH)
        pupil_left = gaze.pupil_left_coords()
        pupil_right = gaze.pupil_right_coords()
        if pupil_left is not None and pupil_right is not None:
            # Simple average of normalized pupil Y coordinates. Needs tuning for accuracy.
            avg_y = (pupil_left[1] + pupil_right[1]) / 2
            # Assuming a pupil Y coordinate of ~240 in a 480px frame maps roughly to the center of our HEIGHT
            screen_y = int(avg_y * HEIGHT / 480)
        else:
            screen_y = HEIGHT // 2
        return (screen_x, screen_y)

    pupil_coords = gaze.pupil_left_coords() or gaze.pupil_right_coords()
    if pupil_coords is not None:
        px, py = pupil_coords
        # Fallback mapping based on raw pupil coordinates
        screen_x = int(px * WIDTH / 640)
        screen_y = int(py * HEIGHT / 480)
        return (screen_x, screen_y)

    return None

def is_gaze_reliable(gaze):
    """Basic checks for whether gaze is reliable."""
    try:
        if gaze.pupil_left_coords() is None and gaze.pupil_right_coords() is None:
            return False
        if gaze.is_blinking():
            return False
    except Exception:
        return False
    return True

def smooth_gaze(history, new_point, size=GAZE_SMOOTHING_SIZE):
    if new_point is None:
        return history[-1] if history else None
    history.append(new_point)
    if len(history) > size:
        history.pop(0)
    if len(history) >= 2:
        avg_x = sum(p[0] for p in history) / len(history)
        avg_y = sum(p[1] for p in history) / len(history)
        return (int(avg_x), int(avg_y))
    return new_point

# ---------------------------
# AUDIO
# ---------------------------
def create_audio_files():
    for zone in zones:
        audio_file = f"{zone['name'].lower()}.mp3"
        if not os.path.exists(audio_file):
            try:
                tts = gTTS(text=f"I am {zone['name']} color", lang='en')
                tts.save(audio_file)
            except Exception:
                # Handle gTTS errors (e.g., no network) gracefully
                pass

def speak_color(color_name):
    global speech_animation_end_time, speaking_zone_name
    try:
        pygame.mixer.music.stop()
        audio_file = f"{color_name.lower()}.mp3"
        if os.path.exists(audio_file):
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            # Set animation time based on a safe estimate or actual length
            speech_animation_end_time = time.time() + 2.5
            speaking_zone_name = color_name
        else:
            # Fallback for systems without gTTS files or without mixer
            speech_animation_end_time = time.time() + 2.0
            speaking_zone_name = color_name
    except Exception:
        speech_animation_end_time = time.time() + 2.0
        speaking_zone_name = color_name

# ---------------------------
# DRAWING
# ---------------------------
def draw_eye(surface, center_x, center_y, eye_openness_factor):
    current_eye_height = int(EYE_RADIUS * eye_openness_factor)
    if current_eye_height > 1:
        # Draw the white eyeball
        pygame.draw.circle(surface, EYE_COLOR, (center_x, center_y), EYE_RADIUS)
        # Draw the black pupil
        pygame.draw.circle(surface, PUPIL_COLOR, (center_x, center_y), PUPIL_RADIUS)
        # Draw the eyelid shape (a simplistic way to visualize the blink/speech animation)
        ellipse_rect = pygame.Rect(center_x - EYE_RADIUS, center_y - current_eye_height,
                                   EYE_RADIUS * 2, current_eye_height * 2)
        pygame.draw.ellipse(surface, PUPIL_COLOR, ellipse_rect, 2)

def draw_mouth(surface, center_x, center_y, is_speaking):
    mouth_y = center_y + EYE_RADIUS + MOUTH_SIZE * 0.8
    if is_speaking:
        # Open mouth for speaking
        mouth_rect = pygame.Rect(center_x - MOUTH_SIZE // 2, mouth_y - MOUTH_SIZE // 2,
                                 MOUTH_SIZE, MOUTH_SIZE)
        pygame.draw.ellipse(surface, PUPIL_COLOR, mouth_rect, 0)
    else:
        # Closed/neutral mouth
        start_pos = (center_x - MOUTH_SIZE, mouth_y)
        end_pos = (center_x + MOUTH_SIZE, mouth_y)
        pygame.draw.line(surface, PUPIL_COLOR, start_pos, end_pos, 2)

def draw_zones_and_eyes(surface, speaking_zone_name, current_time):
    # Global 'natural' blink animation
    blink_sin_wave = (math.sin(current_time * BLINK_SPEED * math.pi) + 1) / 2
    global_blink_animation_factor = 0.5 + (blink_sin_wave * 0.5)
    
    # Draw the colored zones
    for zone in zones:
        pygame.draw.rect(surface, zone['color'], zone['rect'])

    # Draw the 'face' elements over each zone
    for zone in zones:
        center_zone_x = zone['rect'].left + zone['rect'].width // 2
        center_y = CENTER_Y
        left_eye_x = center_zone_x - EYE_OFFSET
        right_eye_x = center_zone_x + EYE_OFFSET
        
        is_speaking_color = (zone['name'] == speaking_zone_name)
        
        # Eyes animate based on speaking status
        eye_openness_factor = global_blink_animation_factor if is_speaking_color else 1.0
        
        draw_eye(surface, left_eye_x, center_y, eye_openness_factor)
        draw_eye(surface, right_eye_x, center_y, eye_openness_factor)
        draw_mouth(surface, center_zone_x, center_y, is_speaking_color)

# ---------------------------
# EMOTION THREAD
# ---------------------------
def emotion_worker():
    global current_emotion, emotion_thread_running
    emotion_thread_running = True
    while emotion_thread_running:
        frame_for_analysis = None
        with emotion_lock:
            if emotion_detection_queue:
                # Get the oldest frame from the queue
                frame_for_analysis = emotion_detection_queue.pop(0) 
        
        if frame_for_analysis is not None:
            detected = "No Face"
            try:
                # Use enforce_detection=False so it doesn't crash when no face is found
                analysis_result = DeepFace.analyze(frame_for_analysis, actions=['emotion'], enforce_detection=False, silent=True)
                
                # DeepFace may return a dict (single face) or a list (multiple/no face)
                if isinstance(analysis_result, list) and len(analysis_result) > 0 and 'dominant_emotion' in analysis_result[0]:
                    val = analysis_result[0]
                elif isinstance(analysis_result, dict) and 'dominant_emotion' in analysis_result:
                    val = analysis_result
                else:
                    val = None

                if val and 'dominant_emotion' in val and val['dominant_emotion']:
                    detected = str(val['dominant_emotion']).upper()
                elif val and 'emotion' in val and isinstance(val['emotion'], dict):
                    # Fallback: pick highest value in emotion dict
                    detected = max(val['emotion'].items(), key=lambda x: x[1])[0].upper()
                else:
                    detected = "No Face"
            except Exception:
                detected = "Error"

            with emotion_lock:
                current_emotion = detected

        # Process at a lower rate (e.g., ~15 fps) to save CPU
        time.sleep(1 / 15) 

# ---------------------------
# MAIN
# ---------------------------
def main():
    global current_time, speech_animation_end_time, speaking_zone_name, current_zone_index, last_zone_change_time
    global gaze_point, current_gazed_zone_name, current_emotion, emotion_frame_counter, gaze_history, emotion_thread_running

    # Setup window & camera
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Color Preference Tracker - Gaze & Emotion Detection")
    CLOCK = pygame.time.Clock()

    gaze = GazeTracking()
    webcam = cv2.VideoCapture(WEBCAM_INDEX)
    if not webcam.isOpened():
        # try alternate index
        webcam = cv2.VideoCapture(WEBCAM_INDEX + 1)
        if not webcam.isOpened():
            print(f"ERROR: cannot open webcam at index {WEBCAM_INDEX} or {WEBCAM_INDEX + 1}. Exiting.")
            pygame.quit()
            return

    # Start emotion thread
    emotion_thread = threading.Thread(target=emotion_worker, daemon=True)
    emotion_thread.start()

    create_audio_files()

    # Initialize output file (clear or create)
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass

    run = True
    start_time = time.time()
    last_frame_time = start_time
    last_zone_change_time = start_time
    current_time = 0.0

    if zones:
        # Start by speaking the first color
        speak_color(zones[current_zone_index]['name'])

    # Main loop
    while run:
        frame_time = time.time()
        delta_time = frame_time - last_frame_time
        if delta_time <= 0:
            CLOCK.tick(30)
            continue
        last_frame_time = frame_time
        current_time += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Read frame
        ret, frame = webcam.read()
        if not ret:
            print("Webcam frame not read, exiting loop.")
            break
            
        # Flip the frame horizontally to be more intuitive (mirror image)
        frame = cv2.flip(frame, 1)

        # Queue frames for emotion analysis occasionally
        emotion_frame_counter = (emotion_frame_counter + 1) % EMOTION_INTERVAL
        if emotion_frame_counter == 0:
            with emotion_lock:
                # Don't let the queue get too long
                if len(emotion_detection_queue) < 3: 
                    emotion_detection_queue.append(frame.copy())

        # Gaze tracking
        try:
            gaze.refresh(frame)
            frame_debug = gaze.annotated_frame()
        except Exception:
            frame_debug = frame.copy()

        # Gaze point detection
        new_gazed_zone_name = None
        gaze_point = None
        current_gazed_zone_name = None

        if is_gaze_reliable(gaze):
            raw_gaze_point = get_gaze_coordinates(gaze)
            if raw_gaze_point is not None:
                gaze_point = smooth_gaze(gaze_history, raw_gaze_point)
                for zone in zones:
                    if gaze_point and zone['rect'].collidepoint(gaze_point):
                        new_gazed_zone_name = zone['name']
                        break
        else:
            # If gaze is unreliable, clear history to stop smoothing old, bad data
            if gaze_history:
                gaze_history.clear()

        # Log times
        if new_gazed_zone_name is not None:
            hover_time[new_gazed_zone_name] += delta_time
            # Only log valid emotions 
            with emotion_lock:
                emotion_snapshot = current_emotion
            if emotion_snapshot not in ["Loading...", "No Face", "Error"]:
                emotion_data_log[new_gazed_zone_name][emotion_snapshot] += delta_time

        current_gazed_zone_name = new_gazed_zone_name

        # Auto-switch prompt zone
        if speaking_zone_name and time.time() > speech_animation_end_time:
            speaking_zone_name = None

        # Cycle to the next color prompt every 3 seconds after the previous speech ends
        if time.time() - last_zone_change_time >= 3 and speaking_zone_name is None:
            current_zone_index = (current_zone_index + 1) % len(zones)
            speak_color(zones[current_zone_index]['name'])
            last_zone_change_time = time.time()

        # Drawing
        WIN.fill(WHITE)
        draw_zones_and_eyes(WIN, speaking_zone_name, current_time)

        # highlight prompting zone
        if zones:
            current_zone_rect = zones[current_zone_index]['rect']
            # Draw a white border around the current zone
            pygame.draw.rect(WIN, (255, 255, 255), current_zone_rect, 5) 

        # Draw webcam small view
        webcam_surface = cvimage_to_pygame(frame_debug, WEBCAM_SIZE)
        WIN.blit(webcam_surface, WEBCAM_POS)
        pygame.draw.rect(WIN, BLACK, (*WEBCAM_POS, *WEBCAM_SIZE), 2)

        # draw gaze dot for debugging 
        if gaze_point is not None:
            # ensure in bounds
            gx, gy = gaze_point
            if 0 <= gx < WIDTH and 0 <= gy < HEIGHT:
                pygame.draw.circle(WIN, (0, 0, 0), gaze_point, GAZE_DOT_RADIUS)

        # Status text
        time_elapsed = time.time() - start_time
        time_left = max(0.0, TIME_LIMIT - time_elapsed)
        timer_surface = FONT.render(f"Time Left: {time_left:.1f}s", True, BLACK)

        gaze_status = f"GAZING AT: {current_gazed_zone_name or 'None'}"
        gaze_status_surface = FONT.render(gaze_status, True, BLACK)

        with emotion_lock:
            emotion_display = current_emotion

        emotion_surface = FONT.render(f"EMOTION: {emotion_display}", True, RED)

        WIN.blit(timer_surface, (WIDTH - timer_surface.get_width() - 10, HEIGHT - 40))
        WIN.blit(gaze_status_surface, (10, HEIGHT - 40))
        WIN.blit(emotion_surface, (WIDTH - emotion_surface.get_width() - 10, HEIGHT - 80))

        if gaze_point is None and time_elapsed < 5:
            hint_surface = FONT.render("Make sure your face is clearly visible to the camera", True, RED)
            WIN.blit(hint_surface, (WIDTH // 2 - hint_surface.get_width() // 2, 10))

        pygame.display.update()
        CLOCK.tick(30)

        if time_elapsed >= TIME_LIMIT:
            run = False

    # Cleanup
    emotion_thread_running = False
    time.sleep(0.2)
    try:
        if emotion_thread.is_alive():
            emotion_thread.join(timeout=1.0)
    except Exception:
        pass

    try:
        webcam.release()
    except Exception:
        pass

    # Determine dominant color
    total_time = sum(hover_time.values())
    if total_time > 0:
        dominant_color_name = max(hover_time, key=hover_time.get)
        dominant_zone = next((z for z in zones if z['name'] == dominant_color_name), None)
        dominant_color_rgb = dominant_zone['color'] if dominant_zone else WHITE
    else:
        dominant_color_name = "N/A (No Data)"
        dominant_color_rgb = (150, 150, 150)

    # Show final screen with emotion breakdown
    display_final_result(WIN, dominant_color_name, dominant_color_rgb, emotion_data_log)

    try:
        pygame.mixer.quit()
    except Exception:
        pass
    pygame.quit()

    # Final report generation
    overall_emotion_time = defaultdict(float)
    for color_emotions in emotion_data_log.values():
        for emotion, t in color_emotions.items():
            overall_emotion_time[emotion] += t

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("Color Attention Summary (Gaze & Emotion Mode):\n")
            f.write(f"Test Duration: {TIME_LIMIT:.0f} seconds\n")
            f.write(f"Total Recorded Gaze Time: {total_time:.2f} seconds\n")
            f.write(f"--- DOMINANT COLOR PREFERENCE: {dominant_color_name} ---\n\n")

            # overall emotion
            total_emotion_time = sum(overall_emotion_time.values())
            if total_emotion_time > 0:
                overall_dominant_emotion = max(overall_emotion_time, key=overall_emotion_time.get)
                dominant_emotion_time = overall_emotion_time[overall_dominant_emotion]
                percent = dominant_emotion_time / total_emotion_time * 100 if total_emotion_time > 0 else 0
                f.write(f"--- OVERALL DOMINANT EMOTION: {overall_dominant_emotion.upper()} ---\n")
                f.write(f"Time spent with {overall_dominant_emotion}: {dominant_emotion_time:.2f} sec ({percent:.1f}%)\n\n")

                f.write("--- OVERALL EMOTION DISTRIBUTION ---\n")
                for emotion, t in sorted(overall_emotion_time.items(), key=lambda x: x[1], reverse=True):
                    perc = (t / total_emotion_time * 100) if total_emotion_time > 0 else 0
                    f.write(f"{emotion}: {t:.2f} sec ({perc:.1f}%)\n")
                f.write("\n")

            # per-color report
            if total_time > 0:
                dominant_color_emotions = emotion_data_log.get(dominant_color_name, {})
                dominant_emotion_for_color = max(dominant_color_emotions, key=dominant_color_emotions.get) if dominant_color_emotions else "No reliable emotion data"
                f.write(f"--- DOMINANT EMOTION (While gazing at {dominant_color_name}): {str(dominant_emotion_for_color).upper()} ---\n\n")

                f.write("--- TIME SPENT PER COLOR (Absolute & Percentage) ---\n")
                for zone in zones:
                    name = zone['name']
                    t = hover_time.get(name, 0.0)
                    perc = (t / total_time * 100) if total_time > 0 else 0
                    f.write(f"{name}: {t:.2f} sec ({perc:.1f}%)\n")

                f.write("\n--- EMOTION ASSOCIATION WITH EACH COLOR ---\n")
                for zone in zones:
                    name = zone['name']
                    f.write(f"\n{name}:\n")
                    emotions = emotion_data_log.get(name, {})
                    if emotions:
                        total_t = sum(emotions.values())
                        for emotion, t in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
                            perc = (t / total_t * 100) if total_t > 0 else 0
                            f.write(f"  - {emotion}: {t:.2f} sec ({perc:.1f}%)\n")
                    else:
                        f.write("  - No reliable emotion data recorded.\n")
            else:
                f.write("No successful gaze data was recorded during the test.\n")
    except Exception as e:
        print(f"Error writing final report: {e}")

def display_final_result(window, dominant_color_name, dominant_color_rgb, emotion_results):
    """Show final result screen until user presses any key or closes."""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                running = False

        if dominant_color_name == "N/A (No Data)":
            bg_color = (150, 150, 150)
            text_color = WHITE
            color_text = "NO PREFERENCE RECORDED"
        else:
            bg_color = dominant_color_rgb
            r, g, b = dominant_color_rgb
            # Determine text color for contrast
            text_color = WHITE if (r + g + b) < 380 else BLACK 
            color_text = dominant_color_name.upper()

        window.fill(bg_color)
        main_surface = LARGE_FONT.render("Your Dominant Preference is:", True, text_color)
        color_surface = LARGE_FONT.render(color_text, True, text_color)
        instr_surface = FONT.render("Press any key to exit.", True, text_color)

        window.blit(main_surface, (WIDTH // 2 - main_surface.get_width() // 2, HEIGHT // 2 - 120))
        window.blit(color_surface, (WIDTH // 2 - color_surface.get_width() // 2, HEIGHT // 2 - 20))
        window.blit(instr_surface, (WIDTH // 2 - instr_surface.get_width() // 2, HEIGHT - 50))

        # emotion breakdown (top 3 colors by total associated emotion time)
        if emotion_results:
            # Compute sum per color
            color_sums = [(c, sum(em.values())) for c, em in emotion_results.items()]
            top_colors = sorted(color_sums, key=lambda x: x[1], reverse=True)[:3]
            y_offset = HEIGHT // 2 + 80
            title_surf = FONT.render("Emotion Breakdown (top associations):", True, text_color)
            window.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, y_offset - 30))
            for i, (color_name, _) in enumerate(top_colors):
                emotions = emotion_results.get(color_name, {})
                if emotions:
                    # Find the most frequent emotion for this color
                    dominant_emotion = max(emotions, key=emotions.get) 
                    line = f"{color_name}: Mostly {dominant_emotion.upper()}"
                else:
                    line = f"{color_name}: No reliable emotion data"
                line_surf = FONT.render(line, True, text_color)
                window.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y_offset + i * 36))

        pygame.display.update()
        pygame.time.Clock().tick(15)

if __name__ == "__main__":
    main()
