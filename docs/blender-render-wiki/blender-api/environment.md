---
type: "API Reference"
title: "Blender Environment Reference"
description: "Version, Python runtime, color management, render engine, material API, and headless execution details for the neural network render pipeline."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["blender-4.2", "cycles", "color-management", "agx", "principled-bsdf", "headless", "python-3.11", "environment"]
timestamp: "2026-07-12"
---

# Blender Environment Reference

All details confirmed against the working render of `demo/nn_animation.mp4` (120 frames, 1920×1080, 5 s @ 24 fps).

---

## Version

| Property | Value |
|---|---|
| Blender version | **4.2** |
| Bundled Python | **3.11** |
| NumPy | Bundled with Blender 4.2 — no separate install needed |
| mathutils | Built-in Blender module — available inside `--background` sessions |

Bugs 5 & 6 in `script-reference/known-bugs.md` are confirmed regressions in Blender 4.2 specifically. The fixes (`scale` keyframes, direct `location` keyframes) are forward-compatible and safe on any Blender version.

---

## Color management

The script does **not** set color management explicitly, so Blender 4.2 defaults apply.

| Setting | Blender 4.2 default | bpy path |
|---|---|---|
| View transform | **AgX** | `scene.view_settings.view_transform` |
| Look | None | `scene.view_settings.look` |
| Exposure | 0.0 | `scene.view_settings.exposure` |
| Gamma | 1.0 | `scene.view_settings.gamma` |
| Display device | sRGB | `scene.display_settings.display_device` |
| PNG output space | sRGB (baked in by renderer) | `scene.render.image_settings.color_mode = 'RGB'` |

**AgX vs Filmic**: Blender 4.0 switched the default view transform from Filmic to AgX. AgX has a different tone curve — it handles high-emission values differently. At `Emission Strength = 10.0` (signal particles) and `Emission Strength = 4.0` (neurons), AgX clips highlights to warm-white rather than the strong-blue bloom Filmic produces. This is why pixel analysis shows "warm-bright" (RGB ~236,230,198) rather than saturated yellow — the emission is over-range for the tone mapper.

To override and use Filmic (Blender 3.x behaviour):
```python
scene.view_settings.view_transform = 'Filmic'
```

To override and see raw linear output (no tonemapping — useful for debugging emission values):
```python
scene.view_settings.view_transform = 'Raw'
```

---

## Render engine

```python
scene.render.engine = 'CYCLES'
```

| Setting | Value | bpy path |
|---|---|---|
| Engine | Cycles (CPU path tracer) | `scene.render.engine` |
| Device | CPU (default; no GPU flag set) | `scene.cycles.device` |
| Samples | **16** | `scene.cycles.samples` |
| Denoiser | **OIDN** (Intel Open Image Denoise, CPU default) | `scene.cycles.denoiser` |
| Denoising enabled | True | `scene.cycles.use_denoising` |
| Resolution | 1920 × 1080 | `scene.render.resolution_x/y` |
| Resolution % | 100 | `scene.render.resolution_percentage` |
| FPS | 24 | `scene.render.fps` |
| Frame range | 1 – 120 | `scene.frame_start / frame_end` |
| Output format | PNG | `scene.render.image_settings.file_format` |
| Output path | `render/frame_` (absolute, from script path) | `scene.render.filepath` |

**Sample count rationale**: 16 samples with OIDN denoising is sufficient for animation review — noise is cleaned up by the denoiser and the scene has strong emission which self-illuminates. For a final presentation render use 64–128 samples; multiply per-frame time by 4–8×.

**GPU acceleration**: add `--cycles-device CUDA` (NVIDIA) or `OPTIX` to the Blender CLI flags, and set `scene.cycles.device = 'GPU'` in the script. This reduces per-frame time from ~25 s to ~1–3 s on a modern GPU.

---

## World / background

```python
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)  # pure black
world.node_tree.nodes["Background"].inputs[1].default_value = 0.0            # zero strength
```

Pure black background with zero environment strength. This makes emissive objects read as luminous against void, which is the visual intent. If HDRI lighting is added later, it will compete with the emission — keep strength ≤ 0.05 to preserve the dark aesthetic.

---

## Material system — Principled BSDF in 4.2

Blender 4.x restructured the Principled BSDF node inputs. Several input names changed from 3.x. The table below shows the names **as used in this script** (confirmed working in 4.2):

| Input name (4.2) | Old name (3.x) | Used for |
|---|---|---|
| `'Base Color'` | `'Base Color'` | Neuron diffuse color, synapse tube color |
| `'Roughness'` | `'Roughness'` | Surface finish (neurons 0.3, synapses 0.4) |
| `'Emission Color'` | `'Emission'` | **Changed in 4.x** — emission tint color |
| `'Emission Strength'` | `'Emission Strength'` | Emission intensity (neurons 0–4, particles 10.0) |

