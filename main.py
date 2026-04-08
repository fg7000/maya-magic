#!/usr/bin/env python3
"""
Maya Magic - Camera-Based Spell-Casting App for Kids

Wave any stick in front of your webcam, say a spell name, and watch the magic!
Uses OpenCV for wand detection, Pygame for rendering, SpeechRecognition for
voice commands, and pre-generated wizard voice lines.

Usage:
    python main.py              # Fullscreen mode
    python main.py --windowed   # Windowed mode (for debugging)

Controls:
    ESC         - Quit
    Keys 1-6    - Cast spells (Lumos, Nova, Glacius, Ignis, Levitas, Tempest)
    D           - Toggle debug overlay
"""

import argparse
import collections
import math
import os
import queue
import random
import sys
import threading
import time

try:
    import cv2
except ImportError:
    print("ERROR: OpenCV not found. Run: pip install opencv-python")
    sys.exit(1)

try:
    import pygame
except ImportError:
    print("ERROR: Pygame not found. Run: pip install pygame")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WINDOW_TITLE = "Maya Magic"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 30

# Wand detection (primary: background subtraction)
MOG2_HISTORY = 500
MOG2_VAR_THRESHOLD = 50
MORPH_ERODE_KERNEL = 3
MORPH_ERODE_ITER = 2
MORPH_DILATE_KERNEL = 5
MORPH_DILATE_ITER = 3
CONTOUR_MIN_AREA = 500
CONTOUR_MAX_AREA = 80000
ASPECT_RATIO_MIN = 2.5
SMOOTHING_WINDOW = 5

# Wand detection (fallback: motion trail)
MOTION_THRESHOLD = 25
FALLBACK_TRIGGER_FRAMES = 30

# Wand state machine
TRACKING_CONFIRM_FRAMES = 5
LOST_CONFIRM_FRAMES = 20
IDLE_HINT_SECONDS = 15

# Spells
SPELL_COOLDOWN = 2.0
VOICE_COOLDOWN = 3.0

# Particles
MAX_PARTICLES = 500
TRAIL_SPAWN_RATE = 3
TRAIL_LIFE = 30

# Colors
COLOR_GOLD = (255, 215, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 100)
COLOR_RED = (255, 80, 30)
COLOR_ORANGE = (255, 160, 50)
COLOR_BLUE = (100, 150, 255)
COLOR_ICE_WHITE = (200, 220, 255)
COLOR_PURPLE = (180, 80, 255)
COLOR_CYAN = (80, 220, 255)
COLOR_GREEN = (80, 255, 120)

# ---------------------------------------------------------------------------
# Spell definitions
# ---------------------------------------------------------------------------

SPELLS = {
    "lumos": {
        "name": "Lumos",
        "key": pygame.K_1,
        "colors": [COLOR_WHITE, COLOR_YELLOW, (255, 240, 200)],
        "count": 80,
        "life": 60,
        "speed": 3.0,
        "behavior": "radial",
        "voice": "spell_lumos",
    },
    "nova": {
        "name": "Nova",
        "key": pygame.K_2,
        "colors": [COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_CYAN, COLOR_PURPLE, COLOR_GREEN],
        "count": 150,
        "life": 90,
        "speed": 6.0,
        "behavior": "radial",
        "voice": "spell_nova",
    },
    "glacius": {
        "name": "Glacius",
        "key": pygame.K_3,
        "colors": [COLOR_BLUE, COLOR_ICE_WHITE, COLOR_WHITE],
        "count": 100,
        "life": 75,
        "speed": 2.0,
        "behavior": "snow",
        "voice": "spell_glacius",
    },
    "ignis": {
        "name": "Ignis",
        "key": pygame.K_4,
        "colors": [COLOR_RED, COLOR_ORANGE, (255, 200, 50)],
        "count": 100,
        "life": 45,
        "speed": 4.0,
        "behavior": "fire",
        "voice": "spell_ignis",
    },
    "levitas": {
        "name": "Levitas",
        "key": pygame.K_5,
        "colors": [COLOR_PURPLE, (200, 120, 255), (140, 60, 220)],
        "count": 80,
        "life": 60,
        "speed": 3.0,
        "behavior": "spiral",
        "voice": "spell_levitas",
    },
    "tempest": {
        "name": "Tempest",
        "key": pygame.K_6,
        "colors": [COLOR_CYAN, COLOR_WHITE, (60, 200, 240)],
        "count": 120,
        "life": 50,
        "speed": 4.0,
        "behavior": "circular",
        "voice": "spell_tempest",
    },
}

