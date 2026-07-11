---
type: "API Reference"
title: "Materials and Node Trees"
description: "Blender Python API for creating Principled BSDF materials and setting node inputs programmatically."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#create_synapse"
tags: ["blender", "bpy", "material", "nodes", "principled-bsdf", "emission", "color"]
timestamp: "2026-07-11"
---

# Materials and Node Trees

## Creating a material

```python
mat = bpy.data.materials.new("Synapse_Positive")
mat.use_nodes = True
```

`use_nodes = True` is required to access the node tree. The default node tree contains a **Principled BSDF** connected to a **Material Output**.

## Accessing Principled BSDF inputs

```python
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.0, 0.8, 0.2, 1.0)  # RGBA
bsdf.inputs['Roughness'].default_value  = 0.5
```

Inputs are accessed by display name. The full list for Principled BSDF includes: `'Base Color'`, `'Metallic'`, `'Roughness'`, `'IOR'`, `'Alpha'`, `'Emission Color'`, `'Emission Strength'`, etc.

## Adding emission (glow effect)

```python
bsdf.inputs['Emission Color'].default_value    = (0.0, 0.8, 0.2, 1.0)
bsdf.inputs['Emission Strength'].default_value = activation_value * 3.0
```

Used in the improved script to make activated neurons glow in proportion to their ReLU output. Emission Strength of 0 = dark, 3.0 = bright bloom (requires Bloom post-processing or Cycles emission).

## Linking material to object

```python
curve_data.materials.append(mat)
```

For a curve, materials are appended to the curve data block (not the curve object). For mesh objects: `obj.data.materials.append(mat)`.

## Per-synapse unique materials (fix)

The original script reuses one `"Synapse_Mat"` material instance for all 69 synapses, meaning all end up the same color. The fix:

```python
mat_name = f"Mat_L{layer_a}_to_L{layer_b}_{na_idx}_{nb_idx}"
mat = bpy.data.materials.new(mat_name)
mat.use_nodes = True
# ... set color and roughness ...
curve_data.materials.append(mat)
```

This creates 69 independent materials — GPU memory cost is negligible for 69 simple Principled BSDF shaders.

## Cross-links

- [concepts/weight-encoding.md](../concepts/weight-encoding.md) — what colors mean
- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — material sharing bug
