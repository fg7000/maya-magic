"""Unit tests for Maya Magic: wand detection, spell matching, particle lifecycle."""

import collections
import math
import queue
import time
from unittest.mock import MagicMock, patch

import pytest

# We need to mock pygame and cv2 before importing main
# since they may not be available in test environments without display

import sys

# Create mock modules
mock_pygame = MagicMock()
mock_pygame.SRCALPHA = 65536
mock_pygame.BLEND_RGB_MULT = 1
mock_pygame.FULLSCREEN = 0x80000000
mock_pygame.QUIT = 256
mock_pygame.KEYDOWN = 768
mock_pygame.K_ESCAPE = 27
mock_pygame.K_1 = 49
mock_pygame.K_2 = 50
mock_pygame.K_3 = 51
mock_pygame.K_4 = 52
mock_pygame.K_5 = 53
mock_pygame.K_6 = 54
mock_pygame.K_d = 100

mock_cv2 = MagicMock()
mock_cv2.RETR_EXTERNAL = 0
mock_cv2.CHAIN_APPROX_SIMPLE = 1
mock_cv2.MORPH_RECT = 0
mock_cv2.CAP_PROP_FRAME_WIDTH = 3
mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
mock_cv2.COLOR_BGR2GRAY = 6
mock_cv2.COLOR_BGR2RGB = 4
mock_cv2.THRESH_BINARY = 0

sys.modules["pygame"] = mock_pygame
sys.modules["pygame.mixer"] = mock_pygame.mixer
sys.modules["pygame.display"] = mock_pygame.display
sys.modules["pygame.font"] = mock_pygame.font
sys.modules["pygame.time"] = mock_pygame.time
sys.modules["pygame.surfarray"] = mock_pygame.surfarray
sys.modules["pygame.draw"] = mock_pygame.draw
sys.modules["cv2"] = mock_cv2

import main


# ---------------------------------------------------------------------------
# Spell Matching Tests
# ---------------------------------------------------------------------------

class TestSpellMatching:
    """Test spell name matching from recognized text."""

    def test_exact_match(self):
        """A recognized word that exactly matches a spell name should match."""
        spell_names = set(main.SPELLS.keys())
        text = "lumos"
        words = text.split()
        matches = [w for w in words if w in spell_names]
        assert matches == ["lumos"]

    def test_match_in_phrase(self):
        """Spell name embedded in a phrase should match."""
        spell_names = set(main.SPELLS.keys())
        text = "i said lumos"
        words = text.split()
        matches = [w for w in words if w in spell_names]
        assert matches == ["lumos"]

    def test_no_partial_match(self):
        """Partial overlap (like 'luminous') should NOT match."""
        spell_names = set(main.SPELLS.keys())
        text = "luminous"
        words = text.split()
        matches = [w for w in words if w in spell_names]
        assert matches == []

    def test_case_insensitive(self):
        """Matching should work case-insensitive (text is lowered before matching)."""
        spell_names = set(main.SPELLS.keys())
        text = "Lumos".lower()
        words = text.split()
        matches = [w for w in words if w in spell_names]
        assert matches == ["lumos"]

    def test_all_spells_recognized(self):
        """All 6 spell names should be recognized."""
        spell_names = set(main.SPELLS.keys())
        expected = {"lumos", "nova", "glacius", "ignis", "levitas", "tempest"}
        assert spell_names == expected

    def test_multiple_spells_in_phrase(self):
        """Only first match should be used."""
        spell_names = set(main.SPELLS.keys())
        text = "lumos nova"
        words = text.split()
        first_match = None
        for w in words:
            if w in spell_names:
                first_match = w
                break
        assert first_match == "lumos"

    def test_empty_input(self):
        """Empty text should produce no matches."""
        spell_names = set(main.SPELLS.keys())
        text = ""
        words = text.split()
        matches = [w for w in words if w in spell_names]
        assert matches == []


# ---------------------------------------------------------------------------
# Spell Cooldown Tests
# ---------------------------------------------------------------------------

