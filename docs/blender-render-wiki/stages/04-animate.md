---
type: "PDLC Stage"
title: "Stage 4 — Animation"
description: "Phase 3 of the Blender script: adding signal spheres and FOLLOW_PATH keyframes to animate forward-pass propagation."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#PHASE-3"
tags: ["pdlc", "animation", "follow-path", "keyframe", "signal", "forward-pass"]
timestamp: "2026-07-11"
---

# Stage 4 — Animation

## What this stage produces

One icosphere per active synapse, travelling from source to target neuron over 30 frames, staggered by layer so the animation reads left-to-right as a forward pass.

## Frame budget

```
Layer 0→1 signals:  frames   1–31
Layer 1→2 signals:  frames  35–65
Layer 2→3 signals:  frames  70–100
Output hold:        frames 101–120
```

Total scene length: 120 frames. Set in the script with:
```python
bpy.context.scene.frame_end = 120
```

## Activation gating

Only spawn a particle when the pre-synaptic activation exceeds a threshold:

```python
ACTIVATION_THRESHOLD = 0.05

for i in range(len(neurons) - 1):
    W = weights[i]          # W1, W2, or W3
    activations = [a1, a2, a1][i]   # source layer activations

    for j, n_a in enumerate(neurons[i]):
        if activations[j] < ACTIVATION_THRESHOLD:
            continue        # skip silent neurons — no particles from here

        for k, n_b in enumerate(neurons[i+1]):
            synapse = synapses[i][j][k]
            start   = layer_start_frames[i]
            add_signal_particle(synapse, start)
```

`layer_start_frames = [1, 35, 70]`. Input neurons (layer 0) always have activation 1.0, so all 4 inputs always fire.

## The `add_signal_particle` function (corrected)

```python
def add_signal_particle(synapse_obj, start_frame):
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=0.12,
        location=(0, 0, 0)
    )
    particle = bpy.context.active_object
    particle.name = f"Signal_{synapse_obj.name}"

    # Remove any accidental default location
    particle.location = (0, 0, 0)

    # FOLLOW_PATH constraint (no FOLLOW_TRACK — that was a bug)
    fmod = particle.constraints.new(type='FOLLOW_PATH')
    fmod.target             = synapse_obj
    fmod.use_curve_follow   = True
    fmod.use_fixed_location = True
    fmod.forward_axis       = 'TRACK_NEGATIVE_Y'
    fmod.up_axis            = 'UP_Y'

    fmod.offset_factor = 0.0
    fmod.keyframe_insert(data_path="offset_factor", frame=start_frame)
    fmod.offset_factor = 1.0
    fmod.keyframe_insert(data_path="offset_factor", frame=start_frame + 30)

    # Make keyframes LINEAR for constant speed
    if particle.animation_data and particle.animation_data.action:
        for fc in particle.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    # Hide outside its travel window
    particle.hide_render = True
    particle.keyframe_insert(data_path="hide_render", frame=1)
    particle.hide_render = False
    particle.keyframe_insert(data_path="hide_render", frame=start_frame)
    particle.hide_render = True
    particle.keyframe_insert(data_path="hide_render", frame=start_frame + 31)
```

## Output neuron brightening

After all particles are placed, keyframe the winning output neuron's emission:

```python
winner = neurons[3][a3.argmax()]   # class-0 neuron for the setosa sample
winner.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 0.0
winner.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].keyframe_insert(
    data_path='default_value', index=0, frame=70)
winner.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 8.0
winner.data.materials[0].node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].keyframe_insert(
    data_path='default_value', index=0, frame=100)
```

## Verification

At frame 50 (mid Hidden1→Hidden2 travel), press `Space` in viewport — you should see spheres moving along the synapse curves between Hidden 1 and Hidden 2.

## Cross-links

- [concepts/signal-propagation.md](../concepts/signal-propagation.md) — design rationale
- [blender-api/follow-path.md](../blender-api/follow-path.md) — constraint API
- [stages/05-render.md](./05-render.md) — next: camera, lighting, render
- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — original bugs fixed here
