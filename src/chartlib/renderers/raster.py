"""Minimal raster rendering for rectangle-, circle-, slanted-edge, and Siemens-star charts."""

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


def render_slanted_edge_region(
    canvas: CanvasSpec,
    chart_x: int,
    chart_y: int,
    chart_width: int,
    chart_height: int,
    edge_angle_degrees: float,
    dark_value: int | float | tuple[int | float, ...],
    light_value: int | float | tuple[int | float, ...],
    background_value: int | float | tuple[int | float, ...] | None = None,
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render a rectangular chart region split by a single slanted edge."""

    render_options = options or RenderOptions()
    fill_value = canvas.background if background_value is None else background_value
    background = normalize_color(fill_value, canvas.channels, "background")
    dark = normalize_color(dark_value, canvas.channels, "dark_value")
    light = normalize_color(light_value, canvas.channels, "light_value")
    dtype = render_options.dtype

    if canvas.channels == 1:
        image = np.full((canvas.height, canvas.width), background[0], dtype=dtype)
    else:
        image = np.full((canvas.height, canvas.width, canvas.channels), background, dtype=dtype)

    theta = np.deg2rad(edge_angle_degrees)
    direction_x = np.sin(theta)
    direction_y = np.cos(theta)
    center_x = chart_x + chart_width / 2.0
    center_y = chart_y + chart_height / 2.0

    yy, xx = np.ogrid[chart_y:chart_y + chart_height, chart_x:chart_x + chart_width]
    x_centers = xx + 0.5
    y_centers = yy + 0.5
    signed = direction_y * (x_centers - center_x) - direction_x * (y_centers - center_y)
    dark_mask = signed < 0

    if canvas.channels == 1:
        region = image[chart_y:chart_y + chart_height, chart_x:chart_x + chart_width]
        region[:] = light[0]
        region[dark_mask] = dark[0]
    else:
        region = image[chart_y:chart_y + chart_height, chart_x:chart_x + chart_width]
        region[:] = light
        region[dark_mask] = dark

    return image


def render_siemens_star(
    canvas: CanvasSpec,
    center_x: int,
    center_y: int,
    outer_radius: int,
    num_sectors: int,
    inner_radius: int = 0,
    dark_value: int | float | tuple[int | float, ...] = 0,
    light_value: int | float | tuple[int | float, ...] = 255,
    background_value: int | float | tuple[int | float, ...] | None = None,
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render an ideal Siemens star with alternating angular sectors."""

    render_options = options or RenderOptions()
    image = render_primitives(canvas=canvas, options=render_options)
    dark = normalize_color(dark_value, canvas.channels, "dark_value")
    light = normalize_color(light_value, canvas.channels, "light_value")
    hole = normalize_color(
        canvas.background if background_value is None else background_value,
        canvas.channels,
        "background_value",
    )

    y0 = max(0, center_y - outer_radius)
    y1 = min(canvas.height, center_y + outer_radius)
    x0 = max(0, center_x - outer_radius)
    x1 = min(canvas.width, center_x + outer_radius)

    yy, xx = np.ogrid[y0:y1, x0:x1]
    x_centers = xx + 0.5 - center_x
    y_centers = center_y - (yy + 0.5)
    radius_squared = x_centers**2 + y_centers**2

    outer_mask = radius_squared <= outer_radius**2
    inner_mask = radius_squared < inner_radius**2 if inner_radius > 0 else np.zeros_like(outer_mask, dtype=bool)
    annulus_mask = outer_mask & ~inner_mask

    angles = np.mod(np.arctan2(y_centers, x_centers), 2.0 * np.pi)
    sector_width = (2.0 * np.pi) / float(num_sectors)
    sector_indices = np.floor(angles / sector_width).astype(np.int32)
    dark_mask = annulus_mask & ((sector_indices % 2) == 0)
    light_mask = annulus_mask & ((sector_indices % 2) == 1)

    region = image[y0:y1, x0:x1]
    if canvas.channels == 1:
        region[dark_mask] = dark[0]
        region[light_mask] = light[0]
        if inner_radius > 0:
            region[inner_mask] = hole[0]
    else:
        region[dark_mask] = dark
        region[light_mask] = light
        if inner_radius > 0:
            region[inner_mask] = hole

    return image


def render_circles_in_rectangle(
    canvas: CanvasSpec,
    rect_x: int,
    rect_y: int,
    rect_width: int,
    rect_height: int,
    circles: list[RasterCircle],
    background_value: int | float | tuple[int | float, ...] | None = None,
    options: RenderOptions | None = None,
) -> np.ndarray:
    """Render circles clipped to a rectangular region on the canvas."""

    image = render_primitives(canvas=canvas, options=options)
    fill = canvas.background if background_value is None else background_value
    background = normalize_color(fill, canvas.channels, "background_value")
    y1 = rect_y + rect_height
    x1 = rect_x + rect_width

    if canvas.channels == 1:
        image[rect_y:y1, rect_x:x1] = background[0]
    else:
        image[rect_y:y1, rect_x:x1] = background

    for circle in circles:
        color = normalize_color(circle.color, canvas.channels, "circle.color")
        y0 = max(rect_y, circle.center_y - circle.radius)
        y1_circle = min(rect_y + rect_height, circle.center_y + circle.radius + 1)
        x0 = max(rect_x, circle.center_x - circle.radius)
        x1_circle = min(rect_x + rect_width, circle.center_x + circle.radius + 1)

        if y0 >= y1_circle or x0 >= x1_circle:
            continue

        yy, xx = np.ogrid[y0:y1_circle, x0:x1_circle]
        mask = (xx - circle.center_x) ** 2 + (yy - circle.center_y) ** 2 <= circle.radius**2

        if canvas.channels == 1:
            image[y0:y1_circle, x0:x1_circle][mask] = color[0]
        else:
            image[y0:y1_circle, x0:x1_circle][mask] = color

    return image
