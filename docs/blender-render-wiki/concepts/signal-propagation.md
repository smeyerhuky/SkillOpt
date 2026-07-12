---
type: "Concept"
title: "Signal Propagation Animation"
description: "How direct location keyframes with scale-based visibility simulate neural signal flow along synapses, replacing the unreliable FOLLOW_PATH approach."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#PHASE-3"
tags: ["animation", "location-keyframe", "scale-visibility", "signal", "particle", "blender-4.2"]
timestamp: "2026-07-11"
---

# Signal Propagation Animation

## The mechanism (corrected implementation)

Each signal is an icosphere (radius 0.15, emission strength 10.0, warm yellow color) that travels from the pre-synaptic neuron's world position to the post-synaptic neuron's position over `SIGNAL_FRAMES = 30` frames. Visibility is controlled via `scale` keyframes (the `hide_render` approach is broken in Blender 4.2 — see below).

```python
def add_signal_particle(synapse_obj, start_pos, end_pos, start_frame):
    from mathutils import Vector
    s = Vector(start_pos)
    e = Vector(end_pos)

    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15, location=s)
    p = bpy.context.active_object

    # Yellow emission material
    mat = bpy.data.materials.new(f"Mat_{p.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Emission Color'].default_value    = (1.0, 0.85, 0.15, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 10.0
    p.data.materials.append(mat)

    end_frame = start_frame + SIGNAL_FRAMES

    # Direct location keyframes — reliable across all Blender versions
    p.location = s
    p.keyframe_insert(data_path="location", frame=start_frame)
    p.location = e
    p.keyframe_insert(data_path="location", frame=end_frame)

    # Visibility via scale — hide_render boolean keyframes silently fail in Blender 4.2
    p.scale = (0.0, 0.0, 0.0)
    p.keyframe_insert(data_path="scale", frame=max(1, start_frame - 1))
    p.scale = (1.0, 1.0, 1.0)
    p.keyframe_insert(data_path="scale", frame=start_frame)
    p.scale = (0.0, 0.0, 0.0)
    p.keyframe_insert(data_path="scale", frame=end_frame + 1)

    # LINEAR interpolation for constant-speed travel
    if p.animation_data and p.animation_data.action:
        for fc in p.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
```

## Why not FOLLOW_PATH?

The original design used a `FOLLOW_PATH` constraint with an animated `offset_factor` to send particles along the Bezier synapse curves. This approach has two fatal problems in Blender 4.2 headless render:

1. **`hide_render` keyframes silently fail** (Bug 5) — particles are permanently hidden regardless of keyframes.
2. **`offset_factor` constraint keyframes don't evaluate correctly in headless mode** (Bug 6) — particles freeze at their default position.

The direct `location` keyframe approach loses the curved path (particles travel in straight lines between neuron positions rather than along the Bezier synapse), but it works reliably in all Blender versions including 4.2 headless, which is the execution environment for this pipeline. At the camera distance used (−18 units in Y), the straight-line travel is visually acceptable.

## Timing strategy for layered propagation

`layer_starts` staggers each wave so propagation appears left-to-right:

| Layer transition | Start frame | End frame | Gap before |
|---|---|---|---|
| L0 → L1 | 1 | 31 | — |
| L1 → L2 | 35 | 65 | 4 frames |
| L2 → L3 | 70 | 100 | 5 frames |

Winner output neuron brightens from frame 70 to 100 (overlapping the final wave). Total animation: 120 frames at 24 fps = 5.0 seconds.

## Activation-driven gating

Only pre-synaptic neurons with activation > `ACTIVATION_THRESHOLD = 0.05` spawn signal particles. The input layer always fires (`acts[0] = np.ones(4)`). Hidden layers use the trained forward-pass values, so only actually-active pathways are visualised. This makes the forward pass legible.

## Cross-links

- [stages/04-animate.md](../stages/04-animate.md) — PDLC stage for the full animation setup
- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — Bugs 5 & 6 (hide_render + FOLLOW_PATH failures)
- [blender-api/follow-path.md](../blender-api/follow-path.md) — FOLLOW_PATH API (not used in corrected script)
