"""
Train a [4, 6, 5, 3] feedforward network on the Iris dataset.
Produces scripts/nn_weights.npy for use by blender_nn_render.py.
No ML framework required — NumPy only.
"""
import numpy as np
from pathlib import Path

import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.iris_data import X_raw, y_raw

# Normalise
mu  = X_raw.mean(axis=0)
std = X_raw.std(axis=0)
X   = (X_raw - mu) / std
Y   = np.eye(3)[y_raw]

def xavier(fan_in, fan_out, rng):
    limit = np.sqrt(6 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, (fan_in, fan_out))

rng = np.random.default_rng(42)
W1 = xavier(4, 6, rng);  b1 = np.zeros(6)
W2 = xavier(6, 5, rng);  b2 = np.zeros(5)
W3 = xavier(5, 3, rng);  b3 = np.zeros(3)

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def forward(X):
    a1 = relu(X @ W1 + b1)
    a2 = relu(a1 @ W2 + b2)
    a3 = softmax(a2 @ W3 + b3)
    return a1, a2, a3

lr, epochs, batch_size = 0.05, 600, 16

for epoch in range(epochs):
    idx = rng.permutation(150)
    for start in range(0, 150, batch_size):
        mb = idx[start:start + batch_size]
        Xb, Yb = X[mb], Y[mb]
        a1, a2, a3 = forward(Xb)

        d3 = (a3 - Yb) / len(mb)
        dW3 = a2.T @ d3;  db3 = d3.sum(0)

        d2 = (d3 @ W3.T) * (a2 > 0)
        dW2 = a1.T @ d2;  db2 = d2.sum(0)

        d1 = (d2 @ W2.T) * (a1 > 0)
        dW1 = Xb.T @ d1;  db1 = d1.sum(0)

        W1 -= lr * dW1;  b1 -= lr * db1
        W2 -= lr * dW2;  b2 -= lr * db2
        W3 -= lr * dW3;  b3 -= lr * db3

_, _, preds = forward(X)
acc = (preds.argmax(1) == y_raw).mean()
print(f"Training accuracy: {acc * 100:.1f}%")

# Sample forward pass — Iris setosa specimen
sample = (np.array([5.1, 3.5, 1.4, 0.2]) - mu) / std
a1_s, a2_s, a3_s = forward(sample.reshape(1, -1))
print(f"Sample softmax: {a3_s.round(4)}  -> class {a3_s.argmax()}")

out_path = Path(__file__).parent / "nn_weights.npy"
np.save(out_path, {
    "W1": W1, "b1": b1,
    "W2": W2, "b2": b2,
    "W3": W3, "b3": b3,
    "mu": mu, "std": std,
    "a1": a1_s[0], "a2": a2_s[0], "a3": a3_s[0],
})
print(f"Saved {out_path}")
