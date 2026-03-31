# ChartLib

ChartLib currently implements the first V1 milestone: a minimal, typed Python package that can render an ideal checkerboard chart to a NumPy array, save it as PNG, and return checkerboard corner annotations.

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
from chartlib import CanvasSpec, CheckerboardChart

canvas = CanvasSpec(width=320, height=240, channels=1, background=255)
chart = CheckerboardChart(canvas=canvas, rows=4, cols=5, square_size=40)

image, annotations = chart.render(return_annotations=True)
chart.save("checkerboard.png")
```

## Included in this milestone

- package skeleton under `src/chartlib`
- project configuration via `pyproject.toml`
- `CanvasSpec`
- `RenderOptions`
- basic validation helpers
- minimal raster rendering for rectangles
- `CheckerboardChart`
- checkerboard corner annotations
- pytest coverage for the first vertical slice
