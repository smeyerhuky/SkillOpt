---
type: "Bug Catalog"
title: "Known Bugs in the Original Script"
description: "Five bugs in the original Blender neural network script that prevent correct color rendering and signal animation, including two Blender 4.2 API regressions."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["bugs", "material-sharing", "follow-track", "particles", "phase-3", "hide-render", "blender-4.2"]
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

---

## Bug 5 — `hide_render` boolean keyframes silently fail in Blender 4.2 (Blender API regression)

**Location**: `add_signal_particle()` — visibility toggling via `hide_render` boolean property.

**What happens**: In Blender 4.2, calling `obj.keyframe_insert(data_path="hide_render", frame=N)` produces no error but stores no keyframe. The property appears to accept the call but the fcurve is never written. All signal particles are therefore permanently hidden from rendering — they exist in the scene but are never visible in any frame.

**Confirmed by**: Pixel analysis of all 120 rendered frames showing exactly 0 yellow pixels (expected: warm-white blobs per frame where signals are active).

**Symptom**: Animation appears completely static — neuron emission is visible but no yellow signal particles ever appear in any frame.

**Fix**: Replace `hide_render` keyframes with `scale` keyframes:

```python
# BROKEN in Blender 4.2 — silently does nothing:
p.hide_render = True
p.keyframe_insert(data_path="hide_render", frame=start_frame - 1)
p.hide_render = False
p.keyframe_insert(data_path="hide_render", frame=start_frame)

# WORKING in all Blender versions:
p.scale = (0.0, 0.0, 0.0)
p.keyframe_insert(data_path="scale", frame=max(1, start_frame - 1))
p.scale = (1.0, 1.0, 1.0)
p.keyframe_insert(data_path="scale", frame=start_frame)
p.scale = (0.0, 0.0, 0.0)
p.keyframe_insert(data_path="scale", frame=end_frame + 1)
```

Node property keyframes (e.g. `Emission Strength`) work correctly in Blender 4.2 — the regression is specific to boolean object properties.

---

## Bug 6 — FOLLOW_PATH `offset_factor` constraint keyframes unreliable in headless render (Blender 4.2)

**Location**: `add_signal_particle()` — the FOLLOW_PATH constraint with `offset_factor` keyframes.

**What happens**: Even after fixing Bug 5 (visibility), using a `FOLLOW_PATH` constraint with `offset_factor` keyframes in headless Blender 4.2 render produces particles that don't move along the path. The constraint is evaluated but the keyframed `offset_factor` values don't animate correctly outside of an interactive session.

**Symptom**: Signal particles appear at the constraint's default position (frame 0 of the curve) in every frame rather than traveling along the synapse.

**Fix**: Remove the `FOLLOW_PATH` constraint entirely. Use direct `location` keyframes instead:

```python
# Direct location keyframes — reliable in all Blender versions:
p.location = start_pos
p.keyframe_insert(data_path="location", frame=start_frame)
p.location = end_pos
p.keyframe_insert(data_path="location", frame=end_frame)

# Set LINEAR interpolation so motion is constant-speed:
for fc in p.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'
```

This also eliminates the need for `create_synapse` to return an object with path constraints, simplifying the call site.

**Note**: Bugs 5 and 6 compound — if `hide_render` is fixed but FOLLOW_PATH is kept, particles appear but don't move. Both must be fixed together for animated signal propagation.

---

## Cross-links

- [script-reference/improved-script.md](./improved-script.md) — all bugs fixed in corrected script
- [concepts/synapse-as-curve.md](../concepts/synapse-as-curve.md) — Bug 1 context
- [concepts/signal-propagation.md](../concepts/signal-propagation.md) — Bugs 2, 3, 5 & 6 context
