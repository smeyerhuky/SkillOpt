---
type: "Concept"
title: "Network Architecture — [4, 6, 5, 3] Iris Classifier"
description: "The four-layer feedforward network used as the visualization subject, mapping Iris flower measurements to species labels."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py"
tags: ["neural-network", "architecture", "iris", "classifier", "layer-sizes"]
timestamp: "2026-07-11"
---

# Network Architecture — [4, 6, 5, 3] Iris Classifier

The script hard-codes `layer_sizes = [4, 6, 5, 3]`. This maps exactly onto the **Iris flower dataset** (Fisher, 1936):

| Layer | Size | Role | Meaning |
|---|---|---|---|
| Input | 4 | Features | sepal length, sepal width, petal length, petal width |
| Hidden 1 | 6 | Representation | non-linear feature mixing |
| Hidden 2 | 5 | Compression | bottleneck toward decision |
| Output | 3 | Classes | *Iris setosa*, *I. versicolor*, *I. virginica* |

## Why Iris fits perfectly

The [4, 6, 5, 3] shape is not a coincidence for "number classifier" purposes — it classifies *numbers* in the sense that each output neuron fires for class index 0, 1, or 2. Iris is the canonical shallow-network benchmark with 4 real-valued inputs and 3 mutually exclusive classes, making it ideal for a visualization that needs **real, interpretable weight patterns** rather than random noise.

## Synapse count

Total synapses rendered = (4×6) + (6×5) + (5×3) = 24 + 30 + 15 = **69 Bezier curves**. At default `layer_spacing = 4.0` and `neuron_spacing = 2.0` the scene spans 12 Blender units in X and 10 units in Y (for the widest layer of 6 neurons).

## Activation function

The visualization uses ReLU activations for hidden layers and softmax for the output. These are not directly rendered in the base script but inform how neuron brightness should be mapped in an extended version — see [weight-encoding.md](./weight-encoding.md) and [signal-propagation.md](./signal-propagation.md).

## Cross-links

- [stages/02-data.md](../stages/02-data.md) — how to train this network and extract real weights
- [concepts/synapse-as-curve.md](./synapse-as-curve.md) — how the 69 synapses are rendered
- [script-reference/improved-script.md](../script-reference/improved-script.md) — full script with real weights embedded
