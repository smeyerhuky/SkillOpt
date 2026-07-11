---
type: "PDLC Stage"
title: "Stage 5 — Render"
description: "Camera placement, lighting, render settings, and headless execution to produce the final MP4 animation."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["pdlc", "render", "camera", "lighting", "cycles", "headless", "ffmpeg", "mp4"]
timestamp: "2026-07-11"
---

# Stage 5 — Render

## Camera setup

```python
bpy.ops.object.camera_add(location=(6, -18, 5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam

# Orthographic for cleaner neural net look (optional)
cam.data.type       = 'PERSP'
cam.data.lens       = 50          # mm focal length
cam.data.clip_end   = 1000
```

The camera is placed at `(6, -18, 5)` — centred on the network's X midpoint (layer 0 at x=0, layer 3 at x=12, midpoint x=6), pulled 18 units back in Y, and slightly elevated. The 75° X-rotation tilts it down to frame the scene.

## Lighting

```python
# Key light — warm, from upper-left
bpy.ops.object.light_add(type='AREA', location=(-5, -10, 15))
key = bpy.context.active_object
key.data.energy = 500
key.data.color  = (1.0, 0.95, 0.8)
key.data.size   = 8

# Rim light — cool, from behind network
bpy.ops.object.light_add(type='SPOT', location=(15, 10, 8))
rim = bpy.context.active_object
rim.data.energy = 200
rim.data.color  = (0.6, 0.8, 1.0)
```

Keep the background pure black (`bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,1)`) so signal spheres and glowing neurons read as luminous against void.

## Render settings

```python
scene = bpy.context.scene
scene.render.engine            = 'CYCLES'
scene.render.resolution_x      = 1920
scene.render.resolution_y      = 1080
scene.render.fps               = 24
scene.cycles.samples           = 64      # 128 for final; 32 for preview
scene.cycles.use_denoising     = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath          = '//render/frame_'
```

## Headless render command

```bash
blender --background \
        --python scripts/blender_nn_render.py \
        --render-anim \
        -- --output /tmp/nn_render/frame_ --start 1 --end 120
```

The `--` separates Blender flags from script arguments. The script reads `sys.argv` after `--` to allow output path overrides without editing the script.

## FFmpeg assembly

```bash
ffmpeg -framerate 24 \
       -i /tmp/nn_render/frame_%04d.png \
       -c:v libx264 -pix_fmt yuv420p \
       -crf 18 \
       output/nn_animation.mp4
```

`-crf 18` is visually lossless for this type of content. Final file is typically 5–15 MB for 120 frames.

## Render time estimates (Cycles)

| Samples | Resolution | Hardware | Per-frame | Total (120f) |
|---|---|---|---|---|
| 32 | 1080p | CPU (8-core) | ~45s | ~90 min |
| 64 | 1080p | CPU (8-core) | ~90s | ~3 hr |
| 64 | 1080p | RTX 3080 | ~4s | ~8 min |
| 128 | 1080p | RTX 3080 | ~8s | ~16 min |

For headless CI renders without GPU, use 32 samples with denoising — the result is clean enough to review the animation logic.

## Bloom post-processing (optional)

Enable in Compositor nodes to make high-emission neurons glow:

```python
scene.eevee.use_bloom       = True    # EEVEE only; for Cycles use compositor
scene.eevee.bloom_threshold = 0.8
scene.eevee.bloom_intensity = 0.5
```

For Cycles, add a **Glare** node (type=Fog Glow, quality=High, threshold=0.8) in the Compositor.

## Cross-links

- [stages/01-design.md](./01-design.md) — render targets established in design stage
- [stages/04-animate.md](./04-animate.md) — animation that this stage renders
- [script-reference/improved-script.md](../script-reference/improved-script.md) — full script with camera/lighting code