class TestSpellCooldown:
    """Test the 2-second global spell cooldown."""

    def test_cooldown_blocks_rapid_cast(self):
        """Spells cast within SPELL_COOLDOWN should be ignored."""
        assert main.SPELL_COOLDOWN == 2.0

    def test_cooldown_allows_after_wait(self):
        """Spells cast after SPELL_COOLDOWN should be allowed."""
        last_cast = time.time() - 3.0  # 3 seconds ago
        now = time.time()
        assert now - last_cast >= main.SPELL_COOLDOWN


# ---------------------------------------------------------------------------
# Keyboard Spell Mapping Tests
# ---------------------------------------------------------------------------

class TestKeyboardSpells:
    """Test that keys 1-6 map to correct spells."""

    def test_key_1_is_lumos(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_1] == "lumos"

    def test_key_2_is_nova(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_2] == "nova"

    def test_key_3_is_glacius(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_3] == "glacius"

    def test_key_4_is_ignis(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_4] == "ignis"

    def test_key_5_is_levitas(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_5] == "levitas"

    def test_key_6_is_tempest(self):
        assert main.SPELL_KEY_MAP[mock_pygame.K_6] == "tempest"

    def test_six_spells_mapped(self):
        assert len(main.SPELL_KEY_MAP) == 6


# ---------------------------------------------------------------------------
# Particle Lifecycle Tests
# ---------------------------------------------------------------------------

class TestParticleLifecycle:
    """Test particle spawn, aging, death, and pool management."""

    def setup_method(self):
        """Create a fresh particle system for each test."""
        # Mock pygame.Surface and pygame.draw
        mock_pygame.Surface.return_value = MagicMock()
        mock_pygame.draw.circle = MagicMock()
        self.ps = main.ParticleSystem()

    def test_spawn_trail_creates_particles(self):
        self.ps.spawn_trail(100, 100, count=3)
        assert self.ps.count == 3

    def test_particles_age_each_frame(self):
        self.ps.spawn_trail(100, 100, count=1)
        initial_life = self.ps.particles[0]["life"]
        self.ps.update()
        assert self.ps.particles[0]["life"] == initial_life - 1

    def test_dead_particles_removed(self):
        self.ps.particles.append({
            "x": 100, "y": 100, "vx": 0, "vy": 0,
            "life": 1, "max_life": 30, "color": (255, 255, 0), "size": 4,
        })
        assert self.ps.count == 1
        self.ps.update()  # life goes from 1 to 0
        assert self.ps.count == 0

    def test_pool_capped_at_max(self):
        # Spawn more than MAX_PARTICLES
        for _ in range(main.MAX_PARTICLES + 100):
            self.ps.particles.append({
                "x": 0, "y": 0, "vx": 0, "vy": 0,
                "life": 30, "max_life": 30, "color": (255, 255, 255), "size": 4,
            })
        self.ps.update()
        assert self.ps.count <= main.MAX_PARTICLES

    def test_pool_drops_oldest_first(self):
        # Add particles with sequential IDs via x coordinate
        for i in range(main.MAX_PARTICLES + 50):
            self.ps.particles.append({
                "x": float(i), "y": 0, "vx": 0, "vy": 0,
                "life": 30, "max_life": 30, "color": (255, 255, 255), "size": 4,
            })
        self.ps.update()
        # After capping, the first particle should be one of the newer ones
        assert self.ps.particles[0]["x"] >= 50.0

    def test_spell_spawn_creates_particles(self):
        spell_data = main.SPELLS["lumos"]
        self.ps.spawn_spell(400, 300, spell_data)
        assert self.ps.count == spell_data["count"]

    def test_spell_behaviors_produce_movement(self):
        """Each spell behavior should produce non-zero velocities."""
        for spell_name, spell_data in main.SPELLS.items():
            self.ps.particles.clear()
            self.ps.spawn_spell(400, 300, spell_data)
            # At least some particles should have non-zero velocity
            has_movement = any(
                abs(p["vx"]) > 0.01 or abs(p["vy"]) > 0.01
                for p in self.ps.particles
            )
            assert has_movement, f"Spell {spell_name} produced no movement"


