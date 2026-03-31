"""Minimal raster rendering for rectangle-based charts."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from calcharts.specs import CanvasSpec, RenderOptions
from calcharts.utils.validation import normalize_color, validate_positive_int


@dataclass(frozen=True)
class RasterRectangle:
    """Axis-aligned filled rectangle in image coordinates."""

    x: int
    y: int
    width: int
    height: int
    color: int | float | tuple[int | float, ...]

    def __post_init__(self) -> None:
        validate_positive_int(self.width, "width")
        validate_positive_int(self.height, "height")


def render_rectangles(
    canvas: CanvasSpec,
    rectangles: list[RasterRectangle],
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render filled rectangles onto a NumPy image."""

    render_options = options or RenderOptions()
    background = normalize_color(canvas.background, canvas.channels, "background")

    if canvas.channels == 1:
        image = np.full((canvas.height, canvas.width), background[0], dtype=np.uint8)
    else:
        image = np.full((canvas.height, canvas.width, canvas.channels), background, dtype=np.uint8)

    for rectangle in rectangles:
        color = normalize_color(rectangle.color, canvas.channels, "rectangle.color")
        y0 = rectangle.y
        y1 = rectangle.y + rectangle.height
        x0 = rectangle.x
        x1 = rectangle.x + rectangle.width

        if canvas.channels == 1:
            image[y0:y1, x0:x1] = color[0]
        else:
            image[y0:y1, x0:x1] = color

    return image.astype(render_options.dtype, copy=False)

