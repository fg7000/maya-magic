#!/bin/bash
echo "Starting Maya Magic server..."
echo "Opening http://localhost:8000 in your browser..."
open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || echo "Open http://localhost:8000 in Chrome"
python3 -m http.server 8000
