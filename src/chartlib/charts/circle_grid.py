"""Circle grid chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle
from chartlib.renderers.raster import RasterCircle, RasterRectangle, render_primitives
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import (
    validate_non_negative_int,
    validate_positive_int,
)


@dataclass(frozen=True)
class CircleGridChart:
    """Render an ideal axis-aligned circle grid chart."""

    canvas: CanvasSpec
    rows: int
    cols: int
    radius: int
    spacing: int | tuple[int, int]
    origin: tuple[int, int] | None = None
    invert: bool = False
    dark_value: int = 0
    light_value: int = 255

    def __post_init__(self) -> None:
        validate_positive_int(self.rows, "rows")
        validate_positive_int(self.cols, "cols")
        validate_positive_int(self.radius, "radius")
        validate_non_negative_int(self.dark_value, "dark_value")
        validate_non_negative_int(self.light_value, "light_value")

        if self.dark_value > 255 or self.light_value > 255:
            raise ValueError("dark_value and light_value must be in the range [0, 255].")

        spacing_x, spacing_y = self._resolved_spacing()
        origin_x, origin_y = self._resolved_origin()
        chart_width = 2 * self.radius + (self.cols - 1) * spacing_x
        chart_height = 2 * self.radius + (self.rows - 1) * spacing_y

        if origin_x + chart_width > self.canvas.width or origin_y + chart_height > self.canvas.height:
            raise ValueError("Circle grid does not fit inside the canvas.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        render_options = options or RenderOptions()
        image = render_primitives(
            canvas=self.canvas,
            rectangles=self._background_rectangles(),
            circles=self._circles(),
            options=render_options,
        )

        if return_annotations:
            return image, self.get_annotations()
        return image

    def save(
        self,
        path: str | Path,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> AnnotationBundle | None:
        rendered = self.render(return_annotations=return_annotations, options=options)
        if return_annotations:
            image, annotations = rendered
            save_png(image, path)
            return annotations

        save_png(rendered, path)
        return None

    def get_annotations(self) -> AnnotationBundle:
        centers = [
            (float(circle.center_x), float(circle.center_y))
            for circle in self._circles()
        ]

        return AnnotationBundle(
            chart_type="circle_grid",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={"centers": centers},
        )

    def _background_rectangles(self) -> list[RasterRectangle]:
        origin_x, origin_y = self._resolved_origin()
        chart_width, chart_height = self._chart_size()
        _, background_value = self._resolved_colors()
        return [
            RasterRectangle(
                x=origin_x,
                y=origin_y,
                width=chart_width,
                height=chart_height,
                color=background_value,
            )
        ]

    def _circles(self) -> list[RasterCircle]:
        origin_x, origin_y = self._resolved_origin()
        spacing_x, spacing_y = self._resolved_spacing()
        foreground_value, _ = self._resolved_colors()
        circles: list[RasterCircle] = []

        for row in range(self.rows):
            for col in range(self.cols):
                circles.append(
                    RasterCircle(
                        center_x=origin_x + self.radius + col * spacing_x,
                        center_y=origin_y + self.radius + row * spacing_y,
                        radius=self.radius,
                        color=foreground_value,
                    )
                )

        return circles

    def _resolved_colors(self) -> tuple[int, int]:
        if self.invert:
            return self.light_value, self.dark_value
        return self.dark_value, self.light_value

    def _resolved_spacing(self) -> tuple[int, int]:
        if isinstance(self.spacing, tuple):
            if len(self.spacing) != 2:
                raise ValueError("spacing must be a positive integer or a 2-tuple of positive integers.")
            spacing_x, spacing_y = self.spacing
        else:
            spacing_x = self.spacing
            spacing_y = self.spacing

        validate_positive_int(spacing_x, "spacing_x")
        validate_positive_int(spacing_y, "spacing_y")
        return spacing_x, spacing_y

    def _chart_size(self) -> tuple[int, int]:
        spacing_x, spacing_y = self._resolved_spacing()
        return (
            2 * self.radius + (self.cols - 1) * spacing_x,
            2 * self.radius + (self.rows - 1) * spacing_y,
        )

    def _resolved_origin(self) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        chart_width, chart_height = self._chart_size()
        return (
            (self.canvas.width - chart_width) // 2,
            (self.canvas.height - chart_height) // 2,
        )
