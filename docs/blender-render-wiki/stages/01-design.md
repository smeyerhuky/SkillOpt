---
type: "PDLC Stage"
title: "Stage 1 — Design"
description: "Define the visualization goals, network architecture, spatial layout, and animation story before touching Blender."
resource: "file:///home/user/SkillOpt/docs/blender-render-wiki/index.md"
tags: ["pdlc", "design", "architecture", "layout", "animation-story"]
timestamp: "2026-07-11"
---

# Stage 1 — Design

## Goal

Decide *what* the animation needs to communicate before writing a line of Blender Python. The design stage produces three concrete artefacts: a **network spec**, a **spatial layout spec**, and an **animation story**.

## 1.1 Network spec

For this pipeline, the network is fixed:

```
layer_sizes   = [4, 6, 5, 3]   # Input, Hidden1, Hidden2, Output
activation    = ReLU (hidden), Softmax (output)
dataset       = Iris flower (150 samples, 4 features, 3 classes)
sample_input  = [5.1, 3.5, 1.4, 0.2]  # Iris-setosa specimen
```

The sample input is chosen to produce a **decisive classification** (high softmax confidence for class 0) so the animation has a clear visual winner in the output layer.

## 1.2 Spatial layout spec

| Parameter | Value | Rationale |
|---|---|---|
| `layer_spacing` | 4.0 | Room for signal spheres and readable synapse angles |
| `neuron_spacing` | 2.0 | Prevents neuron overlap for the widest layer (6 neurons, 10 units tall) |
| Coordinate system | X = depth (layer), Y = height (neuron), Z = 0 | Renders cleanly from a front-facing camera |
| Camera position | `(6, 0, 18)` pointing at `(6, 0, 0)` | Frames all 4 layers; tilt 70° for slight perspective |

## 1.3 Animation story

The animation tells a forward-pass narrative in three acts:

| Frames | Act | What happens |
|---|---|---|
| 1–30 | Layer 0 → 1 | Input signals travel to Hidden 1 |
| 35–65 | Layer 1 → 2 | Hidden 1 signals travel to Hidden 2 |
| 70–100 | Layer 2 → 3 | Hidden 2 signals arrive at output; class-0 neuron brightens |
| 100–120 | Hold | Output state held; winning neuron glows at full emission |

Total: 120 frames at 24 fps = **5 seconds**.

## 1.4 Rendering targets

| Setting | Value |
|---|---|
| Resolution | 1920 × 1080 (Full HD) |
| Samples (Cycles) | 128 (fast preview: 32) |
| Output format | PNG sequence → FFmpeg MP4 |
| Background | Pure black `(0, 0, 0, 1)` — makes glowing signals pop |

## Outputs of this stage

- `layer_sizes`, `layer_spacing`, `neuron_spacing` constants embedded in the script
- Pre-trained weight arrays (computed in [Stage 2](./02-data.md))
- A sample input vector and its expected class
- Camera and render settings for [Stage 5](./05-render.md)

## Cross-links

- [stages/02-data.md](./02-data.md) — next: compute real weights
- [concepts/network-architecture.md](../concepts/network-architecture.md) — architecture rationale