SPELL_KEY_MAP = {}
for spell_name, spell_data in SPELLS.items():
    SPELL_KEY_MAP[spell_data["key"]] = spell_name

# ---------------------------------------------------------------------------
# Voice Manager
# ---------------------------------------------------------------------------

class VoiceManager:
    """Handles loading and playing wizard voice WAV files."""

    def __init__(self):
        self.voices_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices")
        self.channel = None
        self.sounds = {}
        self.last_play_time = 0.0
        self._load_voices()

    def _load_voices(self):
        """Load all WAV files from the voices directory."""
        if not os.path.isdir(self.voices_dir):
            return
        for filename in os.listdir(self.voices_dir):
            if filename.endswith(".wav"):
                name = filename[:-4]
                filepath = os.path.join(self.voices_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                except Exception:
                    pass

    def init_channel(self):
        """Reserve a mixer channel for voice playback."""
        pygame.mixer.set_num_channels(8)
        self.channel = pygame.mixer.Channel(0)

    def play(self, name):
        """Play a voice line by name, respecting cooldown."""
        now = time.time()
        if now - self.last_play_time < VOICE_COOLDOWN:
            return
        sound = self.sounds.get(name)
        if sound and self.channel:
            self.channel.stop()
            self.channel.play(sound)
            self.last_play_time = now

    def play_random_hint(self):
        """Play a random idle hint."""
        hints = [k for k in self.sounds if k.startswith("idle_hint")]
        if hints:
            self.play(random.choice(hints))


# ---------------------------------------------------------------------------
# Particle System
# ---------------------------------------------------------------------------

class ParticleSystem:
    """Manages all particles: trail particles and spell burst particles."""

    def __init__(self):
        self.particles = []
        self.sprites = {}
        self._tint_cache = {}
        self._build_sprites()

    def _build_sprites(self):
        """Pre-render particle sprites at multiple sizes and alpha levels."""
        sizes = [4, 8, 12, 16]
        alphas = [64, 128, 192]
        for size in sizes:
            for alpha in alphas:
                key = (size, alpha)
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                radius = size // 2
                pygame.draw.circle(surf, (255, 255, 255, alpha), (radius, radius), radius)
                self.sprites[key] = surf

    def spawn_trail(self, x, y, count=TRAIL_SPAWN_RATE):
        """Spawn trail particles at wand tip."""
        for _ in range(count):
            self.particles.append({
                "x": x + random.uniform(-3, 3),
                "y": y + random.uniform(-3, 3),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.5, 0.5),
                "life": TRAIL_LIFE,
                "max_life": TRAIL_LIFE,
                "color": random.choice([COLOR_GOLD, COLOR_YELLOW, (255, 200, 50)]),
                "size": random.choice([4, 8]),
            })

    def spawn_spell(self, x, y, spell_data):
        """Spawn a burst of spell particles."""
        behavior = spell_data["behavior"]
        count = spell_data["count"]
        life = spell_data["life"]
        speed = spell_data["speed"]
        colors = spell_data["colors"]

        for i in range(count):
            color = random.choice(colors)
            vx, vy = 0.0, 0.0

            if behavior == "radial":
                angle = random.uniform(0, 2 * math.pi)
                spd = random.uniform(0.5, speed)
                vx = math.cos(angle) * spd
                vy = math.sin(angle) * spd
            elif behavior == "snow":
                vx = random.uniform(-1, 1)
                vy = random.uniform(1, 3)
            elif behavior == "fire":
                vx = random.uniform(-1, 1)
                vy = random.uniform(-speed, -speed * 0.5)
            elif behavior == "spiral":
                angle = (i / count) * 4 * math.pi
                radius = random.uniform(1, speed)
                vx = math.cos(angle) * radius
                vy = math.sin(angle) * radius
            elif behavior == "circular":
                angle = random.uniform(0, 2 * math.pi)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            self.particles.append({
                "x": x + random.uniform(-5, 5),
                "y": y + random.uniform(-5, 5),
                "vx": vx,
                "vy": vy,
                "life": life + random.randint(-10, 10),
                "max_life": life,
                "color": color,
                "size": random.choice([8, 12, 16]),
            })

    def update(self):
        """Update all particles. Remove dead ones. Cap pool."""
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.02  # slight gravity
            p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)

        # Cap at MAX_PARTICLES, drop oldest first
        if len(alive) > MAX_PARTICLES:
            alive = alive[len(alive) - MAX_PARTICLES:]

        self.particles = alive

    def _get_tinted(self, size, alpha, color):
        """Get a tinted sprite, using cache to avoid per-frame allocation."""
        cache_key = (size, alpha, color)
        cached = self._tint_cache.get(cache_key)
        if cached is not None:
            return cached

        base_key = (size, alpha)
        sprite = self.sprites.get(base_key)
        if sprite is None:
            return None

        tinted = sprite.copy()
        tinted.fill(color + (0,), special_flags=pygame.BLEND_RGB_MULT)
        self._tint_cache[cache_key] = tinted
        return tinted

    def draw(self, surface):
        """Render all particles."""
        for p in self.particles:
            ratio = max(0.0, p["life"] / p["max_life"])
            # Pick alpha based on life ratio
            if ratio > 0.66:
                alpha = 192
            elif ratio > 0.33:
                alpha = 128
            else:
                alpha = 64

            size = p["size"]
            tinted = self._get_tinted(size, alpha, p["color"])
            if tinted is None:
                continue

            surface.blit(tinted, (int(p["x"]) - size // 2, int(p["y"]) - size // 2))

    @property
    def count(self):
        return len(self.particles)


# ---------------------------------------------------------------------------
# Wand Detector
# ---------------------------------------------------------------------------

class WandDetector:
    """Hybrid wand detection: MOG2 background subtraction + motion trail fallback."""

    def __init__(self):
        # Primary: background subtraction
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=MOG2_HISTORY,
            varThreshold=MOG2_VAR_THRESHOLD,
            detectShadows=False,
        )
        self.erode_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (MORPH_ERODE_KERNEL, MORPH_ERODE_KERNEL)
        )
        self.dilate_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (MORPH_DILATE_KERNEL, MORPH_DILATE_KERNEL)
        )

        # Fallback: motion trail
        self.prev_gray = None
        self.no_detection_frames = 0
        self.using_fallback = False

        # Smoothing
        self.position_buffer = collections.deque(maxlen=SMOOTHING_WINDOW)
        self.tip_position = None
        self.raw_tip = None

    def detect(self, frame):
        """Run detection pipeline. Returns (x, y) of wand tip or None."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        tip = self._detect_primary(blurred)

        if tip is not None:
            self.no_detection_frames = 0
            if self.using_fallback:
                self.using_fallback = False
        else:
            self.no_detection_frames += 1
            if self.no_detection_frames >= FALLBACK_TRIGGER_FRAMES:
                tip = self._detect_fallback(gray)
                if tip is not None:
                    self.using_fallback = True

        self.prev_gray = gray

        if tip is not None:
            self.raw_tip = tip
            self.position_buffer.append(tip)
            # Moving average smoothing
            avg_x = sum(p[0] for p in self.position_buffer) / len(self.position_buffer)
            avg_y = sum(p[1] for p in self.position_buffer) / len(self.position_buffer)
            self.tip_position = (int(avg_x), int(avg_y))
            return self.tip_position
        else:
            self.raw_tip = None
            self.tip_position = None
            return None

    def _detect_primary(self, blurred):
        """Primary detection: MOG2 background subtraction + contour analysis."""
        fg_mask = self.bg_subtractor.apply(blurred)

        # Morphological cleanup
        fg_mask = cv2.erode(fg_mask, self.erode_kernel, iterations=MORPH_ERODE_ITER)
        fg_mask = cv2.dilate(fg_mask, self.dilate_kernel, iterations=MORPH_DILATE_ITER)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_tip = None
        best_score = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < CONTOUR_MIN_AREA or area > CONTOUR_MAX_AREA:
                continue

            rect = cv2.minAreaRect(contour)
            w, h = rect[1]
            if w == 0 or h == 0:
                continue

            aspect = max(w, h) / min(w, h)
            if aspect < ASPECT_RATIO_MIN:
                continue

            # Found an elongated contour. Find the tip (point furthest from bottom-center).
            frame_bottom_center = (CAMERA_WIDTH // 2, CAMERA_HEIGHT)

            max_dist = 0
            tip_point = None
            for point in contour.reshape(-1, 2):
                dx = point[0] - frame_bottom_center[0]
                dy = point[1] - frame_bottom_center[1]
                dist = dx * dx + dy * dy
                if dist > max_dist:
                    max_dist = dist
                    tip_point = (int(point[0]), int(point[1]))

            if tip_point and area * aspect > best_score:
                best_score = area * aspect
                best_tip = tip_point

        return best_tip

    def _detect_fallback(self, gray):
        """Fallback detection: motion trail (frame differencing)."""
        if self.prev_gray is None:
            return None

        diff = cv2.absdiff(gray, self.prev_gray)
        _, motion_mask = cv2.threshold(diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < 200:
            return None

        # Use topmost point as likely wand tip
        topmost = tuple(largest[largest[:, :, 1].argmin()][0])
        return topmost


# ---------------------------------------------------------------------------
# Wand State Machine
# ---------------------------------------------------------------------------

class WandState:
    SEARCHING = "SEARCHING"
    TRACKING = "TRACKING"
    LOST = "LOST"


class WandStateMachine:
    """Manages SEARCHING -> TRACKING -> LOST transitions."""

    def __init__(self):
        self.state = WandState.SEARCHING
        self.consecutive_detected = 0
        self.consecutive_lost = 0
        self.searching_start = time.time()
        self.hint_played = False

    def update(self, tip_detected):
        """Update state based on whether tip was detected this frame."""
        if tip_detected:
            self.consecutive_detected += 1
            self.consecutive_lost = 0
        else:
            self.consecutive_lost += 1
            self.consecutive_detected = 0

        if self.state == WandState.SEARCHING:
            if self.consecutive_detected >= TRACKING_CONFIRM_FRAMES:
                self.state = WandState.TRACKING
                self.consecutive_lost = 0
                return "wand_found"
            # Check idle hint timer
            elapsed = time.time() - self.searching_start
            if elapsed >= IDLE_HINT_SECONDS and not self.hint_played:
                self.hint_played = True
                return "idle_hint"

        elif self.state == WandState.TRACKING:
            if self.consecutive_lost >= LOST_CONFIRM_FRAMES:
                self.state = WandState.LOST
                self.consecutive_detected = 0
                return "wand_lost"

        elif self.state == WandState.LOST:
            if self.consecutive_detected >= TRACKING_CONFIRM_FRAMES:
                self.state = WandState.TRACKING
                self.consecutive_lost = 0
                return "wand_found"
            if self.consecutive_lost >= LOST_CONFIRM_FRAMES * 2:
                self.state = WandState.SEARCHING
                self.searching_start = time.time()
                self.hint_played = False

        return None


# ---------------------------------------------------------------------------
# Speech Recognition Thread
# ---------------------------------------------------------------------------

def speech_thread_func(spell_queue, stop_event, speech_active_flag):
    """Background thread for continuous speech recognition."""
    try:
        import speech_recognition as sr
    except ImportError:
        speech_active_flag.clear()
        return

    recognizer = sr.Recognizer()

    try:
        mic = sr.Microphone()
    except (OSError, AttributeError):
        speech_active_flag.clear()
        return

    spell_names = set(SPELLS.keys())
    last_recognition = 0.0

    with mic as source:
        # Adjust for ambient noise once
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception:
            pass

        while not stop_event.is_set():
            # Rate limit
            now = time.time()
            if now - last_recognition < 2.0:
                time.sleep(0.1)
                continue

            try:
                audio = recognizer.listen(source, phrase_time_limit=3, timeout=5)
            except sr.WaitTimeoutError:
                continue
            except Exception:
                continue

            try:
                text = recognizer.recognize_google(audio).lower()
                last_recognition = time.time()
                words = text.split()
                for word in words:
                    if word in spell_names:
                        try:
                            spell_queue.put_nowait(word)
                        except queue.Full:
                            pass
                        break
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                # API error (no internet, rate limited, etc.)
                # Disable speech for remainder of session
                speech_active_flag.clear()
                return
            except Exception:
                pass


# ---------------------------------------------------------------------------
# UI Drawing Helpers
# ---------------------------------------------------------------------------

def draw_text(surface, text, x, y, font, color=COLOR_WHITE, center=False):
    """Draw text on a surface."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)


