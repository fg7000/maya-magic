# Changelog

All notable changes to Maya Magic will be documented in this file.

## [0.2.8.0] - 2026-04-09

### Fixed
- Wand trail particles now visible inside the room: reduced Raycaster projection distance from 2.0 to 1.0 units so particles spawn within room bounds instead of outside walls
- Trail particle material now uses `depthTest: false` so particles render in front of room geometry instead of being culled
- Trail particle size actually renders: fixed PointsMaterial uniform `size` from 0.15 to 0.25 (per-particle buffer attribute is ignored by PointsMaterial, only the uniform matters)

### Added
- Throttled debug logging in spawnTrailParticle (every 2s, logs world position for diagnosing particle placement)

## [0.2.7.0] - 2026-04-09

### Fixed
- Narrator no longer blocks speech recognition: removed all wand detection voice lines ("I see your wand") that paused listening via duplex policy
- Welcome line shortened to one sentence so recognition starts listening sooner
- After narrator finishes any line, 500ms delay then force-restart recognition to ensure mic is live
- Idle spell hint timer increased from 30s to 60s to reduce narrator interruptions

### Changed
- Recognition start/stop events now logged to console for debugging duplex timing

## [0.2.6.0] - 2026-04-09

### Added
- 10 real Harry Potter spells replace the original 6: Lumos, Nox, Wingardium Leviosa, Alohomora, Accio, Reparo, Expelliarmus, Incendio, Aguamenti, Expecto Patronum
- 7 new spell effects with unique visuals:
  - **Nox** — candles nearly extinguish, bloom drops, purple darkness particles
  - **Alohomora** — golden sparkles, doors/cabinets jiggle on their hinges
  - **Accio** — objects slide toward the caster, white streak particles
  - **Reparo** — warm golden glow, spiral particles converging inward
  - **Expelliarmus** — red flash, sharp camera shake, concentrated red particles
  - **Aguamenti** — blue water tint, candles dim, rain-like blue particles
  - **Expecto Patronum** — brilliant white-blue burst, bloom maxes out, 500 particles
- Voice state console logging (`[voice] speak:`, `[voice] narrator started/ended`) for debugging duplex policy

### Fixed
- Camera now starts inside the room at eye height instead of orbiting the exterior stone tower
- Exterior-only meshes (_front_mesh, _arch_0, _grunge_) hidden so you never see the outside
- Narrator no longer talks non-stop about the wand: cooldown increased to 10 seconds, wand-lost line removed entirely
- Speech queue capped at 1 item (replace, not accumulate) so narrator never backs up
- 2-second gap between queued voice lines gives speech recognition more listening time
- Spell hint threshold increased from 15s to 30s to reduce narrator interruptions

### Changed
- Keyboard shortcuts expanded from 1-6 to 1-0 (10 spells)
- Spell hint bar updated with all 10 spell names
- OrbitControls: pan disabled, polar angle constrained to prevent looking through floor/ceiling
- Auto-rotate speed reduced from default to 0.2 for gentler interior camera movement

## [0.2.5.0] - 2026-04-09

### Added
- Voice recognition: say spell names to cast (webkitSpeechRecognition, continuous mode, auto-restart)
- Kid-friendly fuzzy matching with 7+ pronunciation aliases per spell (e.g., "loomis" → Lumos)
- Wizard narrator via SpeechSynthesis: welcome greeting, spell announcements, wand coaching tips, streak encouragement
- Duplex policy: recognition pauses during narrator speech to prevent feedback loop
- 6 fully visual spell effects, each reversible after 4 seconds with 1-second smooth lerp back:
  - **Lumos** — candles blaze 3x, bloom intensifies, chandelier/glasslight glow gold, 200 gold particles
  - **Glacius** — candles dim to 15%, room tints frost-blue, stonewall/woodfloor/curtain color shift, 100 ice-blue particles
  - **Ignis** — candles blaze 4x, temporary fire PointLight, fire meshes scale 2x, 300 orange-red particles
  - **Levitas** — documents/props float upward with gentle bobbing, 100 light-blue spiral particles
  - **Nova** — bloom doubles, camera shakes, 500 gold+white particle supernova burst
  - **Tempest** — candles extinguish, camera shakes 1.5s, curtains/documents rotate in wind, 200 white/gray particles
- 5-second cooldown between spells with animated SVG radial indicator
- Spell hint bar ("Say: Lumos · Glacius · ...") that fades after 10 seconds of no interaction
- Procedural whoosh sound effect via Web Audio API (bandpass-filtered noise with exponential decay)
- Spell streak tracking with narrator encouragement at 3+ consecutive casts
- Wand coaching: narrator announces wand detection and suggests spells after 15 seconds of waving
- Mesh cataloging system: FBX meshes indexed by name for pattern-based spell targeting

### Changed
- Keyboard shortcuts 1-6 now trigger full visual spell effects (previously console-logged placeholders)
- Candle flicker system now reads `candleIntensityMultiplier` and `candleColorOverride` for spell modulation
- Debug overlay now shows active spell type, spell count, and spell state
- Animation loop integrates `updateSpell(dt)` for spell timing and camera shake

### Fixed
- Spell hint voice line no longer fires immediately after casting (lastSpellVoiceTime now updated in triggerSpell)

## [0.2.4.0] - 2026-04-09

### Added
- Webcam-based wand detection: wave any stick in front of camera, golden particle trail follows
- Frame differencing pipeline: getUserMedia → 160x120 downscaled canvas → motion centroid → EMA smoothing → Raycaster 3D projection
- Golden particle trail system: 1500-particle ring buffer with AdditiveBlending, gold→orange→red color fade, ~0.8s lifetime
- Wand status indicator ("Wand: Tracking" / "Wand: Scanning") overlays the 3D scene
- Keyboard shortcuts 1-6 to cast spells (Lumos, Glacius, Ignis, Levitas, Nova, Tempest), with console-logged placeholder effects
- Sensitivity controls: +/- keys adjust motion detection threshold
- Debug overlay (D key): FPS, active trail particles, wand detection timing, sensitivity level

### Fixed
- Prevented duplicate camera streams on double-click of Start Magic button
- Camera stream now properly released on page unload (beforeunload handler)
- Eliminated per-frame array allocation in particle update loop (filter→counter optimization)

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
