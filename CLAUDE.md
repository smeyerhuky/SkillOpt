# SkillOpt — Working Notes for Claude Sessions

## Blender Neural Network Render Pipeline

This repo contains an OKF deep-wiki for the **Blender neural network animation render pipeline** at `docs/blender-render-wiki/`. It decomposes the agentic PDLC (Product Development Life Cycle) for building, animating, and rendering a [4, 6, 5, 3] Iris-classifier neural network in Blender Python into small, cross-linked markdown files.

## What OKF is (spec summary)

OKF ([spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)) is a convention for representing knowledge as a directory of markdown files with YAML frontmatter:

- **Required frontmatter field**: `type` (free text — types used here: `"Concept"`, `"PDLC Stage"`, `"API Reference"`, `"Bug Catalog"`, `"Script Reference"`, `"Bundle Root"`).
- **Recommended fields**: `title`, `description`, `resource`, `tags`, `timestamp`.
- **Reserved filenames**: `index.md` (no frontmatter, acts as ToC), `log.md` (changelog), `CLAUDE.md` (agent instructions — this file).
- `okf_version: "0.1"` appears **only** in `docs/blender-render-wiki/index.md` — nowhere else.

## Directory map

```
CLAUDE.md                         this file (sibling of the bundle, not inside it)
scripts/blender_nn_render.py      the Blender visualization script
scripts/train_iris_classifier.py  NumPy training script (produces nn_weights.npy)
scripts/nn_weights.npy            pre-trained weights (generated, not committed)

docs/blender-render-wiki/
  index.md                        root bundle entry point (okf_version here)
  log.md                          change history
  stages/                         5 PDLC pipeline stages in execution order
    01-design.md                  network spec, layout, animation story, render targets
    02-data.md                    training the Iris classifier with NumPy
    03-scene.md                   Phase 1 & 2: neurons and synapses
    04-animate.md                 Phase 3: signal particles with FOLLOW_PATH
    05-render.md                  camera, lighting, Cycles settings, headless render
  concepts/                       5 core design ideas
    network-architecture.md       [4,6,5,3] Iris classifier rationale
    neuron-as-empty.md            Empty SPHERE as neuron representation
    synapse-as-curve.md           Bezier curve as synapse (with thickness/color)
    weight-encoding.md            green/red + thickness = sign/magnitude encoding
    signal-propagation.md         FOLLOW_PATH offset_factor animation design
  blender-api/                    4 Blender Python API reference files
    scene-collections.md          bpy.data.collections, scene clearing
    bezier-curves.md              curve data, splines, bevel_depth
    follow-path.md                FOLLOW_PATH constraint, offset_factor keyframing
    materials-nodes.md            Principled BSDF, emission, per-synapse materials
  script-reference/               original script → bugs → improved version
    known-bugs.md                 4 bugs: shared material, FOLLOW_TRACK, pass stub, random weights
    improved-script.md            complete corrected script with real weights + camera + lighting
```

## How this bundle was built

1. The user provided a Blender Python script for neural network visualization (the original, buggy version).
2. The SkillOpt repo was explored for context.
3. Material was decomposed **by hand into one concept/stage/reference per file** — not a mechanical split.
4. Four bugs in the original script were identified and catalogued; a corrected version was written.
5. The network architecture was matched to the Iris dataset (perfect [4,6,5,3] fit: 4 features, 3 classes).
6. A NumPy-only training script was written to produce real weights without ML framework dependencies.

## How to use this bundle

- **Start from** `docs/blender-render-wiki/index.md` for the full picture.
- **To execute the pipeline**: follow stages 01 → 05 in `stages/`.
- **To understand a design choice**: look in `concepts/`.
- **To debug a Blender API call**: look in `blender-api/`.
- **To understand the original script's bugs**: `script-reference/known-bugs.md`.
- **When citing a claim from this bundle**, include the file path alongside the answer so it's verifiable.

## Running the lint checker

```bash
python3 ~/.claude/skills/okf-wikify/scripts/lint_okf.py docs/blender-render-wiki/
```

## Execution prerequisites

```bash
# 1. Train and export weights (requires numpy only)
python3 scripts/train_iris_classifier.py

# 2a. Render — single process (simple)
blender --background --python scripts/blender_nn_render.py -a

# 2b. Render — parallel (3-4× faster on CPU; N = core count)
N=$(nproc); CHUNK=$(( (120 + N - 1) / N ))
for i in $(seq 0 $((N-1))); do
  S=$(( i*CHUNK+1 )); E=$(( (i+1)*CHUNK )); [ $E -gt 120 ] && E=120
  nohup blender --background --threads 1 --python scripts/blender_nn_render.py \
        -s $S -e $E -a > /tmp/bl_w${i}.log 2>&1 &
done; wait

# 3. Assemble MP4 (requires ffmpeg)
ffmpeg -framerate 24 -i render/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output/nn_animation.mp4
```

See `docs/blender-render-wiki/stages/05-render.md` for the full parallel technique rationale and resume-from-crash instructions.

## Extending this bundle

Add new files matching the existing frontmatter schema (`type`, `title`, `description`, `resource`, `tags`, `timestamp`), link from the relevant `index.md`, and re-run the linter. Do not add `okf_version` to any file other than the root `index.md`.
