---
type: "Concept"
title: "Synapse as Bezier Curve"
description: "How each weighted connection between neurons is rendered as a Bezier curve with bevel thickness proportional to |weight|."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#create_synapse"
tags: ["blender", "curve", "synapse", "bezier", "bevel", "weight"]
timestamp: "2026-07-11"
---

# Synapse as Bezier Curve

Each connection is a `CURVE` data block with one `BEZIER` spline. The two control points are placed at the source and target neuron world positions, with handles set to the same position as the point itself (making the curve a straight line by default — curved appearance requires moving handles).

```python
curve_data = bpy.data.curves.new(name, type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(1)        # total = 2 points
p0.co = start_pos
p0.handle_left = p0.handle_right = start_pos
p1.co = end_pos
p1.handle_left = p1.handle_right = end_pos
```

## Thickness encoding

`bevel_depth = abs(weight) * 0.02` — a weight of magnitude 1.0 produces a tube of radius 0.02 Blender units. `bevel_resolution = 2` keeps the polygon count low (8-sided tube).

## Color encoding

| Weight sign | Base Color (RGBA) |
|---|---|
| Positive | `(0, 0.8, 0.2, 1)` — green |
| Negative | `(0.8, 0.1, 0.1, 1)` — red |

## Known bug: shared material

The original script does `bpy.data.materials.get("Synapse_Mat")` and reuses the same material object for all synapses. Since all curves share one material, only the **last synapse's color** survives — every edge ends up the same color regardless of weight sign. The fix is to create a **unique material per curve**. See [script-reference/known-bugs.md](../script-reference/known-bugs.md) and the fix in [script-reference/improved-script.md](../script-reference/improved-script.md).

## Improved version: curved splines

In the improved script, handles are offset along the X axis by `layer_spacing * 0.4` to produce gentle S-curves, improving visual clarity when many synapses converge on a single neuron.

## Cross-links

- [concepts/weight-encoding.md](./weight-encoding.md) — full encoding scheme
- [blender-api/bezier-curves.md](../blender-api/bezier-curves.md) — Blender curve API details
- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — material sharing bug