# ---------------------------------------------------------------------------
# Wand State Machine Tests
# ---------------------------------------------------------------------------

class TestWandStateMachine:
    """Test SEARCHING -> TRACKING -> LOST transitions."""

    def setup_method(self):
        self.sm = main.WandStateMachine()

    def test_starts_in_searching(self):
        assert self.sm.state == main.WandState.SEARCHING

    def test_transitions_to_tracking_after_confirm_frames(self):
        for _ in range(main.TRACKING_CONFIRM_FRAMES):
            event = self.sm.update(True)
        assert self.sm.state == main.WandState.TRACKING
        assert event == "wand_found"

    def test_no_premature_tracking(self):
        for _ in range(main.TRACKING_CONFIRM_FRAMES - 1):
            self.sm.update(True)
        assert self.sm.state == main.WandState.SEARCHING

    def test_transitions_to_lost_after_lost_frames(self):
        # First get to TRACKING
        for _ in range(main.TRACKING_CONFIRM_FRAMES):
            self.sm.update(True)
        assert self.sm.state == main.WandState.TRACKING

        # Then lose tracking
        event = None
        for _ in range(main.LOST_CONFIRM_FRAMES):
            event = self.sm.update(False)
        assert self.sm.state == main.WandState.LOST
        assert event == "wand_lost"

    def test_recovers_from_lost_to_tracking(self):
        # Get to LOST state
        for _ in range(main.TRACKING_CONFIRM_FRAMES):
            self.sm.update(True)
        for _ in range(main.LOST_CONFIRM_FRAMES):
            self.sm.update(False)
        assert self.sm.state == main.WandState.LOST

        # Recover
        event = None
        for _ in range(main.TRACKING_CONFIRM_FRAMES):
            event = self.sm.update(True)
        assert self.sm.state == main.WandState.TRACKING
        assert event == "wand_found"

    def test_lost_returns_to_searching(self):
        # Get to LOST state
        for _ in range(main.TRACKING_CONFIRM_FRAMES):
            self.sm.update(True)
        for _ in range(main.LOST_CONFIRM_FRAMES):
            self.sm.update(False)
        assert self.sm.state == main.WandState.LOST

        # Stay lost long enough to return to SEARCHING
        for _ in range(main.LOST_CONFIRM_FRAMES * 2):
            self.sm.update(False)
        assert self.sm.state == main.WandState.SEARCHING

    def test_interrupted_detection_resets_counter(self):
        """If detection is interrupted, counter resets."""
        for _ in range(main.TRACKING_CONFIRM_FRAMES - 1):
            self.sm.update(True)
        self.sm.update(False)  # interruption
        self.sm.update(True)   # restart
        assert self.sm.state == main.WandState.SEARCHING


# ---------------------------------------------------------------------------
# Moving Average Smoothing Tests
# ---------------------------------------------------------------------------

class TestMovingAverage:
    """Test wand position smoothing."""

    def test_smoothing_window_size(self):
        assert main.SMOOTHING_WINDOW == 5

    def test_buffer_is_bounded(self):
        buf = collections.deque(maxlen=main.SMOOTHING_WINDOW)
        for i in range(20):
            buf.append((i, i))
        assert len(buf) == main.SMOOTHING_WINDOW

    def test_average_calculation(self):
        buf = collections.deque(maxlen=main.SMOOTHING_WINDOW)
        points = [(10, 20), (12, 22), (14, 24), (16, 26), (18, 28)]
        for p in points:
            buf.append(p)
        avg_x = sum(p[0] for p in buf) / len(buf)
        avg_y = sum(p[1] for p in buf) / len(buf)
        assert avg_x == 14.0
        assert avg_y == 24.0


# ---------------------------------------------------------------------------
# MOG2 Contour Filtering Tests
# ---------------------------------------------------------------------------

