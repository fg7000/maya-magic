# Maya Magic

**Browser-based spell-casting for kids.** Open a URL in Chrome, wave any stick in front of your webcam, say a spell name, and watch a cinematic 3D wizard's study transform with magical effects. A wizard voice narrates the whole experience.

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

1. Click **Start Magic** to grant camera + microphone access
2. A 3D wizard's study appears: floating candles, bubbling cauldron, blinking owl, moonlit window
3. Wave any stick (wand, pencil, spatula) in front of your webcam. A golden particle trail follows.
4. Say a spell name out loud (or press keys 1-6) to cast spells
5. The entire 3D scene transforms with each spell

No special wand needed. No markers. No tape. Just grab a stick and go.

## Spells

| Key | Spell | Effect |
|-----|-------|--------|
| 1 | **Lumos** | Every candle blazes bright, golden particles explode, room fills with light |
| 2 | **Glacius** | Room freezes cold blue, cauldron turns to ice, frost particles spread |
| 3 | **Ignis** | Cauldron erupts with fire, orange glow fills the room, embers float |
| 4 | **Levitas** | Books float off shelves, blue particles spiral upward |
| 5 | **Nova** | Massive gold/white particle explosion, ceiling becomes starfield |
| 6 | **Tempest** | Candles blow out, room goes dark, wind streaks across screen |

## Controls

| Key | Action |
|-----|--------|
| 1-6 | Cast spells |
| D | Toggle debug overlay (FPS, particles, wand detection timing) |
| +/- | Adjust wand detection sensitivity |

On mobile/tablet: tap the spell icons at the bottom of the screen.

## Requirements

- **Chrome or Edge** (desktop, for full experience with camera + voice)
- Webcam
- Microphone (optional, for voice commands)
- Any stick-shaped object for your wand

Safari and Firefox: WebGL and keyboard spells work. Voice recognition may not (Web Speech API limitation). Keyboard shortcuts 1-6 always work.

## Architecture

Single `index.html` file (~400 lines). Three.js r168 + UnrealBloomPass loaded from esm.sh CDN. No build step, no npm, no bundler. Local server required for GLB model loading (see Try It above).

- **Rendering:** Three.js WebGLRenderer with EffectComposer (RenderPass + UnrealBloomPass)
- **Wand detection:** Frame differencing on a 160x120 downscaled canvas, mapped to 3D via Raycaster
- **Voice:** Web Speech API (SpeechRecognition) with fuzzy matching for kid mispronunciations
- **Audio:** All sounds procedurally generated via Web Audio API (no audio files)
- **Narrator:** SpeechSynthesis API with duplex policy (pauses recognition during narration)

## Privacy

Your camera feed is processed entirely on your device. It never leaves your browser. Voice recognition uses your browser's built-in speech service (Google's servers in Chrome). No data is collected or sent by this app.

## Project Structure

```
maya-magic/
  index.html           # The entire app
  scene.glb            # Dumbledore's Office 3D model
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
