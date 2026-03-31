"""Checkerboard chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from calcharts.annotations import AnnotationBundle
from calcharts.renderers.raster import RasterRectangle, render_rectangles
from calcharts.specs import CanvasSpec, RenderOptions
from calcharts.utils.image import save_png
from calcharts.utils.validation import (
    validate_non_negative_int,
    validate_positive_int,
)


@dataclass(frozen=True)
class CheckerboardChart:
    """Render an ideal axis-aligned checkerboard chart."""

    canvas: CanvasSpec
    rows: int
    cols: int
    square_size: int
    origin: tuple[int, int] | None = None
    invert: bool = False
    dark_value: int = 0
    light_value: int = 255

    def __post_init__(self) -> None:
        validate_positive_int(self.rows, "rows")
        validate_positive_int(self.cols, "cols")
        validate_positive_int(self.square_size, "square_size")
        validate_non_negative_int(self.dark_value, "dark_value")
        validate_non_negative_int(self.light_value, "light_value")

        if self.dark_value > 255 or self.light_value > 255:
            raise ValueError("dark_value and light_value must be in the range [0, 255].")

        origin_x, origin_y = self._resolved_origin()
        chart_width = self.cols * self.square_size
        chart_height = self.rows * self.square_size

        if origin_x + chart_width > self.canvas.width or origin_y + chart_height > self.canvas.height:
            raise ValueError("Checkerboard does not fit inside the canvas.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        render_options = options or RenderOptions()
        image = render_rectangles(
            canvas=self.canvas,
            rectangles=self._rectangles(),
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
        origin_x, origin_y = self._resolved_origin()
        corners: list[tuple[float, float]] = []

        for row in range(1, self.rows):
            for col in range(1, self.cols):
                x = origin_x + col * self.square_size
                y = origin_y + row * self.square_size
                corners.append((float(x), float(y)))

        return AnnotationBundle(
            chart_type="checkerboard",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={"inner_corners": corners},
        )

    def _rectangles(self) -> list[RasterRectangle]:
        origin_x, origin_y = self._resolved_origin()
        rectangles: list[RasterRectangle] = []

        for row in range(self.rows):
            for col in range(self.cols):
                is_dark = (row + col) % 2 == 0
                if self.invert:
                    is_dark = not is_dark

                value = self.dark_value if is_dark else self.light_value
                rectangles.append(
                    RasterRectangle(
                        x=origin_x + col * self.square_size,
                        y=origin_y + row * self.square_size,
                        width=self.square_size,
                        height=self.square_size,
                        color=value,
                    )
                )

        return rectangles

    def _resolved_origin(self) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        chart_width = self.cols * self.square_size
        chart_height = self.rows * self.square_size
        return (
            (self.canvas.width - chart_width) // 2,
            (self.canvas.height - chart_height) // 2,
        )

