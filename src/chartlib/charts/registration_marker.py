"""Registration marker chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle, rectangle_region
from chartlib.renderers.raster import RasterRectangle, render_rectangles
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class RegistrationMarkerChart:
    """Render a deterministic grayscale registration-marker block."""

    canvas: CanvasSpec
    marker_size: int
    marker_positions: list[tuple[int, int]] | None = None
    marker_shape: str = "square"
    origin: tuple[int, int] | None = None
    layout_size: tuple[int, int] | None = None
    dark_value: int = 0
    light_value: int = 255
    background_value: int | None = None

    def __post_init__(self) -> None:
        validate_positive_int(self.marker_size, "marker_size")

        if self.canvas.channels != 1:
            raise ValueError("RegistrationMarkerChart requires a grayscale canvas with channels=1.")
        if self.marker_shape not in ("square", "cross"):
            raise ValueError("marker_shape must be 'square' or 'cross'.")
        validate_non_negative_int(self.dark_value, "dark_value")
        validate_non_negative_int(self.light_value, "light_value")
        if self.dark_value > 255 or self.light_value > 255:
            raise ValueError("dark_value and light_value must be in the range [0, 255].")
        if self.background_value is not None:
            validate_non_negative_int(self.background_value, "background_value")
            if self.background_value > 255:
                raise ValueError("background_value must be in the range [0, 255].")

        layout_width, layout_height = self._resolved_layout_size()
        origin_x, origin_y = self._resolved_origin(layout_width, layout_height)
        if origin_x + layout_width > self.canvas.width or origin_y + layout_height > self.canvas.height:
            raise ValueError("Registration marker layout does not fit inside the canvas.")

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
        layout_width, layout_height = self._resolved_layout_size()
        origin_x, origin_y = self._resolved_origin(layout_width, layout_height)
        centers = []
        regions = []

        for index, (local_x, local_y) in enumerate(self._resolved_marker_positions(layout_width, layout_height)):
            center_x = origin_x + local_x
            center_y = origin_y + local_y
            x, y, width, height = self._marker_bounds(center_x, center_y)
            centers.append((float(center_x), float(center_y)))
            regions.append(
                rectangle_region(
                    "rectangle",
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    index=index,
                    shape=self.marker_shape,
                    center_x=center_x,
                    center_y=center_y,
                )
            )

        return AnnotationBundle(
            chart_type="registration_marker",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={"centers": centers},
            regions={"markers": regions},
        )

    def _rectangles(self) -> list[RasterRectangle]:
        layout_width, layout_height = self._resolved_layout_size()
        origin_x, origin_y = self._resolved_origin(layout_width, layout_height)
        rectangles: list[RasterRectangle] = []

        if self.background_value is not None:
            rectangles.append(
                RasterRectangle(
                    x=origin_x,
                    y=origin_y,
                    width=layout_width,
                    height=layout_height,
                    color=self.background_value,
                )
            )

        for local_x, local_y in self._resolved_marker_positions(layout_width, layout_height):
            center_x = origin_x + local_x
            center_y = origin_y + local_y
            if self.marker_shape == "square":
                x, y, width, height = self._marker_bounds(center_x, center_y)
                rectangles.append(
                    RasterRectangle(
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        color=self.dark_value,
                    )
                )
            else:
                for rect in self._cross_rectangles(center_x, center_y):
                    rectangles.append(rect)

        return rectangles

    def _cross_rectangles(self, center_x: int, center_y: int) -> list[RasterRectangle]:
        thickness = self._cross_thickness()
        x, y, width, height = self._marker_bounds(center_x, center_y)
        horizontal_y = center_y - thickness // 2
        vertical_x = center_x - thickness // 2
        return [
            RasterRectangle(
                x=x,
                y=horizontal_y,
                width=width,
                height=thickness,
                color=self.dark_value,
            ),
            RasterRectangle(
                x=vertical_x,
                y=y,
                width=thickness,
                height=height,
                color=self.dark_value,
            ),
        ]

    def _cross_thickness(self) -> int:
        return max(1, self.marker_size // 4)

    def _marker_bounds(self, center_x: int, center_y: int) -> tuple[int, int, int, int]:
        x = center_x - self.marker_size // 2
        y = center_y - self.marker_size // 2
        return (x, y, self.marker_size, self.marker_size)

    def _resolved_origin(self, layout_width: int, layout_height: int) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        return (
            (self.canvas.width - layout_width) // 2,
            (self.canvas.height - layout_height) // 2,
        )

    def _resolved_layout_size(self) -> tuple[int, int]:
        if self.layout_size is not None:
            if len(self.layout_size) != 2:
                raise ValueError("layout_size must be a 2-tuple of positive integers.")
            layout_width, layout_height = self.layout_size
            validate_positive_int(layout_width, "layout_width")
            validate_positive_int(layout_height, "layout_height")
            self._resolved_marker_positions(layout_width, layout_height)
            return layout_width, layout_height

        default_width = 3 * self.marker_size
        default_height = 3 * self.marker_size
        if self.marker_positions is None:
            return (default_width, default_height)

        max_x = 0
        max_y = 0
        for center_x, center_y in self._resolved_marker_positions(default_width, default_height):
            x, y, width, height = self._marker_bounds(center_x, center_y)
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)
        return (max_x, max_y)

    def _resolved_marker_positions(self, layout_width: int, layout_height: int) -> list[tuple[int, int]]:
        if self.marker_positions is None:
            return self._default_marker_positions(layout_width, layout_height)

        resolved: list[tuple[int, int]] = []
        for index, position in enumerate(self.marker_positions):
            if not isinstance(position, tuple) or len(position) != 2:
                raise ValueError("marker_positions must contain 2-tuples of non-negative integers.")
            center_x, center_y = position
            validate_non_negative_int(center_x, f"marker_positions[{index}][0]")
            validate_non_negative_int(center_y, f"marker_positions[{index}][1]")
            x, y, width, height = self._marker_bounds(center_x, center_y)
            if x < 0 or y < 0 or x + width > layout_width or y + height > layout_height:
                raise ValueError("marker_positions must keep the full marker inside the layout bounds.")
            resolved.append((center_x, center_y))
        return resolved

    def _default_marker_positions(self, layout_width: int, layout_height: int) -> list[tuple[int, int]]:
        start_x = self.marker_size // 2
        start_y = self.marker_size // 2
        end_x = layout_width - (self.marker_size - self.marker_size // 2)
        end_y = layout_height - (self.marker_size - self.marker_size // 2)
        return [
            (start_x, start_y),
            (end_x, start_y),
            (start_x, end_y),
            (end_x, end_y),
        ]
