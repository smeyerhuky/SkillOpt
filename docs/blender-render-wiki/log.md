## 2026-07-11

* **Creation**: Initial OKF bundle built from the user-provided Blender neural network script and SkillOpt repo context. Five directories: stages/ (PDLC pipeline), concepts/ (core ideas), blender-api/ (API reference), script-reference/ (original + improved script). Four bugs catalogued and fixed in improved-script.md.
* **Parallel render technique**: Added to `stages/05-render.md` and `CLAUDE.md`. On a 4-core CPU-only machine, running one Blender instance per core with `--threads 1` across non-overlapping frame ranges achieves ~3× wall-clock speedup over the default single-process render. Validated during headless render of the 120-frame Iris classifier animation (16 Cycles samples + denoising, 1920×1080).
