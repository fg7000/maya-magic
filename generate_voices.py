#!/usr/bin/env python3
"""Generate wizard voice WAV files using pyttsx3.

Run once during setup. If pyttsx3 fails on your system, the app falls back
to pre-generated WAVs shipped in the voices/ directory.
"""

import os
import sys

VOICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices")

VOICE_LINES = {
    # Welcome
    "welcome": "Welcome, young wizard. Pick up your wand and let the magic begin.",
    # Wand found
    "wand_found": "Ah, I see your wand! Give it a wave.",
    # Wand lost
    "wand_lost": "Where did your wand go? Wave it for me again.",
    # Spell cast lines
    "spell_lumos": "Lumos! Let there be light!",
    "spell_nova": "Nova! A burst of pure energy!",
    "spell_glacius": "Glacius! Feel the frost!",
    "spell_ignis": "Ignis! The flames obey you!",
    "spell_levitas": "Levitas! Rise and float!",
    "spell_tempest": "Tempest! The storm is yours!",
    # Idle hints
    "idle_hint_1": "Try waving your wand and saying Lumos!",
    "idle_hint_2": "Say a spell name. Try Nova, or Glacius!",
    "idle_hint_3": "Wave your wand in a big arc. I will follow the tip!",
    # Farewell
    "farewell": "Until next time, young wizard. The magic lives in you.",
}


def generate_voices():
    """Generate all voice WAV files."""
    try:
        import pyttsx3
    except ImportError:
        print("ERROR: pyttsx3 not installed. Run: pip install pyttsx3")
        print("The app will use fallback WAVs if available.")
        return False

    os.makedirs(VOICES_DIR, exist_ok=True)

    try:
        engine = pyttsx3.init()
    except Exception as e:
        print(f"ERROR: Could not initialize pyttsx3: {e}")
        print("On Linux, install espeak: sudo apt install espeak")
        print("The app will use fallback WAVs if available.")
        return False

    # Try to set a deeper, wizard-like voice
    voices = engine.getProperty("voices")
    for voice in voices:
        # Prefer a male voice for the wizard
        if "male" in voice.name.lower() or "daniel" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.setProperty("rate", 140)  # Slightly slow for wizard gravitas
    engine.setProperty("volume", 1.0)

    generated = 0
    failed = 0

    for name, text in VOICE_LINES.items():
        filepath = os.path.join(VOICES_DIR, f"{name}.wav")
        try:
            engine.save_to_file(text, filepath)
            engine.runAndWait()
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"  Generated: {name}.wav")
                generated += 1
            else:
                print(f"  WARNING: {name}.wav was empty, skipping")
                failed += 1
        except Exception as e:
            print(f"  WARNING: Failed to generate {name}.wav: {e}")
            failed += 1

    print(f"\nDone. Generated {generated}/{len(VOICE_LINES)} voice files.")
    if failed > 0:
        print(f"{failed} files failed. The app will skip missing voices gracefully.")

    return generated > 0


if __name__ == "__main__":
    print("Maya Magic Voice Generator")
    print("=" * 40)
    success = generate_voices()
    sys.exit(0 if success else 1)
