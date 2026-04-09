# Maya Magic

**Browser-based spell-casting for kids.** Open a URL in Chrome, wave any stick in front of your webcam, and watch a golden particle trail follow your wand through a cinematic 3D wizard's study. Say spell names or press 1-6 to cast spells with full visual effects.

Think Universal Studios wand experience, but free, open-source, and runs in your browser with zero install.

## Try It

**[https://fg7000.github.io/maya-magic/](https://fg7000.github.io/maya-magic/)**

Or clone and run locally:

```bash
git clone https://github.com/fg7000/maya-magic.git
cd maya-magic
bash start.sh
```

This starts a local server and opens `http://localhost:8000` in your browser. A local server is required because Chrome blocks 3D model loading from `file://` URLs.

## How It Works

1. Click **Start Magic** to grant camera access
2. A 3D wizard's study appears with flickering candles, dust motes, and moonlight
3. Wave any stick (wand, pencil, spatula) in front of your webcam. A golden particle trail follows your motion.
4. Say a spell name ("Lumos!") or press keys 1-6. The room transforms with particle bursts, lighting changes, and camera effects.
5. A wizard narrator guides you with voice prompts and encouragement.

No special wand needed. No markers. No tape. Just grab a stick and go.

## Spells

| Key | Spell | Effect |
|-----|-------|--------|
| 1 | **Lumos** | Candles blaze, bloom intensifies, gold particle burst |
| 2 | **Glacius** | Room tints frost-blue, candles dim, ice particles |
| 3 | **Ignis** | Fire erupts, candles blaze 4x, orange-red particles |
| 4 | **Levitas** | Objects float upward with gentle bobbing, blue particles |
| 5 | **Nova** | Bloom doubles, camera shakes, supernova particle burst |
| 6 | **Tempest** | Candles extinguish, wind shakes camera, white particles |

## Controls

| Input | Action |
|-------|--------|
| Voice: "Lumos", "Glacius", etc. | Cast spells by speaking |
| Keys 1-6 | Cast spells by keyboard |
| D | Toggle debug overlay (FPS, particles, spell state) |
| +/- | Adjust wand detection sensitivity |

Voice recognition works in Chrome (uses browser's built-in speech service). On mobile/tablet: keyboard spells require a physical keyboard. Touch spell UI coming in a future version.

## Requirements

- **Chrome or Edge** (desktop, for camera + WebGL)
- Webcam
- Any stick-shaped object for your wand

Safari and Firefox: WebGL and keyboard spells work. Wand detection requires getUserMedia support. Keyboard shortcuts 1-6 always work.

## Architecture

Single `index.html` file (~1400 lines). Three.js r168 + UnrealBloomPass loaded from esm.sh CDN. No build step, no npm, no bundler. Local server required for FBX model loading (see Try It above).

- **Rendering:** Three.js WebGLRenderer with EffectComposer (RenderPass + UnrealBloomPass)
- **Wand detection:** getUserMedia → 160x120 downscaled canvas → frame differencing → EMA-smoothed motion centroid → Raycaster 3D projection
- **Particles:** 80 dust motes + 1500 trail particles (ring buffer, gold→orange→red fade, ~0.8s lifetime)
- **Voice recognition:** webkitSpeechRecognition, continuous mode, fuzzy matching with kid-friendly aliases
- **Narrator:** SpeechSynthesis queue with priority interrupt, duplex policy (pauses recognition during speech)
- **Spell effects:** 6 reversible spells with 4s duration + 1s lerp revert. Modify candle intensity, bloom, mesh colors/emissive/scale/position, camera shake. 5s cooldown between casts.
- **Audio:** Web Audio API procedural synthesis (bandpass-filtered noise whoosh)

## Privacy

Your camera feed is processed entirely on your device. It never leaves your browser. Voice recognition uses your browser's built-in speech service (Google's servers in Chrome). No data is collected or sent by this app.

## Project Structure

```
maya-magic/
  index.html           # The entire app
  model/source/        # Dumbledore's Office FBX model + 17 PNG textures
  scene.glb            # Legacy GLB model (unused, kept for reference)
  start.sh             # Local dev server launcher
  README.md            # This file
  CLAUDE.md            # Project context for Claude Code
  LICENSE              # MIT
  .github/workflows/
    pages.yml          # GitHub Pages deploy on push to webgl
```

## License

MIT License. Copyright (c) 2026 Faryar Ghazanfari.

Original branding only. No affiliation with any theme park or franchise.