**Critical**: In Blender 3.x the emission input was a single `'Emission'` RGBA socket. In 4.x it was split into `'Emission Color'` (RGBA) and `'Emission Strength'` (float). Using the old `'Emission'` name in 4.2 raises a `KeyError` silently or sets the wrong socket.

### Keyframeable node inputs

Node input `default_value` fields **can** be keyframed in Blender 4.2:

```python
# This works correctly in 4.2 (winner neuron brightening):
es = bsdf.inputs['Emission Strength']
es.default_value = 0.0
es.keyframe_insert(data_path='default_value', frame=70)
es.default_value = 10.0
es.keyframe_insert(data_path='default_value', frame=100)
```

Note: `bsdf.inputs[...]` is on the node, so the fcurve path is `node_tree.nodes["Principled BSDF"].inputs[7].default_value` internally. The `keyframe_insert` with `data_path='default_value'` handles this correctly. Only **object-level boolean properties** like `hide_render` are broken (Bug 5).

---

## Geometry primitives

| Primitive | Function | Key params used |
|---|---|---|
| Icosphere (neurons) | `bpy.ops.mesh.primitive_ico_sphere_add` | `radius=0.4, location=(x,y,0)` |
| Icosphere (signal particles) | `bpy.ops.mesh.primitive_ico_sphere_add` | `radius=0.15, location=s` |
| Bezier curve (synapses) | `bpy.data.curves.new(name, type='CURVE')` | `bevel_depth`, `bevel_resolution=3` |

After any `bpy.ops` call, the created object is available as `bpy.context.active_object`. This is relied upon throughout the script — avoid interleaving ops calls with context switches.

---

## Camera

```python
bpy.ops.object.camera_add(location=(6, -18, 5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam
cam.data.lens = 50   # mm — ~natural perspective
```

| Property | Value | Notes |
|---|---|---|
| Location | (6, −18, 5) | X=6 centres on 4-layer network (spans x=0 to x=12); Y=−18 pulls back; Z=5 slight elevation |
| Rotation X | 75° | Tilts down to frame the flat-Z scene |
| Rotation Y, Z | 0° | No roll or yaw |
| Type | PERSP (default) | Perspective projection |
| Focal length | 50 mm | Equivalent to a "normal" lens — minimal distortion |

---

## Lighting

```python
# Key light — warm, area, upper-left
bpy.ops.object.light_add(type='AREA', location=(-4, -12, 14))
key.data.energy = 600           # watts
key.data.color  = (1.0, 0.95, 0.8)   # warm white
key.data.size   = 10            # large soft source
key.rotation_euler = (math.radians(45), 0, math.radians(-30))

# Rim light — cool, spot, behind network
bpy.ops.object.light_add(type='SPOT', location=(15, 8, 6))
rim.data.energy    = 300
rim.data.color     = (0.6, 0.8, 1.0)  # cool blue
rim.data.spot_size = math.radians(60)
```

| Light | Type | Energy | Color | Role |
|---|---|---|---|---|
| Key | AREA, size 10 | 600 W | (1.0, 0.95, 0.8) warm | Main illumination, soft shadows |
| Rim | SPOT, 60° cone | 300 W | (0.6, 0.8, 1.0) cool | Backlight separating network from void |

Lighting contribution is secondary to self-emission (neurons and particles glow intrinsically). The lights mainly catch the Bezier synapse tubes, which have no emission.

---

## Headless execution

```bash
blender --background --python scripts/blender_nn_render.py -a
```

| Flag | Effect |
|---|---|
| `--background` | No GUI — required for server/CI environments |
| `--python <file>` | Execute script after Blender initialises |
| `-a` | Render animation (frame_start → frame_end) |
| `-s <N>` | Override start frame (for parallel workers) |
| `-e <N>` | Override end frame (for parallel workers) |
| `--threads <N>` | Cycles thread count (use `1` per worker in parallel mode) |

**Python path note**: inside `--background`, `bpy`, `mathutils`, and `numpy` are available. The script's own directory is not automatically on `sys.path`, so all imports must either be from Blender builtins or installed into Blender's bundled Python. The script uses only `bpy`, `mathutils`, `math`, `sys`, `pathlib.Path`, and `numpy` — all present in a standard Blender 4.2 install.

---

## Cross-links

- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — Bugs 5 & 6: Blender 4.2 regressions in hide_render and FOLLOW_PATH
- [stages/05-render.md](../stages/05-render.md) — parallel render recipe, per-frame timing, FFmpeg assembly
- [blender-api/materials-nodes.md](./materials-nodes.md) — Principled BSDF setup in detail
- [blender-api/follow-path.md](./follow-path.md) — FOLLOW_PATH (not used in corrected script; retained for reference)
