# CalCharts — Project Scope and Architecture

## 1. Project Goal

CalCharts is a Python library for generating **ideal 2D calibration/reference charts** as raster images, together with optional structured annotations.

The library is intended primarily for:
- computer vision workflows
- imaging algorithm development
- synthetic data generation
- calibration and evaluation pipelines
- controlled generation of mathematically defined chart content

It is **not** intended in V1 to be a print-oriented chart tool.

## 2. Core Design Principle

The library should model charts as **structured 2D scenes** rather than as ad-hoc drawing code that writes directly into an image buffer.

That means each chart should exist conceptually as:
- a chart-plane scene
- composed of reusable elements
- with exact geometry
- with style/rendering attributes
- with semantic meaning and optional annotations

Raster rendering is then one backend built on top of that representation.

## 3. Scope of V1

V1 focuses on **ideal chart synthesis**:
- exact geometry
- deterministic rendering
- configurable raster output
- annotations for key landmarks / regions / masks where relevant

V1 does **not** include camera-capture simulation such as:
- intrinsics / extrinsics
- perspective projection
- lens distortion
- illumination simulation
- blur / PSF / defocus
- noise / CFA / ISP

## 4. Architectural Layers

### 4.1 User-facing specification layer
This is the public API layer.
It should let the user define:
- canvas size
- chart type
- chart parameters
- composition/layout
- rendering/export options

### 4.2 Scene / geometry layer
This layer defines resolved chart-plane geometry:
- positions
- sizes
- shapes
- anchors
- transforms
- semantic labels

This is the most important internal layer.

### 4.3 Chart generator layer
This layer provides reusable chart definitions such as:
- checkerboard
- circle grid
- Siemens star
- grayscale step chart
- slanted edge
- composite chart

Each chart should build a scene representation, not draw pixels directly.

### 4.4 Raster rendering layer
This layer converts the resolved scene into a raster image.
Key concerns:
- grayscale / RGB output
- dtype / bit depth policy
- optional anti-aliasing
- deterministic output

### 4.5 Annotation layer
This layer provides structured metadata such as:
- landmarks
- corners
- centers
- polygons
- regions
- masks
- chart-space to image-space correspondences

## 5. Why Scene-first Matters

Even though camera simulation is postponed, V1 should still preserve enough structure to support it later.

A future simulator may need:
- chart-plane coordinates
- exact keypoint locations
- semantic region identities
- shape boundaries

If V1 only produces pixels, that future extension becomes much harder.

## 6. Main Output Types

V1 should support:
- raster image output
- optional structured annotations

Typical rendering call:

```python
img = chart.render()
```

Typical rendering call with annotations:

```python
img, ann = chart.render(return_annotations=True)
```

## 7. Suggested Internal Package Structure

```text
calcharts/
    __init__.py
    scene/
        canvas.py
        elements.py
        geometry.py
        annotations.py
    charts/
        checkerboard.py
        circle_grid.py
        siemens_star.py
        slanted_edge.py
        grayscale.py
        composite.py
    renderers/
        raster.py
    metadata/
        landmarks.py
        masks.py
        regions.py
    utils/
        color.py
        units.py
        math.py
    tests/
        ...
```

## 8. Future Extension Point

A future `simulation/` package can be added later, cleanly separated from chart generation:

```text
simulation/
    camera.py
    projection.py
    optics.py
    illumination.py
    sensor.py
```

This separation should be preserved from the beginning.

## 9. Design Risks to Avoid

- mixing layout logic with rasterization
- making each chart a one-off special case
- overcommitting to exact real-world standards too early
- ignoring annotation support
- baking future camera simulation assumptions into V1 rendering code

## 10. Recommended V1 Philosophy

Build CalCharts V1 as an **ideal chart scene generator with raster rendering and annotations**.

That gives:
- a clean core
- practical utility for CV/imaging work
- a stable basis for future simulation features
