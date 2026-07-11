---
type: "API Reference"
title: "Bezier Curve Construction"
description: "Blender Python API for creating 3D Bezier curves with bevel depth, used to render synapses."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#create_synapse"
tags: ["blender", "bpy", "curve", "bezier", "bevel", "spline"]
timestamp: "2026-07-11"
---

# Bezier Curve Construction

## Creating the curve data block

```python
curve_data = bpy.data.curves.new(name, type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 2   # subdivisions along the curve length
```

`resolution_u = 2` keeps geometry low while still producing smooth motion for particles.

## Adding a Bezier spline

```python
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(1)   # starts with 1 point; add(1) gives 2 total
```

## Setting control point positions

```python
p0 = spline.bezier_points[0]
p0.co           = start_pos   # world position (Vector or tuple)
p0.handle_left  = start_pos
p0.handle_right = start_pos

p1 = spline.bezier_points[1]
p1.co           = end_pos
p1.handle_left  = end_pos
p1.handle_right = end_pos
```

Setting handles equal to `co` produces a **straight line** (free handles at zero offset). For S-curves, offset the handles along X:

```python
offset = Vector((layer_spacing * 0.4, 0, 0))
p0.handle_right = start_pos + offset
p1.handle_left  = end_pos  - offset
```

## Tube rendering via bevel

```python
curve_data.bevel_depth      = abs(weight) * 0.02
curve_data.bevel_resolution = 2   # 8-sided tube (2^(n+1) sides)
```

`bevel_depth` is the tube radius. `bevel_resolution = 0` gives a 4-sided tube; 2 gives 8 sides (adequate for most shots).

## Linking curve to scene

```python
curve_obj = bpy.data.objects.new(name, curve_data)
bpy.context.scene.collection.objects.link(curve_obj)
```

Note: synapses are linked to the **root scene collection**, not to a layer sub-collection. Moving them into per-connection collections would allow toggling individual layers' synapses but adds complexity.

## Cross-links

- [concepts/synapse-as-curve.md](../concepts/synapse-as-curve.md) — why curves, not cylinders
- [blender-api/follow-path.md](./follow-path.md) — FOLLOW_PATH targets this curve object
