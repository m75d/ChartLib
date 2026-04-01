"""Grayscale step chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle
from chartlib.renderers.raster import RasterRectangle, render_rectangles
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class GrayscaleStepChart:
    """Render an ideal axis-aligned grayscale step chart."""

    canvas: CanvasSpec
    steps: int
    step_size: tuple[int, int] | int
    orientation: str = "horizontal"
    values: list[int] | None = None
    origin: tuple[int, int] | None = None
    background_value: int | None = None

    def __post_init__(self) -> None:
        validate_positive_int(self.steps, "steps")
        step_width, step_height = self._resolved_step_size()

        if self.orientation not in ("horizontal", "vertical"):
            raise ValueError("orientation must be 'horizontal' or 'vertical'.")

        if self.background_value is not None:
            validate_non_negative_int(self.background_value, "background_value")
            if self.background_value > 255:
                raise ValueError("background_value must be in the range [0, 255].")

        values = self._resolved_values()
        origin_x, origin_y = self._resolved_origin(step_width, step_height)
        chart_width, chart_height = self._chart_size(step_width, step_height)

        if origin_x + chart_width > self.canvas.width or origin_y + chart_height > self.canvas.height:
            raise ValueError("Grayscale step chart does not fit inside the canvas.")

        # Force validation early in __post_init__ so bad user inputs fail at construction time.
        for value in values:
            if not 0 <= value <= 255:
                raise ValueError("values must contain integers in the range [0, 255].")

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
        step_width, step_height = self._resolved_step_size()
        origin_x, origin_y = self._resolved_origin(step_width, step_height)
        values = self._resolved_values()
        centers: list[tuple[float, float]] = []
        regions: list[dict[str, object]] = []

        for index, value in enumerate(values):
            x, y = self._step_origin(index, origin_x, origin_y, step_width, step_height)
            centers.append((float(x + step_width / 2), float(y + step_height / 2)))
            regions.append(
                {
                    "index": index,
                    "value": value,
                    "x": x,
                    "y": y,
                    "width": step_width,
                    "height": step_height,
                }
            )

        return AnnotationBundle(
            chart_type="grayscale_step",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={"centers": centers},
            regions={"steps": regions},
        )

    def _rectangles(self) -> list[RasterRectangle]:
        step_width, step_height = self._resolved_step_size()
        origin_x, origin_y = self._resolved_origin(step_width, step_height)
        values = self._resolved_values()
        rectangles: list[RasterRectangle] = []

        if self.background_value is not None:
            chart_width, chart_height = self._chart_size(step_width, step_height)
            rectangles.append(
                RasterRectangle(
                    x=origin_x,
                    y=origin_y,
                    width=chart_width,
                    height=chart_height,
                    color=self.background_value,
                )
            )

        for index, value in enumerate(values):
            x, y = self._step_origin(index, origin_x, origin_y, step_width, step_height)
            rectangles.append(
                RasterRectangle(
                    x=x,
                    y=y,
                    width=step_width,
                    height=step_height,
                    color=value,
                )
            )

        return rectangles

    def _resolved_step_size(self) -> tuple[int, int]:
        if isinstance(self.step_size, tuple):
            if len(self.step_size) != 2:
                raise ValueError("step_size must be a positive integer or a 2-tuple of positive integers.")
            step_width, step_height = self.step_size
        else:
            step_width = self.step_size
            step_height = self.step_size

        validate_positive_int(step_width, "step_width")
        validate_positive_int(step_height, "step_height")
        return step_width, step_height

    def _resolved_values(self) -> list[int]:
        if self.values is None:
            ramp = np.linspace(0, 255, self.steps)
            return [int(round(value)) for value in ramp]

        if len(self.values) != self.steps:
            raise ValueError("values length must match steps.")

        resolved_values: list[int] = []
        for value in self.values:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError("values must contain integers in the range [0, 255].")
            if not 0 <= value <= 255:
                raise ValueError("values must contain integers in the range [0, 255].")
            resolved_values.append(value)
        return resolved_values

    def _chart_size(self, step_width: int, step_height: int) -> tuple[int, int]:
        if self.orientation == "horizontal":
            return (self.steps * step_width, step_height)
        return (step_width, self.steps * step_height)

    def _resolved_origin(self, step_width: int, step_height: int) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        chart_width, chart_height = self._chart_size(step_width, step_height)
        return (
            (self.canvas.width - chart_width) // 2,
            (self.canvas.height - chart_height) // 2,
        )

    def _step_origin(
        self,
        index: int,
        origin_x: int,
        origin_y: int,
        step_width: int,
        step_height: int,
    ) -> tuple[int, int]:
        if self.orientation == "horizontal":
            return (origin_x + index * step_width, origin_y)
        return (origin_x, origin_y + index * step_height)
