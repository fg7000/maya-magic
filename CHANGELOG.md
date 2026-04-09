# Changelog

All notable changes to Maya Magic will be documented in this file.

## [0.2.3.0] - 2026-04-09

### Changed
- Switched from GLTFLoader/GLB to FBXLoader/FBX for the Dumbledore's Office model, resolving texture issues caused by GLB format conversion
- FBX textures load directly from `model/source/` (17 PNG files), no format conversion needed
- Diagnostic logging now handles FBX material arrays (meshes can have multiple materials)
- Camera collision bounds keep the camera inside the room (`maxDistance = 0.9 * bounding box`)

### Fixed
- Fixed diagnostic `logMeshInfo()` crash when FBX mesh has a material array (Array.prototype.map collision)
- Fixed stale "GLB loading" reference in file:// protocol error message

## [0.2.2.0] - 2026-04-08

### Fixed
- Fixed missing textures on GLB model: converted `scene.glb` from deprecated `KHR_materials_pbrSpecularGlossiness` (unsupported by Three.js r168) to standard `pbrMetallicRoughness` using gltf-transform
- Fixed dark/black scene: set `outputColorSpace = SRGBColorSpace` on renderer and increased ambient + moonlight intensity
- Fixed invisible model: GLB bounding box was ~0.1 units, added 100x scale so geometry fills the viewport

### Added
- Diagnostic texture logging in debug output: per-mesh texture status, map dimensions, colorSpace, GLTF extension metadata

### Changed
- Updated CLAUDE.md to reflect esm.sh CDN, GLB model architecture, and server requirement

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
