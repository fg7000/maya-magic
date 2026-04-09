# Maya Magic

**Browser-based spell-casting for kids.** Open a URL in Chrome, wave any stick in front of your webcam, and watch a golden particle trail follow your wand through a cinematic 3D wizard's study. Press 1-6 to cast spells.

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
4. Press keys 1-6 to cast spells (visual effects coming soon, keyboard triggers work now)

No special wand needed. No markers. No tape. Just grab a stick and go.

## Spells

| Key | Spell | Status |
|-----|-------|--------|
| 1 | **Lumos** | Keyboard trigger ready, visual effects coming |
| 2 | **Glacius** | Keyboard trigger ready, visual effects coming |
| 3 | **Ignis** | Keyboard trigger ready, visual effects coming |
| 4 | **Levitas** | Keyboard trigger ready, visual effects coming |
| 5 | **Nova** | Keyboard trigger ready, visual effects coming |
| 6 | **Tempest** | Keyboard trigger ready, visual effects coming |

## Controls

| Key | Action |
|-----|--------|
| 1-6 | Cast spells |
| D | Toggle debug overlay (FPS, particles, wand detection timing) |
| +/- | Adjust wand detection sensitivity |

On mobile/tablet: keyboard spells require a physical keyboard. Touch spell UI coming in a future version.

## Requirements

- **Chrome or Edge** (desktop, for camera + WebGL)
- Webcam
- Any stick-shaped object for your wand

Safari and Firefox: WebGL and keyboard spells work. Wand detection requires getUserMedia support. Keyboard shortcuts 1-6 always work.

## Architecture

Single `index.html` file (~740 lines). Three.js r168 + UnrealBloomPass loaded from esm.sh CDN. No build step, no npm, no bundler. Local server required for FBX model loading (see Try It above).

- **Rendering:** Three.js WebGLRenderer with EffectComposer (RenderPass + UnrealBloomPass)
- **Wand detection:** getUserMedia → 160x120 downscaled canvas → frame differencing → EMA-smoothed motion centroid → Raycaster 3D projection
- **Particles:** 80 dust motes + 1500 trail particles (ring buffer, gold→orange→red fade, ~0.8s lifetime)

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