def draw_camera_frame(surface, frame, display_w, display_h):
    """Convert OpenCV frame to Pygame surface and blit it."""
    # Flip horizontally (mirror) so it feels natural
    frame = cv2.flip(frame, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (display_w, display_h))
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    surface.blit(frame_surface, (0, 0))


def scale_point(x, y, cam_w, cam_h, disp_w, disp_h):
    """Scale a point from camera coordinates to display coordinates, accounting for mirror flip."""
    # Mirror the x coordinate (we flip the frame horizontally)
    sx = int((cam_w - x) * disp_w / cam_w)
    sy = int(y * disp_h / cam_h)
    return sx, sy


# ---------------------------------------------------------------------------
# Error Screen
# ---------------------------------------------------------------------------

def show_error_screen(screen, font_large, font_small, message, detail=""):
    """Display an error screen and wait for user to quit."""
    screen.fill((30, 0, 40))
    draw_text(screen, "Maya Magic", screen.get_width() // 2, 80, font_large, COLOR_PURPLE, center=True)
    draw_text(screen, message, screen.get_width() // 2, 200, font_small, COLOR_RED, center=True)
    if detail:
        draw_text(screen, detail, screen.get_width() // 2, 250, font_small, COLOR_WHITE, center=True)
    draw_text(screen, "Press ESC to exit", screen.get_width() // 2, 350, font_small, COLOR_GOLD, center=True)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.time.wait(100)


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Maya Magic - Camera-Based Spell Casting")
    parser.add_argument("--windowed", action="store_true", help="Run in windowed mode")
    args = parser.parse_args()

    # Initialize Pygame
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    if args.windowed:
        screen = pygame.display.set_mode((960, 720))
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    pygame.display.set_caption(WINDOW_TITLE)
    display_w, display_h = screen.get_size()

    clock = pygame.time.Clock()

    # Fonts
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
    font_tiny = pygame.font.Font(None, 24)

    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        show_error_screen(screen, font_large, font_small,
                          "Camera not found!",
                          "Check that your camera is connected and permissions are granted.")
        pygame.quit()
        return

    # Verify camera actually returns frames (macOS permission issue)
    ret, test_frame = cap.read()
    if not ret or test_frame is None:
        cap.release()
        show_error_screen(screen, font_large, font_small,
                          "Camera permission denied!",
                          "On macOS: System Preferences > Privacy & Security > Camera > Allow Terminal/Python.")
        pygame.quit()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    # Initialize systems
    voice = VoiceManager()
    voice.init_channel()
    particles = ParticleSystem()
    detector = WandDetector()
    state_machine = WandStateMachine()

    # Spell state
    spell_queue = queue.Queue(maxsize=10)
    last_spell_time = 0.0
    active_spell_name = ""
    active_spell_timer = 0

    # Speech recognition thread
    stop_event = threading.Event()
    speech_active = threading.Event()
    speech_t = None

    try:
        import speech_recognition
        speech_active.set()
        speech_t = threading.Thread(
            target=speech_thread_func,
            args=(spell_queue, stop_event, speech_active),
            daemon=True,
        )
        speech_t.start()
    except ImportError:
        pass

    # Pre-allocate overlay surface (reused every frame)
    overlay = pygame.Surface((display_w, display_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, 80))

    # Play welcome voice
    voice.play("welcome")

    # Debug mode
    debug_mode = False

    # Main loop
    running = True
    frame_count = 0

    while running:
        dt = clock.tick(TARGET_FPS)
        current_fps = clock.get_fps()
        frame_count += 1

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif event.key in SPELL_KEY_MAP:
                    try:
                        spell_queue.put_nowait(SPELL_KEY_MAP[event.key])
                    except queue.Full:
                        pass

        # Capture frame
        ret, frame = cap.read()
        if not ret or frame is None:
            # Camera disconnected mid-session
            screen.fill((0, 0, 0))
            draw_text(screen, "Camera lost!", display_w // 2, display_h // 2,
                      font_medium, COLOR_RED, center=True)
            pygame.display.flip()
            continue

        # Detect wand
        tip = detector.detect(frame)

        # Update state machine
        event_name = state_machine.update(tip is not None)
        if event_name == "wand_found":
            voice.play("wand_found")
        elif event_name == "wand_lost":
            voice.play("wand_lost")
        elif event_name == "idle_hint":
            voice.play_random_hint()

        # Check spell queue
        now = time.time()
        try:
            while True:
                spell_name = spell_queue.get_nowait()
                if now - last_spell_time >= SPELL_COOLDOWN:
                    last_spell_time = now
                    spell_data = SPELLS.get(spell_name)
                    if spell_data:
                        active_spell_name = spell_data["name"]
                        active_spell_timer = 60  # frames to show spell name

                        # Play voice
                        voice.play(spell_data["voice"])

                        # Determine spawn point
                        if tip:
                            sx, sy = scale_point(tip[0], tip[1],
                                                 CAMERA_WIDTH, CAMERA_HEIGHT,
                                                 display_w, display_h)
                        else:
                            sx, sy = display_w // 2, display_h // 2

                        # Adjust particle count based on fps
                        adjusted_data = dict(spell_data)
                        if current_fps > 0 and current_fps < 20:
                            adjusted_data["count"] = spell_data["count"] // 2

                        particles.spawn_spell(sx, sy, adjusted_data)
        except queue.Empty:
            pass

        # Draw camera frame
        draw_camera_frame(screen, frame, display_w, display_h)

        # Draw semi-transparent overlay for better particle visibility
        screen.blit(overlay, (0, 0))

        # Spawn trail particles if tracking
        if state_machine.state == WandState.TRACKING and tip:
            sx, sy = scale_point(tip[0], tip[1],
                                 CAMERA_WIDTH, CAMERA_HEIGHT,
                                 display_w, display_h)
            # Reduce trail spawn at lower fps
            spawn_count = TRAIL_SPAWN_RATE
            if current_fps > 0 and current_fps < 25:
                spawn_count = max(1, TRAIL_SPAWN_RATE - 1)
            particles.spawn_trail(sx, sy, spawn_count)

        # Update and draw particles
        particles.update()
        particles.draw(screen)

        # UI: State-dependent text
        if state_machine.state == WandState.SEARCHING:
            draw_text(screen, "Wave your wand!", display_w // 2, 50,
                      font_medium, COLOR_GOLD, center=True)

        # UI: Spell name flash
        if active_spell_timer > 0:
            alpha = min(255, active_spell_timer * 8)
            spell_surf = font_large.render(active_spell_name + "!", True, COLOR_WHITE)
            spell_surf.set_alpha(alpha)
            rect = spell_surf.get_rect(center=(display_w // 2, display_h // 3))
            screen.blit(spell_surf, rect)
            active_spell_timer -= 1

        # UI: Keyboard hint (when speech is disabled)
        if not speech_active.is_set():
            draw_text(screen, "Press 1-6 for spells", display_w // 2, display_h - 40,
                      font_tiny, (180, 180, 180), center=True)

        # UI: Detection mode indicator
        if detector.using_fallback:
            draw_text(screen, "*", display_w - 30, 15, font_small, COLOR_CYAN)
        elif state_machine.state == WandState.TRACKING:
            draw_text(screen, "+", display_w - 30, 15, font_small, COLOR_GOLD)

        # UI: Debug overlay
        if debug_mode:
            y_off = 50
            debug_lines = [
                f"FPS: {current_fps:.0f}",
                f"State: {state_machine.state}",
                f"Detector: {'motion' if detector.using_fallback else 'MOG2'}",
                f"Particles: {particles.count}",
                f"Tip: {detector.tip_position}",
                f"Speech: {'on' if speech_active.is_set() else 'off'}",
                f"Frame: {frame_count}",
            ]
            for line in debug_lines:
                draw_text(screen, line, 10, y_off, font_tiny, COLOR_GREEN)
                y_off += 22

        pygame.display.flip()

    # Cleanup
    voice.play("farewell")
    pygame.time.wait(500)  # Brief pause for farewell voice to start

    stop_event.set()
    cap.release()

    if speech_t and speech_t.is_alive():
        speech_t.join(timeout=2.0)

    pygame.quit()


if __name__ == "__main__":
    main()
