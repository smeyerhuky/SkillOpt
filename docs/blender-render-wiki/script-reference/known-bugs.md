---
type: "Bug Catalog"
title: "Known Bugs in the Original Script"
description: "Three bugs in the original Blender neural network script that prevent correct color rendering and signal animation."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["bugs", "material-sharing", "follow-track", "particles", "phase-3"]
timestamp: "2026-07-11"
---

# Known Bugs in the Original Script

## Bug 1 — Shared material (all synapses same color)

**Location**: `create_synapse()`, the `bpy.data.materials.get("Synapse_Mat")` block.

**What happens**: Every call to `create_synapse` checks whether `"Synapse_Mat"` already exists. After the first call it does, so every subsequent call reuses the *same* material object. The color is then overwritten on every call — all 69 synapses end up the color of the **last synapse processed**.

**Symptom**: All synapse tubes are the same color (last processed weight's color — red or green depending on the last random weight's sign).

**Fix**: Create a unique material per synapse. Replace:

```python
mat = bpy.data.materials.get("Synapse_Mat")
if not mat:
    mat = bpy.data.materials.new("Synapse_Mat")
```

With:

```python
mat = bpy.data.materials.new(f"Mat_{name}")
```

Full fix in [script-reference/improved-script.md](./improved-script.md).

---

## Bug 2 — Orphaned FOLLOW_TRACK constraint

**Location**: `add_signal_particle()`, lines adding `FOLLOW_TRACK` before `FOLLOW_PATH`.

**What happens**: The script adds a `FOLLOW_TRACK` constraint (used for camera tracking, not path following) and then immediately adds a `FOLLOW_PATH` constraint. The `FOLLOW_TRACK` has no target set, so it silently no-ops, but it remains on every particle object, generating a Blender warning ("constraint has no target") and consuming memory.

**Symptom**: Console warnings about missing constraint targets; particles still follow the path (because `FOLLOW_PATH` overrides).

**Fix**: Delete the `FOLLOW_TRACK` lines entirely. The `FOLLOW_TRACK` constraint is not needed and was likely a copy-paste error from a camera-tracking example.

---

## Bug 3 — Phase 3 loop body is `pass` (no particles ever created)

**Location**: The `for n_a in layer_a / for n_b in layer_b` loop at the bottom of Phase 3.

**What happens**: The loop body is `pass` with a comment "Omitted to keep script execution time reasonable". The `add_signal_particle` function is defined but never called. **No signal particles are created**.

**Symptom**: The script prints "Neural Network Topology Generated." and exits with a static scene — no animation.

**Fix**: Replace `pass` with actual calls to `add_signal_particle`, indexed by layer and staggered by frame. Full implementation in [stages/04-animate.md](../stages/04-animate.md) and [script-reference/improved-script.md](./improved-script.md).

---

## Bug 4 — Random weights (no real data)

**Status**: Design gap, not a code crash.

The original uses `random.uniform(-1, 1)` for every weight. The result is a visually random scene that doesn't encode any real network behaviour.

**Fix**: Load pre-trained weights from `scripts/nn_weights.npy` (produced by [stages/02-data.md](../stages/02-data.md)) and use `W{i+1}[j, k]` for the weight between neurons `j` (layer `i`) and `k` (layer `i+1`).

## Cross-links

- [script-reference/improved-script.md](./improved-script.md) — all four bugs fixed
- [concepts/synapse-as-curve.md](../concepts/synapse-as-curve.md) — Bug 1 context
- [concepts/signal-propagation.md](../concepts/signal-propagation.md) — Bugs 2 & 3 context
