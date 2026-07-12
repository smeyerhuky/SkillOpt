---
type: "PDLC Stage"
title: "Stage 2 — Data: Training the Iris Classifier"
description: "Train a [4,6,5,3] network on Iris data using NumPy and extract weight arrays for embedding in the Blender script."
resource: "file:///home/user/SkillOpt/scripts/train_iris_classifier.py"
tags: ["pdlc", "data", "numpy", "iris", "training", "weights", "forward-pass"]
timestamp: "2026-07-11"
---

# Stage 2 — Data: Training the Iris Classifier

## Why real weights matter

Random weights produce a scene where synapse colors are noise — the visualization teaches nothing. Real trained weights have **structure**: feature-detector patterns in Hidden 1, class-separator patterns in Hidden 2, and winner-takes-all competition in the output. This structure is what makes the animation meaningful.

## Training script (NumPy, no ML framework)

Save as `scripts/train_iris_classifier.py` and run with `python3 scripts/train_iris_classifier.py`:

```python
import numpy as np

# ── Iris dataset (hard-coded; avoids sklearn dependency) ─────────────────────
# 150 samples, 4 features, class 0/1/2
# (abbreviated — full dataset in scripts/iris_data.py)
from scripts.iris_data import X_raw, y_raw   # shape (150,4), (150,)

# Normalise to zero mean, unit variance (per feature)
mu  = X_raw.mean(axis=0)
std = X_raw.std(axis=0)
X   = (X_raw - mu) / std

# One-hot encode targets
Y = np.eye(3)[y_raw]   # shape (150, 3)

# ── Weight initialisation (Xavier) ───────────────────────────────────────────
def xavier(fan_in, fan_out):
    limit = np.sqrt(6 / (fan_in + fan_out))
    return np.random.uniform(-limit, limit, (fan_in, fan_out))

np.random.seed(42)
W1 = xavier(4, 6);  b1 = np.zeros(6)
W2 = xavier(6, 5);  b2 = np.zeros(5)
W3 = xavier(5, 3);  b3 = np.zeros(3)

# ── Forward pass helpers ──────────────────────────────────────────────────────
def relu(x):     return np.maximum(0, x)
def softmax(x):  e = np.exp(x - x.max(axis=1, keepdims=True)); return e / e.sum(axis=1, keepdims=True)

def forward(X):
    a1 = relu(X  @ W1 + b1)
    a2 = relu(a1 @ W2 + b2)
    a3 = softmax(a2 @ W3 + b3)
    return a1, a2, a3

# ── Training loop (mini-batch SGD, 500 epochs) ───────────────────────────────
lr, epochs, batch = 0.05, 500, 16

for epoch in range(epochs):
    idx = np.random.permutation(150)
    for start in range(0, 150, batch):
        mb = idx[start:start+batch]
        Xb, Yb = X[mb], Y[mb]
        a1, a2, a3 = forward(Xb)

        # Cross-entropy gradient w.r.t. output pre-softmax
        d3 = (a3 - Yb) / len(mb)
        dW3 = a2.T @ d3;  db3 = d3.sum(0)

        d2 = (d3 @ W3.T) * (a2 > 0)
        dW2 = a1.T @ d2;  db2 = d2.sum(0)

        d1 = (d2 @ W2.T) * (a1 > 0)
        dW1 = Xb.T @ d1;  db1 = d1.sum(0)

        W1 -= lr*dW1; b1 -= lr*db1
        W2 -= lr*dW2; b2 -= lr*db2
        W3 -= lr*dW3; b3 -= lr*db3

# ── Evaluation ───────────────────────────────────────────────────────────────
_, _, preds = forward(X)
acc = (preds.argmax(1) == y_raw).mean()
print(f"Accuracy: {acc*100:.1f}%")   # typically 96-98%

# ── Sample forward pass for animation ────────────────────────────────────────
sample = (np.array([5.1, 3.5, 1.4, 0.2]) - mu) / std  # Iris-setosa
a1_s, a2_s, a3_s = forward(sample.reshape(1,-1))
print("Output softmax:", a3_s.round(3))   # expect [~0.98, ~0.01, ~0.01]

# ── Export for Blender ────────────────────────────────────────────────────────
np.save("scripts/nn_weights.npy", {"W1":W1,"b1":b1,"W2":W2,"b2":b2,"W3":W3,"b3":b3,
                                    "a1":a1_s[0],"a2":a2_s[0],"a3":a3_s[0],
                                    "mu":mu,"std":std})
print("Saved scripts/nn_weights.npy")
```

## Expected output

After ~500 epochs the network achieves **96–98% accuracy** on Iris. The sample forward pass produces softmax outputs approximately `[0.97, 0.02, 0.01]`, confirming class 0 (setosa) wins decisively.

## Weight structure expected in the animation

After training, W1 row patterns typically show:
- **Petal length** (feature 2) and **petal width** (feature 3) have large positive weights into several Hidden 1 neurons — these are the discriminative features.
- **Sepal width** (feature 1) weights are small — it's less discriminative.

This produces a scene where the thicker green synapses cluster around petal-length inputs, giving the animation genuine visual interest.

## Loading weights in the Blender script

```python
import numpy as np
data   = np.load("scripts/nn_weights.npy", allow_pickle=True).item()
W1, W2, W3 = data['W1'], data['W2'], data['W3']
a1, a2, a3 = data['a1'], data['a2'], data['a3']
```

The weight value `W1[i, j]` drives the synapse from input neuron `i` to hidden-1 neuron `j`. The activation `a1[j]` drives the glow intensity of hidden-1 neuron `j`.

## Cross-links

- [stages/03-scene.md](./03-scene.md) — next: embed weights into Blender scene
- [concepts/weight-encoding.md](../concepts/weight-encoding.md) — how W1/W2/W3 map to colors
- [concepts/signal-propagation.md](../concepts/signal-propagation.md) — how a1/a2/a3 drive animation
