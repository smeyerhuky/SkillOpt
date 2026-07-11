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

### Single-process (simple)

```bash
blender --background \
        --python scripts/blender_nn_render.py \
        -a
```

Blender's `-a` flag renders the frame range set in the scene (`frame_start`=1, `frame_end`=120). Use `-s <N>` and `-e <N>` to override start/end without editing the script.

### Parallel render (CPU — recommended for 4+ core machines)

On a CPU-only machine, running one Blender instance per core with `--threads 1` gives a ~3–4× wall-clock speedup over the default single-process render. Each instance writes to a non-overlapping frame range, so there are no race conditions.

**Split the 120 frames into N chunks equal to the core count:**

```bash
# 4-core example — renders frames 1–120 in ~4 parallel batches
N=4
TOTAL=120
CHUNK=$(( (TOTAL + N - 1) / N ))   # ceil(120/4) = 30

for i in $(seq 0 $((N-1))); do
  START=$(( i * CHUNK + 1 ))
  END=$(( (i + 1) * CHUNK ))
  [ $END -gt $TOTAL ] && END=$TOTAL
  nohup blender --background --threads 1 \
        --python scripts/blender_nn_render.py \
        -s $START -e $END -a \
        > /tmp/bl_worker_${i}.log 2>&1 &
  echo "Worker $i: frames $START–$END (PID $!)"
done
wait
echo "All workers done."
```

**Why `--threads 1`:** Cycles uses all available threads for a single frame by default. Four 4-thread instances compete for the same 4 cores with high synchronisation overhead. Four 1-thread instances each own one core — the same total CPU but without lock contention, giving ~3× real-world speedup on a 4-core machine.

**Resume from a partially-completed render:** the `-s`/`-e` flags override the scene's frame range, so you can resume individual workers mid-batch without re-rendering already-saved frames.

```bash
# Resume only missing range (e.g. frames 79–120 after a crash)
nohup blender --background --threads 1 \
      --python scripts/blender_nn_render.py \
      -s 79 -e 120 -a > /tmp/bl_resume.log 2>&1 &
```

## FFmpeg assembly

```bash
ffmpeg -framerate 24 \
       -i render/frame_%04d.png \
       -c:v libx264 -pix_fmt yuv420p \
       -crf 18 \
       output/nn_animation.mp4
```

`-crf 18` is visually lossless for this content. Final file is typically 5–15 MB for 120 frames. Run only after all parallel workers have exited (`wait` in the script above covers this).

## Render time estimates (Cycles, 16 samples + denoising)

| Mode | Cores used | Per-frame | Total (120f) |
|---|---|---|---|
| Single process, default threads | 4 | ~17s | ~34 min |
| 4 parallel workers, `--threads 1` | 4 (1 each) | ~24s/worker | **~10 min** |
| Single process, default threads | 8 | ~10s | ~20 min |
| 4 parallel workers, `--threads 2` | 8 (2 each) | ~13s/worker | **~6 min** |

At 64 samples (final quality), multiply per-frame times by ~4. Add GPU (`--cycles-device CUDA` or `OPTIX`) to drop to seconds per frame.

For headless CI renders without GPU, 16 samples + denoising is clean enough to review animation logic; use the parallel recipe to keep total time under 10 minutes on a 4-core runner.

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
