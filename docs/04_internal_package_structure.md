# CalCharts V1 — Internal Package Structure

This document defines the recommended internal package structure for the V1 implementation of `calcharts`.

## Goals

The package structure should:
- keep public API and internal implementation separate,
- allow chart types to reuse common geometry and rendering code,
- make testing straightforward,
- support future extension toward annotations and scene-based rendering,
- avoid premature complexity.

## Recommended package layout

```text
calcharts/
    __init__.py
    specs.py
    scene.py
    annotations.py
    colors.py
    charts/
        __init__.py
        checkerboard.py
        circle_grid.py
        siemens_star.py
        grayscale.py
        slanted_edge.py
        composite.py
    primitives/
        __init__.py
        base.py
        shapes.py
        grids.py
    renderers/
        __init__.py
        raster.py
    utils/
        __init__.py
        math.py
        validation.py
        image.py
```

## Responsibilities by module

### `calcharts/__init__.py`
Public exports only.

Should expose the main V1 user-facing objects, for example:
- `CanvasSpec`
- `RenderOptions`
- `AnnotationBundle`
- `CheckerboardChart`
- `CircleGridChart`
- `SiemensStarChart`
- `GrayscaleStepChart`
- `SlantedEdgeChart`
- `CompositeChart`

Do not place implementation logic here.

### `calcharts/specs.py`
Contains user-facing dataclasses and configuration objects.

Recommended contents:
- `CanvasSpec`
- `RenderOptions`
- maybe `ColorSpec` if needed in V1

This module should define declarative inputs, not rendering logic.

### `calcharts/scene.py`
Defines lightweight resolved scene representations.

Recommended contents:
- `Scene`
- `SceneElement`
- element transforms or placement fields
- style fields used by the renderer

Even if V1 keeps this simple, the scene layer should exist conceptually.

### `calcharts/annotations.py`
Defines structured outputs for metadata.

Recommended contents:
- `AnnotationBundle`
- point landmarks
- polygons / rectangles
- semantic labels

This should be format-agnostic and convenient for downstream CV use.

### `calcharts/colors.py`
Color utilities and normalization.

Recommended contents:
- grayscale / RGB parsing
- conversion of user colors to renderer-ready numeric values
- clipping / dtype preparation

Keep this modest in V1.

### `calcharts/charts/`
Contains chart-specific scene builders.

Each chart module should:
- validate its parameters,
- construct geometry,
- emit a resolved scene,
- optionally emit annotations.

Each chart should avoid direct pixel painting where possible.

Recommended chart modules:
- `checkerboard.py`
- `circle_grid.py`
- `siemens_star.py`
- `grayscale.py`
- `slanted_edge.py`
- `composite.py`

### `calcharts/primitives/base.py`
Foundational geometry dataclasses.

Recommended contents:
- `Rectangle`
- `Circle`
- `Polygon`
- `LineSegment`
- common style definitions

### `calcharts/primitives/shapes.py`
Helpers that generate primitive shape sets.

Examples:
- rectangle arrays
- wedges for Siemens star
- slanted edge polygon construction

### `calcharts/primitives/grids.py`
Reusable grid layout generators.

Examples:
- checkerboard cell placement
- circle center generation
- grayscale bar placement

### `calcharts/renderers/raster.py`
Raster rendering backend.

Responsibilities:
- render scene elements to NumPy arrays,
- honor canvas size and background,
- optionally support supersampling / anti-aliasing,
- return HxW or HxWxC arrays in a consistent format.

This is the main implementation backend for V1.

### `calcharts/utils/math.py`
Low-level math helpers.

Examples:
- angle calculations,
- coordinate helpers,
- line equations,
- rotation helpers.

### `calcharts/utils/validation.py`
Common validation utilities.

Examples:
- positive integer checks,
- bounds checks,
- enum-like option validation,
- shape consistency checks.

### `calcharts/utils/image.py`
Simple output helpers.

Examples:
- PNG save helper,
- dtype conversion,
- maybe PIL integration.

## Design rules

1. Chart modules build scenes, not pixels.
2. Rendering happens in the renderer layer.
3. Annotation generation stays explicit.
4. Parameter validation should happen near the chart constructor.
5. Avoid inheritance-heavy design in V1.

## Suggested class style

Prefer dataclasses and composition over deep class hierarchies.

A minimal common chart base class is acceptable if it helps unify:
- `to_scene()`
- `get_annotations()`
- `render()`
- `save()`

But avoid complicated abstract class stacks in V1.

## Minimal skeleton to build first

```text
calcharts/
    __init__.py
    specs.py
    annotations.py
    charts/
        checkerboard.py
    renderers/
        raster.py
    utils/
        validation.py
        image.py
```

Then extend step by step.

## Why this structure is the next step

Codex needs a clear implementation skeleton.
Without one, it may invent inconsistent module boundaries and entangle chart generation with raster drawing.
This package layout gives it a sane starting point while leaving room for future growth.
