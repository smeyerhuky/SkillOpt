---
type: "Concept"
title: "Neuron as Empty Object"
description: "How Blender Empty objects with SPHERE display type represent neurons in the 3D scene."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#PHASE-1"
tags: ["blender", "empty", "neuron", "geometry", "positioning"]
timestamp: "2026-07-11"
---

# Neuron as Empty Object

Each neuron is a Blender **Empty** (no mesh geometry) with `empty_type = 'SPHERE'` and `empty_size = 0.5`. Empties are chosen over mesh spheres because:

1. **No render cost** — Empties don't appear in renders by default; they serve as transform anchors for curve endpoints and particle follow-path targets.
2. **Viewport clarity** — The SPHERE display shows a wireframe globe at the correct radius, making the topology legible without visual clutter.
3. **Parent-ready** — Signal particles parent to the Empty's world position for the follow-path animation.

## Positioning formula

```python
total_height = (size - 1) * neuron_spacing   # neuron_spacing = 2.0
start_y      = -total_height / 2             # center the layer vertically
x = i * layer_spacing                        # layer_spacing = 4.0
y = start_y + j * neuron_spacing
z = 0
```

For the 6-neuron hidden layer: `total_height = 10`, `start_y = -5`, neurons at y = -5, -3, -1, 1, 3, 5.

## Naming convention

`L{layer_index}_N{neuron_index}` — e.g. `L0_N0` is the first input neuron, `L3_N2` is the third output neuron. The naming is used to look up objects by name in Phase 3 (signal particles).

## Collection organisation

Each layer's neurons are linked to a dedicated collection `Layer_{i}`, which groups them in the Outliner for visibility toggling during animation review.

## Extended version: mesh neurons

In the improved script ([script-reference/improved-script.md](../script-reference/improved-script.md)), neurons are replaced with icospheres whose **Emission strength** is driven by the neuron's activation value for a sample input — see [concepts/signal-propagation.md](./signal-propagation.md).

## Cross-links

- [concepts/synapse-as-curve.md](./synapse-as-curve.md) — curves use neuron `.location` as endpoints
- [blender-api/scene-collections.md](../blender-api/scene-collections.md) — collection setup API
