"""Minimal raster rendering for rectangle- and circle-based charts."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.validation import normalize_color, validate_positive_int


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


@dataclass(frozen=True)
class RasterCircle:
    """Filled circle in image coordinates."""

    center_x: int
    center_y: int
    radius: int
    color: int | float | tuple[int | float, ...]

    def __post_init__(self) -> None:
        validate_positive_int(self.radius, "radius")


def render_rectangles(
    canvas: CanvasSpec,
    rectangles: list[RasterRectangle],
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render filled rectangles onto a NumPy image."""

    return render_primitives(canvas=canvas, rectangles=rectangles, options=options)


def render_primitives(
    canvas: CanvasSpec,
    rectangles: list[RasterRectangle] | None = None,
    circles: list[RasterCircle] | None = None,
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render a small set of filled primitives onto a NumPy image."""

    render_options = options or RenderOptions()
    background = normalize_color(canvas.background, canvas.channels, "background")
    dtype = render_options.dtype
    rectangle_list = rectangles or []
    circle_list = circles or []

    if canvas.channels == 1:
        image = np.full((canvas.height, canvas.width), background[0], dtype=dtype)
    else:
        image = np.full((canvas.height, canvas.width, canvas.channels), background, dtype=dtype)

    for rectangle in rectangle_list:
        color = normalize_color(rectangle.color, canvas.channels, "rectangle.color")
        y0 = rectangle.y
        y1 = rectangle.y + rectangle.height
        x0 = rectangle.x
        x1 = rectangle.x + rectangle.width

        if canvas.channels == 1:
            image[y0:y1, x0:x1] = color[0]
        else:
            image[y0:y1, x0:x1] = color

    for circle in circle_list:
        color = normalize_color(circle.color, canvas.channels, "circle.color")
        y0 = max(0, circle.center_y - circle.radius)
        y1 = min(canvas.height, circle.center_y + circle.radius + 1)
        x0 = max(0, circle.center_x - circle.radius)
        x1 = min(canvas.width, circle.center_x + circle.radius + 1)

        yy, xx = np.ogrid[y0:y1, x0:x1]
        mask = (xx - circle.center_x) ** 2 + (yy - circle.center_y) ** 2 <= circle.radius ** 2

        if canvas.channels == 1:
            image[y0:y1, x0:x1][mask] = color[0]
        else:
            image[y0:y1, x0:x1][mask] = color

    return image