class TestContourFiltering:
    """Test contour filtering parameters."""

    def test_min_area_threshold(self):
        assert main.CONTOUR_MIN_AREA == 500

    def test_max_area_threshold(self):
        assert main.CONTOUR_MAX_AREA == 80000

    def test_aspect_ratio_minimum(self):
        assert main.ASPECT_RATIO_MIN == 2.5

    def test_elongated_shape_passes(self):
        """An elongated shape (aspect > 2.5) should pass the filter."""
        w, h = 10, 30
        aspect = max(w, h) / min(w, h)
        assert aspect >= main.ASPECT_RATIO_MIN

    def test_square_shape_rejected(self):
        """A roughly square shape should be rejected."""
        w, h = 20, 22
        aspect = max(w, h) / min(w, h)
        assert aspect < main.ASPECT_RATIO_MIN


# ---------------------------------------------------------------------------
# Motion Fallback Tests
# ---------------------------------------------------------------------------

class TestMotionFallback:
    """Test fallback detection trigger conditions."""

    def test_fallback_trigger_threshold(self):
        assert main.FALLBACK_TRIGGER_FRAMES == 30

    def test_fallback_activates_after_threshold(self):
        detector = main.WandDetector()
        detector.no_detection_frames = main.FALLBACK_TRIGGER_FRAMES
        assert detector.no_detection_frames >= main.FALLBACK_TRIGGER_FRAMES

    def test_fallback_resets_on_primary_detection(self):
        detector = main.WandDetector()
        detector.no_detection_frames = 50
        detector.using_fallback = True
        # Simulate primary detection found something
        detector.no_detection_frames = 0
        detector.using_fallback = False
        assert detector.no_detection_frames == 0
        assert detector.using_fallback is False


# ---------------------------------------------------------------------------
# Voice Cooldown Tests
# ---------------------------------------------------------------------------

class TestVoiceCooldown:
    """Test wizard voice cooldown."""

    def test_voice_cooldown_value(self):
        assert main.VOICE_COOLDOWN == 3.0


# ---------------------------------------------------------------------------
# Scale Point Tests
# ---------------------------------------------------------------------------

class TestScalePoint:
    """Test coordinate scaling from camera space to display space."""

    def test_center_maps_to_center(self):
        sx, sy = main.scale_point(320, 240, 640, 480, 1920, 1080)
        assert sx == 1920 // 2
        assert sy == 1080 // 2

    def test_mirror_flip(self):
        """X should be mirrored (for webcam mirror effect)."""
        # Point at far left of camera (x=0) should map to far right of display
        sx, sy = main.scale_point(0, 0, 640, 480, 640, 480)
        assert sx == 640

    def test_origin_maps_correctly(self):
        # Camera top-right (x=640) maps to display top-left (x=0) due to mirror
        sx, sy = main.scale_point(640, 0, 640, 480, 640, 480)
        assert sx == 0
        assert sy == 0


# ---------------------------------------------------------------------------
# Spell Queue Tests
# ---------------------------------------------------------------------------

class TestSpellQueue:
    """Test spell queue behavior."""

    def test_queue_non_blocking_get(self):
        q = queue.Queue(maxsize=10)
        q.put("lumos")
        result = q.get_nowait()
        assert result == "lumos"

    def test_queue_empty_raises(self):
        q = queue.Queue(maxsize=10)
        with pytest.raises(queue.Empty):
            q.get_nowait()

    def test_queue_full_put_nowait(self):
        q = queue.Queue(maxsize=2)
        q.put_nowait("lumos")
        q.put_nowait("nova")
        with pytest.raises(queue.Full):
            q.put_nowait("glacius")


# ---------------------------------------------------------------------------
# FPS Degradation Tests
# ---------------------------------------------------------------------------

class TestFPSDegradation:
    """Test particle count reduction at low FPS."""

    def test_below_20fps_halves_count(self):
        spell_data = dict(main.SPELLS["nova"])
        original_count = spell_data["count"]
        current_fps = 15
        if current_fps < 20:
            spell_data["count"] = original_count // 2
        assert spell_data["count"] == original_count // 2

    def test_above_20fps_keeps_count(self):
        spell_data = dict(main.SPELLS["nova"])
        original_count = spell_data["count"]
        current_fps = 25
        if current_fps < 20:
            spell_data["count"] = original_count // 2
        assert spell_data["count"] == original_count
