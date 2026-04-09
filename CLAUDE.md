# Maya Magic

Browser-based spell-casting experience for kids. Single HTML file, Three.js r168, WebGL + UnrealBloomPass. Zero dependencies, zero build step.

## Architecture

Single-file app (`index.html`, ~480 lines). Three.js + post-processing loaded from esm.sh CDN via `<script type="importmap">`. Requires HTTP server for FBX model loading (Chrome blocks `fetch()` on `file://`).

**Rendering pipeline:** WebGLRenderer → EffectComposer → RenderPass → UnrealBloomPass → canvas output. ACESFilmicToneMapping. Bloom: strength 1.0, radius 0.4, threshold 0.7.

**Scene:** Dumbledore's Office FBX model (`model/source/DumbledoreOffice.fbx`) loaded via FBXLoader with 17 separate PNG textures. 4 flickering candle PointLights, moonlight DirectionalLight with PCFSoftShadowMap shadows. OrbitControls with auto-rotate. Camera collision bounds prevent escaping the room.

**Particles:** 80 dust motes with AdditiveBlending and oscillating opacity. Simple Points geometry (no object pooling in current version).

**Status:** Visual foundation only. Spells, voice recognition, wand detection, audio engine, and narrator are planned but not yet re-implemented after the v0.2.0 rewrite.

## Key File

- `index.html` — the entire app (scene, spells, detection, audio, voice, UI, error handling)

## Running Locally

```bash
bash start.sh
# Or manually: python3 -m http.server 8000
```

Local server required because Chrome blocks FBX model loading from `file://` URLs. The app detects `file://` protocol and shows instructions.

## Deployment

GitHub Pages via `.github/workflows/pages.yml`. Push to `webgl` branch → auto-deploy. No build step.

## Code Organization (index.html sections)

1. Import map (Three.js r168 from esm.sh)
2. Loading UI + file:// protocol detection
3. Three.js setup (renderer, scene, camera, controls, post-processing)
4. FBX model loading (FBXLoader with progress bar)
5. Lighting (candle PointLights with flicker, moonlight DirectionalLight)
6. Dust mote particles (80 motes, AdditiveBlending)
7. Title overlay with fade-out on interaction
8. Debug mode (press D for FPS counter)
9. Animation loop (candle flicker, dust mote oscillation, controls update)

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
