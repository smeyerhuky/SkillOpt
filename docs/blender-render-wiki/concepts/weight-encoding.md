---
type: "Concept"
title: "Weight Encoding — Color and Thickness"
description: "The visual language mapping neural network weight sign and magnitude to curve color and bevel thickness."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#create_synapse"
tags: ["visualization", "weight", "color", "thickness", "encoding", "material"]
timestamp: "2026-07-11"
---

# Weight Encoding — Color and Thickness

The script encodes each synapse weight on two channels simultaneously:

## Channel 1: Hue (weight sign)

| Sign | Color | RGBA |
|---|---|---|
| w > 0 | Green (excitatory) | `(0.0, 0.8, 0.2, 1.0)` |
| w ≤ 0 | Red (inhibitory) | `(0.8, 0.1, 0.1, 1.0)` |

This maps to the biological convention: excitatory connections (positive weights amplify signals) are green; inhibitory connections (negative weights suppress signals) are red.

## Channel 2: Thickness (weight magnitude)

```
bevel_depth = |w| × 0.02
```

Range: weights are typically in `[-1, 1]` after training (or random init), giving tube radii of `[0, 0.02]`. A weight of magnitude 0.5 produces a radius of 0.01 Blender units.

For real Iris-trained weights, magnitudes after Xavier initialization and gradient descent often fall in `[-2, 2]` — rescale with `bevel_depth = min(abs(weight), 2.0) * 0.01` to keep visible tubes.

## Principled BSDF setup

The material uses the default Principled BSDF node with:
- `Roughness = 0.5` (semi-matte)
- `Base Color` set per the sign encoding above
- No emission, no metallic (keeps render times low)

For a glow effect on high-magnitude weights, add a **Emission** socket contribution proportional to `|w|` — documented in [blender-api/materials-nodes.md](../blender-api/materials-nodes.md).

## Extended encoding (improved script)

The improved script adds a third channel: **neuron emission** driven by the activation value for a sample forward pass. Output neurons for the winning class glow brightest, making the classification decision visible without text labels. See [concepts/signal-propagation.md](./signal-propagation.md).

## Cross-links

- [concepts/synapse-as-curve.md](./synapse-as-curve.md) — where thickness/color are applied
- [stages/02-data.md](../stages/02-data.md) — real weight values that drive the encoding
- [blender-api/materials-nodes.md](../blender-api/materials-nodes.md) — node tree API
