# Maya Magic

Camera-based spell-casting app for kids. Python 3.9+, OpenCV, Pygame, SpeechRecognition, pyttsx3.

## Architecture

Single-file app (`main.py`). Hybrid wand detection: MOG2 background subtraction (primary) + motion-trail tracking (fallback). Speech recognition runs in daemon thread, communicates via `queue.Queue`. Pygame renders fullscreen at 30fps target.

## Key Files

- `main.py` - entire app (detection, particles, voice, UI)
- `generate_voices.py` - one-time WAV generation via pyttsx3
- `setup.sh` - install + generate + launch
- `tests/test_gestures.py` - 50 unit tests

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Running the App

```bash
python3 main.py --windowed  # windowed mode
python3 main.py             # fullscreen
```

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health
