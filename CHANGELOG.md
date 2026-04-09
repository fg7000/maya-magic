# Changelog

All notable changes to Maya Magic will be documented in this file.

## [0.2.1.0] - 2026-04-08

### Fixed
- Fixed `ReferenceError: moteOpacities is not defined` crash on page load (missing Float32Array declaration)
- Added `file://` protocol detection with user-friendly message and instructions when Chrome blocks GLB loading from local files

### Added
- `start.sh` helper script for one-command local dev server (`bash start.sh`)

### Changed
- Updated README quick start to use `start.sh` instead of `open index.html`
- Fixed README architecture section: corrected CDN reference (esm.sh, not jsDelivr) and line count (~400, not ~2000), noted server requirement for GLB loading

## [0.2.0.0] - 2026-04-08

### Changed
- Replaced procedural 3D scene with real Dumbledore's Office GLB model (scene.glb)
- Rewrote index.html from scratch as visual foundation only (no spells, voice, or camera detection)
- Switched to `<script type="importmap">` for clean ES module imports
- Added GLTFLoader pipeline with loading progress bar
- Cinematic lighting: 4 flickering candle PointLights, moonlight DirectionalLight with PCFSoftShadowMap shadows
- 80 dust mote particles with AdditiveBlending and oscillating opacity
- OrbitControls with auto-rotate for interactive camera
- EffectComposer with UnrealBloomPass post-processing (strength 1.0, radius 0.4, threshold 0.7)
- Dynamic camera positioning from GLB bounding box
- Title overlay with fade-out on first interaction
- Debug mode (press D) showing FPS counter and mesh names in console

### Removed
- All procedural geometry (flat-box bookshelves, sphere-stack owls, cylinder candles)
- Spell system, voice recognition, wand detection, audio engine, narrator (to be re-added later)
- Particle pool system (replaced with simple dust motes)

## [0.1.0.0] - 2026-04-07

### Added
- Initial WebGL version with Three.js r168, procedural scene, 6 spells, voice recognition
- Camera-based wand detection with frame differencing
- Web Audio procedural synthesis
- GitHub Pages deployment via `.github/workflows/pages.yml`
