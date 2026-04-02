# ChartLib

ChartLib is a typed Python library for generating ideal 2D calibration and reference charts as NumPy arrays, with PNG export and structured annotations.

The current repository state implements a small V1 foundation with these built-in chart types:

- `CheckerboardChart`
- `CircleGridChart`
- `GrayscaleStepChart`
- `SiemensStarChart`
- `SlantedEdgeChart`

## Install

```bash
pip install -e .
```

For test dependencies:

```bash
pip install -e .[dev]
```

## Example

```python
from chartlib import (
    CanvasSpec,
    CheckerboardChart,
    CircleGridChart,
    GrayscaleStepChart,
    SiemensStarChart,
    SlantedEdgeChart,
)

canvas = CanvasSpec(width=320, height=240, channels=1, background=255)
checkerboard = CheckerboardChart(canvas=canvas, rows=4, cols=5, square_size=40)
circle_grid = CircleGridChart(canvas=canvas, rows=3, cols=4, radius=10, spacing=30)
steps = GrayscaleStepChart(canvas=canvas, steps=5, step_size=(20, 60))
star = SiemensStarChart(canvas=canvas, outer_radius=90, num_sectors=32)
slanted = SlantedEdgeChart(canvas=canvas, chart_size=(120, 80), edge_angle_degrees=5.0)

image, annotations = checkerboard.render(return_annotations=True)
circle_grid.save("circle-grid.png")
steps.save("grayscale-step.png")
star.save("siemens-star.png")
slanted.save("slanted-edge.png")
```

## Current Scope

- package skeleton under `src/chartlib`
- project configuration via `pyproject.toml`
- `CanvasSpec`
- `RenderOptions`
- basic validation helpers
- raster rendering for filled rectangles and circles
- `CheckerboardChart`
- `CircleGridChart`
- `GrayscaleStepChart`
- `SiemensStarChart`
- `SlantedEdgeChart`
- structured annotations for corners, centers, and step regions
- structured annotations for Siemens-star center and geometry
- structured annotations for slanted-edge geometry
- PNG export
- pytest coverage for the implemented V1 slices

## Annotation Structure

`AnnotationBundle` remains the public annotation container.
Where charts expose `regions`, the payloads now use common bounds fields: `type`, `x`, `y`, `width`, and `height`, while preserving chart-specific keys such as `steps`, `chart`, `edge`, and `star`.

## Slanted Edge Convention

`SlantedEdgeChart` uses a single straight edge passing through the center of the chart rectangle.
`edge_angle_degrees` is measured relative to the vertical axis: `0.0` is a vertical edge, and positive angles tilt the lower part of the edge to the right.
