---
type: "Script Reference"
title: "Improved Blender Script"
description: "The corrected and extended blender_nn_render.py with real Iris weights, unique materials, working signal particles, camera, and lighting."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["blender", "python", "script", "improved", "complete", "animation"]
timestamp: "2026-07-11"
---

# Improved Blender Script

This is the complete corrected version of the original script. Save as `scripts/blender_nn_render.py` and run after `scripts/train_iris_classifier.py` has produced `scripts/nn_weights.npz`.

All four bugs from [known-bugs.md](./known-bugs.md) are fixed. Real trained weights are loaded. Signal particles are created. Camera and lighting are added.

```python
"""
blender_nn_render.py — Iris Classifier Neural Network Visualization
Run: blender --background --python scripts/blender_nn_render.py --render-anim
Prerequisite: python3 scripts/train_iris_classifier.py  (produces nn_weights.npz)
"""
import bpy
import math
import numpy as np
from pathlib import Path

# ── Load real trained weights ─────────────────────────────────────────────────
weights_path = Path(__file__).parent / "nn_weights.npz"
data  = np.load(weights_path, )
W     = [data['W1'], data['W2'], data['W3']]     # weight matrices
acts  = [np.ones(4), data['a1'], data['a2'], data['a3']]  # per-layer activations

# ── Configuration ─────────────────────────────────────────────────────────────
layer_sizes    = [4, 6, 5, 3]
layer_spacing  = 4.0
neuron_spacing = 2.0
SIGNAL_FRAMES  = 30          # frames for one layer traversal
LAYER_GAPS     = 4           # frames between layers
layer_starts   = [1, 1 + SIGNAL_FRAMES + LAYER_GAPS,
                  1 + 2*(SIGNAL_FRAMES + LAYER_GAPS)]   # [1, 35, 70]

# ── Clear scene ───────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── PHASE 1: Neurons (icospheres with emission) ───────────────────────────────
neurons    = []
collections = []

for i, size in enumerate(layer_sizes):
    col = bpy.data.collections.new(f"Layer_{i}")
    bpy.context.scene.collection.children.link(col)
    collections.append(col)

    total_h = (size - 1) * neuron_spacing
    start_y = -total_h / 2
    layer_neurons = []

    for j in range(size):
        x = i * layer_spacing
        y = start_y + j * neuron_spacing

        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.4, location=(x, y, 0))
        neuron = bpy.context.active_object
        neuron.name = f"L{i}_N{j}"

        # Material with emission driven by activation
        mat = bpy.data.materials.new(f"Neuron_L{i}_N{j}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value  = (0.9, 0.9, 0.95, 1.0)
        bsdf.inputs['Roughness'].default_value   = 0.3
        activation = float(acts[i][j]) if i < len(acts) and j < len(acts[i]) else 1.0
        bsdf.inputs['Emission Color'].default_value    = (0.4, 0.7, 1.0, 1.0)
        bsdf.inputs['Emission Strength'].default_value = activation * 4.0
        neuron.data.materials.append(mat)

        col.objects.link(neuron)
        try:
            bpy.context.scene.collection.objects.unlink(neuron)
        except RuntimeError:
            pass
        layer_neurons.append(neuron)

    neurons.append(layer_neurons)

# ── PHASE 2: Synapses (Bezier curves, unique materials, real weights) ─────────
synapses = []   # synapses[layer][pre][post] = curve_obj

def create_synapse(name, start_pos, end_pos, weight):
    from mathutils import Vector
    s = Vector(start_pos)
    e = Vector(end_pos)
    offset = Vector((layer_spacing * 0.35, 0, 0))

    curve_data             = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions  = '3D'
    curve_data.resolution_u = 4

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)

    p0 = spline.bezier_points[0]
    p0.co           = s
    p0.handle_left  = s
    p0.handle_right = s + offset

    p1 = spline.bezier_points[1]
    p1.co           = e
    p1.handle_left  = e - offset
    p1.handle_right = e

    # BUG FIX 1: unique material per synapse
    mat = bpy.data.materials.new(f"Mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Roughness'].default_value = 0.4
    if weight > 0:
        bsdf.inputs['Base Color'].default_value = (0.0, 0.85, 0.25, 1.0)
    else:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.1, 0.1, 1.0)

    curve_data.bevel_depth      = min(abs(weight), 2.0) * 0.012
    curve_data.bevel_resolution = 3
    curve_data.materials.append(mat)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.scene.collection.objects.link(obj)
    return obj

for i in range(len(neurons) - 1):
    layer_syn = []
    for j, n_a in enumerate(neurons[i]):
        row_syn = []
        for k, n_b in enumerate(neurons[i+1]):
            weight  = float(W[i][j, k])
            syn_obj = create_synapse(
                f"Syn_L{i}_{j}_L{i+1}_{k}",
                n_a.location, n_b.location, weight
            )
            row_syn.append(syn_obj)
        layer_syn.append(row_syn)
    synapses.append(layer_syn)

# ── PHASE 3: Signal particles (BUG FIX 3: actually called) ───────────────────
ACTIVATION_THRESHOLD = 0.05

def add_signal_particle(synapse_obj, start_frame):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12, location=(0, 0, 0))
    p = bpy.context.active_object
    p.name     = f"Signal_{synapse_obj.name}"
    p.location = (0, 0, 0)

    mat = bpy.data.materials.new(f"Mat_{p.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Emission Color'].default_value    = (1.0, 0.9, 0.3, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 6.0
    p.data.materials.append(mat)

    # BUG FIX 2: no FOLLOW_TRACK — only FOLLOW_PATH
    fmod                    = p.constraints.new(type='FOLLOW_PATH')
    fmod.target             = synapse_obj
    fmod.use_curve_follow   = True
    fmod.use_fixed_location = True
    fmod.forward_axis       = 'TRACK_NEGATIVE_Y'
    fmod.up_axis            = 'UP_Y'

    fmod.offset_factor = 0.0
    fmod.keyframe_insert(data_path="offset_factor", frame=start_frame)
    fmod.offset_factor = 1.0
    fmod.keyframe_insert(data_path="offset_factor", frame=start_frame + SIGNAL_FRAMES)

    # Linear interpolation for constant speed
    if p.animation_data and p.animation_data.action:
        for fc in p.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    # Visibility keyframes
    p.hide_render = True
    p.keyframe_insert(data_path="hide_render", frame=1)
    p.hide_render = False
    p.keyframe_insert(data_path="hide_render", frame=start_frame)
    p.hide_render = True
    p.keyframe_insert(data_path="hide_render", frame=start_frame + SIGNAL_FRAMES + 1)

for i in range(len(neurons) - 1):
    for j, n_a in enumerate(neurons[i]):
        if acts[i][j] < ACTIVATION_THRESHOLD:
            continue
        for k in range(len(neurons[i+1])):
            add_signal_particle(synapses[i][j][k], layer_starts[i])

# ── PHASE 4: Winner neuron brightening ────────────────────────────────────────
winner_idx = int(acts[3].argmax())
winner     = neurons[3][winner_idx]
bsdf_w     = winner.data.materials[0].node_tree.nodes["Principled BSDF"]
es_input   = bsdf_w.inputs['Emission Strength']

es_input.default_value = 0.0
es_input.keyframe_insert(data_path='default_value', index=0, frame=70)
es_input.default_value = 10.0
es_input.keyframe_insert(data_path='default_value', index=0, frame=100)

# ── PHASE 5: Camera and lighting ──────────────────────────────────────────────
bpy.ops.object.camera_add(location=(6, -18, 5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam
cam.data.lens = 50

bpy.ops.object.light_add(type='AREA', location=(-4, -12, 14))
key = bpy.context.active_object
key.data.energy = 600
key.data.color  = (1.0, 0.95, 0.8)
key.data.size   = 10
key.rotation_euler = (math.radians(45), 0, math.radians(-30))

bpy.ops.object.light_add(type='SPOT', location=(15, 8, 6))
rim = bpy.context.active_object
rim.data.energy = 300
rim.data.color  = (0.6, 0.8, 1.0)
rim.data.spot_size = math.radians(60)

# Black background
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.0

# ── Render settings ───────────────────────────────────────────────────────────
scene                = bpy.context.scene
scene.frame_start    = 1
scene.frame_end      = 120
scene.render.fps     = 24
scene.render.engine  = 'CYCLES'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '//render/frame_'

print(f"Scene complete. Winner class: {winner_idx} (softmax: {acts[3].round(3)})")
print("Neural Network Visualization Ready.")
```

## Cross-links

- [script-reference/known-bugs.md](./known-bugs.md) — the four bugs this fixes
- [stages/02-data.md](../stages/02-data.md) — produces nn_weights.npz
- [stages/04-animate.md](../stages/04-animate.md) — animation design
- [stages/05-render.md](../stages/05-render.md) — render execution
