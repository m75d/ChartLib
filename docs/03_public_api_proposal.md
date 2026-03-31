# CalCharts — Public API Proposal

## 1. API Design Goals

The public API should be:
- explicit
- typed
- composable
- deterministic
- easy to inspect and test

The API should avoid overly magical behavior.

## 2. Main User Concepts

### 2.1 Canvas
Defines the output image domain.

Example:

```python
from calcharts import CanvasSpec

canvas = CanvasSpec(
    width=1920,
    height=1080,
    channels=3,
    background=(1.0, 1.0, 1.0),
)
```

### 2.2 Chart objects
Each built-in chart should be represented by a dedicated class.

Examples:
- `CheckerboardChart`
- `CircleGridChart`
- `SiemensStarChart`
- `GrayscaleStepChart`
- `SlantedEdgeChart`
- `CompositeChart`

### 2.3 Rendering
A chart should be easy to render and save.

```python
img = chart.render()
chart.save("chart.png")
```

### 2.4 Annotations
Annotations should be optional and structured.

```python
img, ann = chart.render(return_annotations=True)
```

## 3. Proposed Top-level API

```python
from calcharts import (
    CanvasSpec,
    CheckerboardChart,
    CircleGridChart,
    SiemensStarChart,
    GrayscaleStepChart,
    SlantedEdgeChart,
    CompositeChart,
)
```

## 4. Proposed Class Sketches

### 4.1 CanvasSpec

```python
CanvasSpec(
    width: int,
    height: int,
    channels: int = 1,
    background=0.0,
)
```

Notes:
- `channels=1` for grayscale
- `channels=3` for RGB
- background may be scalar or tuple depending on channel count

### 4.2 CheckerboardChart

```python
CheckerboardChart(
    canvas: CanvasSpec,
    rows: int,
    cols: int,
    square_size: int,
    origin: tuple[int, int] | None = None,
    invert: bool = False,
)
```

### 4.3 CircleGridChart

```python
CircleGridChart(
    canvas: CanvasSpec,
    rows: int,
    cols: int,
    spacing: float,
    radius: float,
    origin: tuple[float, float] | None = None,
    staggered: bool = False,
)
```

### 4.4 SiemensStarChart

```python
SiemensStarChart(
    canvas: CanvasSpec,
    center: tuple[float, float],
    radius: float,
    num_sectors: int,
    inner_radius: float = 0.0,
)
```

### 4.5 GrayscaleStepChart

```python
GrayscaleStepChart(
    canvas: CanvasSpec,
    num_steps: int,
    step_values: list[float] | None = None,
    patch_width: int = 64,
    patch_height: int = 64,
    origin: tuple[int, int] | None = None,
    orientation: str = "horizontal",
)
```

### 4.6 SlantedEdgeChart

```python
SlantedEdgeChart(
    canvas: CanvasSpec,
    center: tuple[float, float],
    length: float,
    angle_deg: float,
    edge_width: float,
    dark_side=0.0,
    bright_side=1.0,
)
```

### 4.7 CompositeChart

```python
CompositeChart(
    canvas: CanvasSpec,
    elements: list,
)
```

## 5. Common Methods

All chart classes should support at least:

```python
chart.render(return_annotations: bool = False)
chart.save(path: str, return_annotations: bool = False)
chart.get_annotations()
```

Possible behavior:
- `render()` returns image only
- `render(return_annotations=True)` returns `(image, annotations)`
- `save()` writes PNG
- `get_annotations()` returns structured metadata independent of rendering if possible

## 6. Example Usage

### 6.1 Simple checkerboard

```python
from calcharts import CanvasSpec, CheckerboardChart

canvas = CanvasSpec(width=1920, height=1080, channels=1, background=1.0)
chart = CheckerboardChart(canvas=canvas, rows=6, cols=9, square_size=80)
img = chart.render()
chart.save("checkerboard.png")
```

### 6.2 Siemens star with annotations

```python
from calcharts import CanvasSpec, SiemensStarChart

canvas = CanvasSpec(width=1024, height=1024, channels=1, background=1.0)
chart = SiemensStarChart(canvas=canvas, center=(512, 512), radius=400, num_sectors=72)
img, ann = chart.render(return_annotations=True)
```

### 6.3 Composite chart

```python
from calcharts import (
    CanvasSpec,
    CompositeChart,
    SiemensStarChart,
    GrayscaleStepChart,
)

canvas = CanvasSpec(width=1920, height=1080, channels=1, background=1.0)

star = SiemensStarChart(
    canvas=canvas,
    center=(500, 540),
    radius=280,
    num_sectors=72,
)

steps = GrayscaleStepChart(
    canvas=canvas,
    num_steps=12,
    patch_width=60,
    patch_height=120,
    origin=(1100, 480),
)

chart = CompositeChart(canvas=canvas, elements=[star, steps])
img = chart.render()
```

## 7. Annotation Format Proposal

A lightweight dictionary-based format is sufficient for V1.

Example:

```python
{
    "chart_type": "checkerboard",
    "image_size": [1920, 1080],
    "landmarks": {
        "inner_corners": [[x1, y1], [x2, y2], ...]
    },
    "regions": {
        "squares": [
            {"id": 0, "polygon": [[...], [...], [...], [...]], "color": 0},
            {"id": 1, "polygon": [[...], [...], [...], [...]], "color": 1},
        ]
    }
}
```

This can be refined later, but should stay stable and predictable.

## 8. API Principles to Preserve

- built-in charts are convenience wrappers around reusable internal geometry
- public API stays small in V1
- charts should not require users to understand internal scene abstractions
- annotation support is first-class, not an afterthought
- saving/rendering should be simple and unsurprising

## 9. Recommended Implementation Order for API

1. `CanvasSpec`
2. base chart class
3. `CheckerboardChart`
4. `CircleGridChart`
5. `GrayscaleStepChart`
6. `SiemensStarChart`
7. `SlantedEdgeChart`
8. `CompositeChart`
9. annotation stabilization
10. examples and tests
