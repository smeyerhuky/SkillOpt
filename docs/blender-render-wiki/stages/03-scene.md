---
type: "PDLC Stage"
title: "Stage 3 — Scene Construction"
description: "Phase 1 (neurons) and Phase 2 (synapses) of the Blender script: building the static 3D topology with real weights."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["pdlc", "blender", "scene", "neurons", "synapses", "construction"]
timestamp: "2026-07-11"
---

# Stage 3 — Scene Construction

This stage runs the Blender script's Phase 1 and Phase 2. All geometry is static at this point — no animation yet.

## Phase 1: Neuron placement (Empties)

For each layer `i` with `layer_sizes[i]` neurons, the script:
1. Creates collection `Layer_{i}`
2. Calculates `start_y = -(size-1) * neuron_spacing / 2` to centre the layer
3. Places an Empty SPHERE at `(i * layer_spacing, start_y + j * neuron_spacing, 0)`
4. Names it `L{i}_N{j}` and links to the layer collection

**Improved version** replaces Empties with icospheres whose Emission strength is set to `activation_value * 5.0`. Hidden neurons use `a1[j]` / `a2[j]`; output neurons use `a3[k]`. Input neurons use `1.0` (always active).

## Phase 2: Synapse construction (Bezier curves)

For every pair `(n_a in layer_i, n_b in layer_{i+1})`:
1. Compute `weight = W{i+1}[n_a_idx, n_b_idx]` from the loaded weight matrix
2. Call `create_synapse(name, n_a.location, n_b.location, weight)`
3. Each call creates a unique material named `Mat_{i}_{j}_{k}` (fix for the shared-material bug)

**Store references** — in the improved script, `synapses[i][j][k]` holds the curve object for layer `i`, pre-synaptic neuron `j`, post-synaptic neuron `k`. The Phase 3 loop needs these references; looking up by name (as the original does) is O(N) over all objects.

## Scene inspection checklist

After running Phases 1 and 2, verify in the Blender viewport:

- [ ] 20 Empty spheres (4+6+5+3 = 20 total) visible in viewport
- [ ] 69 curve objects visible (check Object Count in viewport statistics)
- [ ] Synapse colors mix red and green — not all the same color (confirms unique materials)
- [ ] Thicker curves connect inputs to Hidden 1 neurons 2 and 3 (petal-length/width features with large weights)
- [ ] Layer collections `Layer_0` through `Layer_3` visible in Outliner

## Running in Blender

```bash
# Headless scene construction (no render)
blender --background --python scripts/blender_nn_render.py -- --stage=scene

# Or open in Blender GUI:
blender scripts/empty_scene.blend --python scripts/blender_nn_render.py
```

## Expected scene stats

| Metric | Value |
|---|---|
| Objects | 20 (neurons) + 69 (synapses) + 69 (particles, after Phase 3) |
| Materials | 69 (one per synapse) + 20 (one per neuron) |
| Collections | 5 (scene root + Layer_0 through Layer_3) |
| Scene bounding box | ~12 × 10 × 0.4 Blender units |

## Cross-links

- [stages/02-data.md](./02-data.md) — weights that drive synapse colors
- [stages/04-animate.md](./04-animate.md) — next: add signal particles
- [concepts/neuron-as-empty.md](../concepts/neuron-as-empty.md) — Empty design
- [concepts/synapse-as-curve.md](../concepts/synapse-as-curve.md) — curve design
- [blender-api/scene-collections.md](../blender-api/scene-collections.md) — collection API
