---
type: "Concept"
title: "Signal Propagation Animation"
description: "How FOLLOW_PATH constraints with animated offset_factor simulate neural signal flow along synapses."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#PHASE-3"
tags: ["animation", "follow-path", "constraint", "signal", "particle", "keyframe"]
timestamp: "2026-07-11"
---

# Signal Propagation Animation

## The mechanism

Each signal is an icosphere (radius 0.15) with a `FOLLOW_PATH` constraint targeting a synapse curve. The constraint's `offset_factor` is keyframed from 0.0 to 1.0 over 30 frames, causing the sphere to travel from the pre-synaptic neuron to the post-synaptic neuron.

```python
fmod = particle.constraints.new(type='FOLLOW_PATH')
fmod.target    = synapse_obj
fmod.use_curve_follow = True
fmod.use_fixed_location = True
fmod.forward_axis = 'TRACK_NEGATIVE_Y'
fmod.up_axis = 'UP_Y'

fmod.offset_factor = 0.0
fmod.keyframe_insert(data_path="offset_factor", frame=start_frame)
fmod.offset_factor = 1.0
fmod.keyframe_insert(data_path="offset_factor", frame=start_frame + 30)
```

## Timing strategy for layered propagation

To show layer-by-layer forward propagation, stagger `start_frame` by layer:

| Layer transition | Start frame | End frame |
|---|---|---|
| L0 → L1 | 1 | 31 |
| L1 → L2 | 35 | 65 |
| L2 → L3 | 70 | 100 |

This gives 4-frame gaps between layers for visual clarity. Total animation: ~100 frames at 24 fps = ~4.2 seconds.

## Known bug: FOLLOW_TRACK stub

The original script adds a `FOLLOW_TRACK` constraint immediately before adding `FOLLOW_PATH`. The `FOLLOW_TRACK` constraint has no target and is never removed — it silently coexists with `FOLLOW_PATH`. In practice `FOLLOW_PATH` takes precedence but the orphaned constraint wastes memory and causes warnings. The fix: remove the `FOLLOW_TRACK` line entirely. See [script-reference/known-bugs.md](../script-reference/known-bugs.md).

## Phase 3 stub

The original script's Phase 3 loop ends with `pass` — the `add_signal_particle` function is defined but never called in the connection loop. The improved script calls it for every synapse with the correct stagger. See [script-reference/improved-script.md](../script-reference/improved-script.md).

## Activation-driven gating

In the improved script, only synapses where the pre-synaptic activation > 0.1 actually spawn a particle — visually suppressing signals along silent pathways and making the forward pass legible for a specific sample input.

## Cross-links

- [blender-api/follow-path.md](../blender-api/follow-path.md) — FOLLOW_PATH API details
- [stages/04-animate.md](../stages/04-animate.md) — PDLC stage for the full animation setup
- [script-reference/known-bugs.md](../script-reference/known-bugs.md) — FOLLOW_TRACK bug
