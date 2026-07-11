---
okf_version: "0.1"
type: "Bundle Root"
title: "Blender Neural Network Render — OKF Deep Wiki"
description: "Agentic PDLC knowledge base for animating and rendering a number-classifier neural network in Blender using real trained weights."
resource: "file:///home/user/SkillOpt/docs/blender-render-wiki/"
tags: ["blender", "neural-network", "animation", "render", "pdlc", "iris", "bpy"]
timestamp: "2026-07-11"
---

# Blender Neural Network Render — Deep Wiki

This bundle is an **OKF (Open Knowledge Format) deep wiki** decomposing the agentic pipeline for visualizing a [4, 6, 5, 3] Iris-flower classifier neural network as a Blender animation. It covers everything from training real network weights through scene construction, signal animation, and headless rendering to a final MP4.

The source is a user-provided Blender Python script (`scripts/blender_nn_render.py`) plus the SkillOpt repository context. Four bugs in the original script are catalogued and fixed. The improved script embeds a NumPy-trained Iris classifier whose weights drive synapse colors and neuron glow in the final render.

## Directory map

```
docs/blender-render-wiki/
├── index.md               this file
├── log.md                 change history
├── stages/                the 5 PDLC pipeline stages in order
├── concepts/              5 core ideas (architecture, geometry, encoding, animation)
├── blender-api/           4 Blender Python API reference files
└── script-reference/      original bug catalog + complete improved script
```

## Table of contents

* [stages/](./stages/index.md) — Run these five stages in sequence to go from idea to rendered video
* [concepts/](./concepts/index.md) — The design decisions and representation choices behind the script
* [blender-api/](./blender-api/index.md) — Blender Python API patterns referenced in the script
* [script-reference/](./script-reference/index.md) — Bug catalog and the corrected full script

## Quick-start for a Claude session

1. Start from [stages/01-design.md](./stages/01-design.md) for an overview of what to build.
2. Run `python3 scripts/train_iris_classifier.py` ([stages/02-data.md](./stages/02-data.md)) to produce `scripts/nn_weights.npy`.
3. Run `blender --background --python scripts/blender_nn_render.py --render-anim` ([stages/05-render.md](./stages/05-render.md)).
4. If a bug appears, check [script-reference/known-bugs.md](./script-reference/known-bugs.md) first.

## Original source

The original Blender script lives at `scripts/blender_nn_render.py`. The sibling `CLAUDE.md` at the repo root contains agent operating instructions for working with this bundle.
