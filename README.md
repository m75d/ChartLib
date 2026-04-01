# ChartLib

ChartLib is a typed Python library for generating ideal 2D calibration and reference charts as NumPy arrays, with PNG export and structured annotations.

The current repository state implements a small V1 foundation with these built-in chart types:

- `CheckerboardChart`
- `CircleGridChart`
- `GrayscaleStepChart`

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
from chartlib import CanvasSpec, CheckerboardChart, CircleGridChart, GrayscaleStepChart

canvas = CanvasSpec(width=320, height=240, channels=1, background=255)
checkerboard = CheckerboardChart(canvas=canvas, rows=4, cols=5, square_size=40)
circle_grid = CircleGridChart(canvas=canvas, rows=3, cols=4, radius=10, spacing=30)
steps = GrayscaleStepChart(canvas=canvas, steps=5, step_size=(20, 60))

image, annotations = checkerboard.render(return_annotations=True)
circle_grid.save("circle-grid.png")
steps.save("grayscale-step.png")
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
- structured annotations for corners, centers, and step regions
- PNG export
- pytest coverage for the implemented V1 slices
