---
type: "API Reference"
title: "FOLLOW_PATH Constraint"
description: "Blender Python API for animating an object along a curve using the FOLLOW_PATH constraint and offset_factor keyframing."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#add_signal_particle"
tags: ["blender", "bpy", "constraint", "follow-path", "animation", "keyframe", "offset-factor"]
timestamp: "2026-07-11"
---

# FOLLOW_PATH Constraint

## Adding the constraint

```python
fmod = particle.constraints.new(type='FOLLOW_PATH')
fmod.target           = curve_obj        # the synapse curve object
fmod.use_curve_follow = True             # align rotation to curve tangent
fmod.use_fixed_location = True           # use offset_factor (0..1) not time offset
fmod.forward_axis     = 'TRACK_NEGATIVE_Y'
fmod.up_axis          = 'UP_Y'
```

`use_fixed_location = True` is the critical flag — without it, Blender uses the curve's built-in **Evaluation Time** property, which conflicts with multi-curve scenes where all curves share the same timeline slot. With `use_fixed_location`, the position is purely driven by `offset_factor`.

## Animating offset_factor

```python
fmod.offset_factor = 0.0
fmod.keyframe_insert(data_path="offset_factor", frame=start_frame)

fmod.offset_factor = 1.0
fmod.keyframe_insert(data_path="offset_factor", frame=start_frame + 30)
```

`offset_factor` goes from 0.0 (start of curve = pre-synaptic neuron) to 1.0 (end of curve = post-synaptic neuron) over `duration` frames. At 24 fps, 30 frames = 1.25 seconds per layer traversal.

## Interpolation

By default Blender inserts BEZIER keyframes, giving a smooth ease-in/ease-out. For constant-speed signals, change to LINEAR:

```python
action = particle.animation_data.action
for fcurve in action.fcurves:
    if fcurve.data_path.endswith("offset_factor"):
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
```

## Parent transform caveat

The particle's `location = (0, 0, 0)` must be set **before** adding FOLLOW_PATH. If the object has a non-zero rest location, the constraint adds that offset to the curve position, causing the particle to miss the curve endpoints.

## Common mistake: FOLLOW_TRACK before FOLLOW_PATH

The original script adds `FOLLOW_TRACK` (for camera tracking, unrelated) before adding `FOLLOW_PATH`. While FOLLOW_PATH overrides it, the orphaned constraint wastes resources. See [script-reference/known-bugs.md](../script-reference/known-bugs.md).

## Cross-links

- [concepts/signal-propagation.md](../concepts/signal-propagation.md) — animation design
- [stages/04-animate.md](../stages/04-animate.md) — how this fits the PDLC
