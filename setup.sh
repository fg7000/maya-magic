#!/usr/bin/env bash
# Maya Magic Setup Script
# Installs dependencies, generates voice files, and launches the app.

set -e

echo "=========================================="
echo "  Maya Magic - Setup & Launch"
echo "=========================================="
echo ""

# Check Python version
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ] 2>/dev/null; then
            PYTHON="$cmd"
            echo "Found Python $version ($cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.9+ is required but not found."
    echo "Install Python from https://python.org"
    exit 1
fi

# Install pip dependencies
echo ""
echo "Installing dependencies..."
$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r requirements.txt

# Check for espeak on Linux (needed for pyttsx3)
if [ "$(uname)" = "Linux" ]; then
    if ! command -v espeak &>/dev/null; then
        echo ""
        echo "NOTE: espeak is needed for voice generation on Linux."
        echo "Install with: sudo apt install espeak"
        echo "Continuing without it (app will use keyboard shortcuts)..."
    fi
fi

# Generate voice files
echo ""
echo "Generating wizard voice files..."
$PYTHON generate_voices.py || echo "Voice generation had issues (app will still work)."

# Launch
echo ""
echo "=========================================="
echo "  Launching Maya Magic!"
echo "  Press ESC to quit"
echo "=========================================="
echo ""
$PYTHON main.py "$@"
