---
type: "API Reference"
title: "Scene Setup and Collections"
description: "Blender Python API patterns for clearing the default scene and organizing objects into named layer collections."
resource: "file:///home/user/SkillOpt/scripts/blender_nn_render.py#PHASE-1"
tags: ["blender", "bpy", "collections", "scene", "outliner"]
timestamp: "2026-07-11"
---

# Scene Setup and Collections

## Clearing the default scene

```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
```

This removes the default cube, camera, and light. Run this before building the neural network scene. `use_global=False` respects multi-scene setups (only deletes from the active scene).

## Creating a layer collection

```python
layer_collection = bpy.data.collections.new(f"Layer_{i}")
bpy.context.scene.collection.children.link(layer_collection)
```

`bpy.data.collections.new()` creates the collection data block; `.children.link()` attaches it to the scene's root collection so it appears in the Outliner. The collection is then used to group all neurons in layer `i`.

## Linking an object to a collection (not the scene directly)

```python
layer_collection.objects.link(empty)
```

Do **not** also call `bpy.context.scene.collection.objects.link(empty)` — that would create a duplicate entry. Objects linked to a child collection are already part of the scene hierarchy.

## Why collections matter for animation

The Layer collections allow toggling entire layers' visibility (`layer_collection.hide_viewport`) during development and rendering. In the improved script, layer collections are revealed sequentially during the animation to emphasize the forward-pass structure.

## Cross-links

- [concepts/neuron-as-empty.md](../concepts/neuron-as-empty.md) — the objects being collected
- [stages/03-scene.md](../stages/03-scene.md) — when to run scene setup in the PDLC
