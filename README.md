# Maya Magic

**Camera-based spell-casting for kids.** Wave any stick in front of your webcam, say a spell name, and watch fullscreen magical particle effects explode on screen. A wizard voice guides the whole experience.

Think Universal Studios wand experience, but free, open-source, and works with any stick in your living room.

## Quick Start

```bash
git clone https://github.com/fg7000/maya-magic.git
cd maya-magic
bash setup.sh
```

That's it. The setup script installs dependencies, generates wizard voice files, and launches the app.

## How It Works

1. The webcam detects any stick-shaped object using background subtraction (OpenCV)
2. The wand tip is tracked in real-time with golden particle trails
3. Say a spell name out loud (or press keys 1-6) to cast spells
4. Fullscreen particle effects + wizard voice respond

No special wand needed. No markers. No tape. Just grab a stick and go.

## Spells

| Key | Spell | Effect |
|-----|-------|--------|
| 1 | **Lumos** | Radial burst of white/yellow light |
| 2 | **Nova** | Rainbow explosion |
| 3 | **Glacius** | Blue snowfall |
| 4 | **Ignis** | Rising flames |
| 5 | **Levitas** | Purple spiral |
| 6 | **Tempest** | Cyan storm |

## Controls

| Key | Action |
|-----|--------|
| ESC | Quit |
| 1-6 | Cast spells |
| D | Toggle debug overlay |

## Requirements

- Python 3.9+
- Webcam
- Microphone (optional, for voice commands)
- Internet connection (optional, for speech recognition via Google API)

### Dependencies

- **OpenCV** - camera capture and wand detection
- **Pygame** - fullscreen display, particles, audio
- **SpeechRecognition** - voice command detection (requires internet)
- **pyttsx3** - offline wizard voice generation
- **PyAudio** - microphone access

## Platform Notes

### macOS
- First run requires granting **camera** and **microphone** access in System Preferences > Privacy & Security
- Python/Terminal must be in the allowed apps list

### Linux
- Install espeak for voice generation: `sudo apt install espeak`
- Camera works via V4L2 (usually out of the box)
- You may need: `sudo apt install python3-pyaudio`

### Windows
- Best-effort support
- PyAudio may require manual install of PortAudio binaries

## Running in Windowed Mode

For debugging or multi-monitor setups:

```bash
python main.py --windowed
```

## Offline Mode

Voice commands require internet (Google Speech API). Without internet, the app works perfectly with keyboard shortcuts (keys 1-6). The keyboard hint appears automatically when speech recognition is unavailable.

## How Detection Works

Maya Magic uses a hybrid detection approach:

1. **Primary: Background Subtraction (MOG2)** - Detects moving objects against a relatively stable background. Filters for elongated shapes (sticks) by aspect ratio.

2. **Fallback: Motion Trail** - When the primary detector can't find an elongated shape for 30+ frames, it switches to tracking the fastest-moving point in frame. Kids wave wands in big arcs, so the tip is usually the fastest thing moving.

The child never knows which detector is active. A small indicator in the corner shows the mode (+ for primary, * for fallback) for debugging.

## Project Structure

```
maya-magic/
  main.py              # The whole app
  generate_voices.py   # One-time voice WAV generation
  setup.sh             # Install + generate voices + launch
  requirements.txt     # Python dependencies
  README.md            # This file
  LICENSE              # MIT
  CLAUDE.md            # Project context for Claude Code
  tests/
    test_gestures.py   # Unit tests (50 tests)
```

## License

MIT License. Copyright (c) 2026 Faryar Ghazanfari.

Original branding only. No affiliation with any theme park or franchise.
