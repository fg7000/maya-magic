# Maya Magic

Browser-based spell-casting experience for kids. Single HTML file, Three.js r168, WebGL + UnrealBloomPass. Zero dependencies, zero build step.

## Architecture

Single-file app (`index.html`). All code inline, Three.js + post-processing from jsDelivr CDN via ES module imports.

**Rendering pipeline:** WebGLRenderer → EffectComposer → RenderPass → UnrealBloomPass → canvas output. ACESFilmicToneMapping. Bloom: strength 1.0, radius 0.4, threshold 0.6.

**Wand detection:** getUserMedia → 160x120 hidden canvas (willReadFrequently) → frame differencing → motion region → Raycaster NDC mapping → 3D particle spawn at depth 2.0.

**Voice:** webkitSpeechRecognition with fuzzy matching + kid mispronunciation aliases. Duplex policy: recognition pauses during narrator speech to prevent feedback loop.

**Audio:** All procedural via Web Audio API. No audio files.

**Particles:** Object pool pattern (ParticlePool class). 300 trail + 300 spell + 150 ambient = 750 total pre-allocated.

**Spells:** DRY castSpell pattern. Each spell returns a cleanup function. One active at a time (ignore new casts during active spell).

## Key File

- `index.html` — the entire app (scene, spells, detection, audio, voice, UI, error handling)

## Running Locally

```bash
open index.html  # Chrome
# or: python3 -m http.server 8000
```

## Deployment

GitHub Pages via `.github/workflows/pages.yml`. Push to `webgl` branch → auto-deploy. No build step.

## Code Organization (section separators in index.html)

1. CDN Imports (Three.js r168 from jsdelivr)
2. Constants/Config (CONFIG object, all tunable parameters)
3. Audio Engine (Web Audio procedural synthesis)
4. Particle System (ParticlePool class, object pooling)
5. Scene Builder (room geometry, candles, cauldron, owl, bookshelves, window)
6. Wand Detection (frame differencing, raycaster mapping)
7. Voice Recognition (fuzzy match, aliases, watchdog)
8. Narrator (SpeechSynthesis, duplex policy)
9. Spell Effects (6 spells, each with apply + cleanup)
10. UI Overlay (title, hints, touch-to-cast, debug mode)
11. Error Handling + Performance Degradation (progressive: shadows → bloom → particles)
12. Main Loop + Initialization (10-step init sequence)

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
