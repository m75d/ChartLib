"""Siemens star chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle, line_region, rectangle_region
from chartlib.renderers.raster import render_siemens_star
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class SiemensStarChart:
    """Render an ideal Siemens star with alternating angular sectors."""

    canvas: CanvasSpec
    outer_radius: int
    num_sectors: int
    center: tuple[int, int] | None = None
    inner_radius: int = 0
    dark_value: int = 0
    light_value: int = 255
    background_value: int | None = None

    def __post_init__(self) -> None:
        validate_positive_int(self.outer_radius, "outer_radius")
        validate_positive_int(self.num_sectors, "num_sectors")
        validate_non_negative_int(self.inner_radius, "inner_radius")
        validate_non_negative_int(self.dark_value, "dark_value")
        validate_non_negative_int(self.light_value, "light_value")

        if self.background_value is not None:
            validate_non_negative_int(self.background_value, "background_value")
            if self.background_value > 255:
                raise ValueError("background_value must be in the range [0, 255].")

        if self.dark_value > 255 or self.light_value > 255:
            raise ValueError("dark_value and light_value must be in the range [0, 255].")

        if self.inner_radius >= self.outer_radius:
            raise ValueError("inner_radius must be smaller than outer_radius.")

        center_x, center_y = self._resolved_center()
        if (
            center_x - self.outer_radius < 0
            or center_y - self.outer_radius < 0
            or center_x + self.outer_radius > self.canvas.width
            or center_y + self.outer_radius > self.canvas.height
        ):
            raise ValueError("Siemens star does not fit inside the canvas.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        center_x, center_y = self._resolved_center()
        render_options = options or RenderOptions()
        image = render_siemens_star(
            canvas=self.canvas,
            center_x=center_x,
            center_y=center_y,
            outer_radius=self.outer_radius,
            num_sectors=self.num_sectors,
            inner_radius=self.inner_radius,
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
        center_x, center_y = self._resolved_center()
        star_x = center_x - self.outer_radius
        star_y = center_y - self.outer_radius
        star_size = 2 * self.outer_radius

        return AnnotationBundle(
            chart_type="siemens_star",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={
                "center": [(float(center_x), float(center_y))],
                "boundary_ray": [
                    (float(center_x), float(center_y)),
                    (float(center_x + self.outer_radius), float(center_y)),
                ],
            },
            regions={
                "star": [
                    rectangle_region(
                        "circle_annulus",
                        x=star_x,
                        y=star_y,
                        width=star_size,
                        height=star_size,
                        center_x=center_x,
                        center_y=center_y,
                        outer_radius=self.outer_radius,
                        inner_radius=self.inner_radius,
                        num_sectors=self.num_sectors,
                        start_angle_degrees=0.0,
                    )
                ],
                "boundary_ray": [
                    line_region(
                        float(center_x),
                        float(center_y),
                        float(center_x + self.outer_radius),
                        float(center_y),
                        angle_degrees=0.0,
                    )
                ],
            },
        )

    def _resolved_center(self) -> tuple[int, int]:
        if self.center is not None:
            center_x, center_y = self.center
            validate_non_negative_int(center_x, "center[0]")
            validate_non_negative_int(center_y, "center[1]")
            return center_x, center_y

        return (
            self.canvas.width // 2,
            self.canvas.height // 2,
        )
