"""Slanted-edge chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import math
import numbers
import numpy as np

from chartlib.annotations import AnnotationBundle, line_region, rectangle_region
from chartlib.renderers.raster import render_slanted_edge_region
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class SlantedEdgeChart:
    """Render an ideal rectangular slanted-edge chart."""

    canvas: CanvasSpec
    chart_size: tuple[int, int]
    edge_angle_degrees: float = 5.0
    origin: tuple[int, int] | None = None
    dark_value: int = 0
    light_value: int = 255
    background_value: int | None = None

    def __post_init__(self) -> None:
        chart_width, chart_height = self._resolved_chart_size()
        validate_non_negative_int(self.dark_value, "dark_value")
        validate_non_negative_int(self.light_value, "light_value")

        if self.background_value is not None:
            validate_non_negative_int(self.background_value, "background_value")
            if self.background_value > 255:
                raise ValueError("background_value must be in the range [0, 255].")

        if self.dark_value > 255 or self.light_value > 255:
            raise ValueError("dark_value and light_value must be in the range [0, 255].")

        if not isinstance(self.edge_angle_degrees, numbers.Real) or isinstance(self.edge_angle_degrees, bool):
            raise ValueError("edge_angle_degrees must be a finite number.")
        if not math.isfinite(float(self.edge_angle_degrees)):
            raise ValueError("edge_angle_degrees must be a finite number.")

        origin_x, origin_y = self._resolved_origin(chart_width, chart_height)
        if origin_x + chart_width > self.canvas.width or origin_y + chart_height > self.canvas.height:
            raise ValueError("Slanted-edge chart does not fit inside the canvas.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        chart_width, chart_height = self._resolved_chart_size()
        origin_x, origin_y = self._resolved_origin(chart_width, chart_height)
        render_options = options or RenderOptions()
        image = render_slanted_edge_region(
            canvas=self.canvas,
            chart_x=origin_x,
            chart_y=origin_y,
            chart_width=chart_width,
            chart_height=chart_height,
            edge_angle_degrees=float(self.edge_angle_degrees),
            dark_value=self.dark_value,
            light_value=self.light_value,
            background_value=self.background_value,
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
        chart_width, chart_height = self._resolved_chart_size()
        origin_x, origin_y = self._resolved_origin(chart_width, chart_height)
        center_x = origin_x + chart_width / 2.0
        center_y = origin_y + chart_height / 2.0
        point_a, point_b = self._edge_segment(origin_x, origin_y, chart_width, chart_height)

        return AnnotationBundle(
            chart_type="slanted_edge",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={
                "edge_segment": [point_a, point_b],
                "edge_center": [(center_x, center_y)],
            },
            regions={
                "chart": [
                    rectangle_region(
                        "rectangle",
                        x=origin_x,
                        y=origin_y,
                        width=chart_width,
                        height=chart_height,
                    )
                ],
                "edge": [
                    line_region(
                        point_a[0],
                        point_a[1],
                        point_b[0],
                        point_b[1],
                        angle_degrees=float(self.edge_angle_degrees),
                    )
                ],
            },
        )

    def _resolved_chart_size(self) -> tuple[int, int]:
        if len(self.chart_size) != 2:
            raise ValueError("chart_size must be a 2-tuple of positive integers.")
        chart_width, chart_height = self.chart_size
        validate_positive_int(chart_width, "chart_width")
        validate_positive_int(chart_height, "chart_height")
        return chart_width, chart_height

    def _resolved_origin(self, chart_width: int, chart_height: int) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        return (
            (self.canvas.width - chart_width) // 2,
            (self.canvas.height - chart_height) // 2,
        )

    def _edge_segment(
        self,
        origin_x: int,
        origin_y: int,
        chart_width: int,
        chart_height: int,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        center_x = origin_x + chart_width / 2.0
        center_y = origin_y + chart_height / 2.0
        theta = math.radians(float(self.edge_angle_degrees))
        direction_x = math.sin(theta)
        direction_y = math.cos(theta)
        x_min = float(origin_x)
        x_max = float(origin_x + chart_width)
        y_min = float(origin_y)
        y_max = float(origin_y + chart_height)
        intersections: list[tuple[float, float]] = []

        if abs(direction_x) > 1e-12:
            for x_edge in (x_min, x_max):
                t = (x_edge - center_x) / direction_x
                y_edge = center_y + t * direction_y
                if y_min - 1e-9 <= y_edge <= y_max + 1e-9:
                    intersections.append((x_edge, y_edge))

        if abs(direction_y) > 1e-12:
            for y_edge in (y_min, y_max):
                t = (y_edge - center_y) / direction_y
                x_edge = center_x + t * direction_x
                if x_min - 1e-9 <= x_edge <= x_max + 1e-9:
                    intersections.append((x_edge, y_edge))

        unique: list[tuple[float, float]] = []
        for point in intersections:
            rounded = (round(point[0], 10), round(point[1], 10))
            if rounded not in {(round(p[0], 10), round(p[1], 10)) for p in unique}:
                unique.append(point)

        unique.sort(key=lambda point: (point[1], point[0]))
        if len(unique) < 2:
            raise ValueError("Could not resolve slanted-edge segment within chart bounds.")

        return unique[0], unique[-1]
