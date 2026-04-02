"""Dead-leaves patch chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle, rectangle_region
from chartlib.renderers.raster import RasterCircle, render_circles_in_rectangle
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class DeadLeavesPatchChart:
    """Render a deterministic grayscale dead-leaves texture block."""

    canvas: CanvasSpec
    patch_size: tuple[int, int]
    origin: tuple[int, int] | None = None
    num_shapes: int = 200
    radius_range: tuple[int, int] = (3, 20)
    value_range: tuple[int, int] = (0, 255)
    background_value: int | None = None
    seed: int = 0

    def __post_init__(self) -> None:
        patch_width, patch_height = self._resolved_patch_size()
        validate_positive_int(self.num_shapes, "num_shapes")

        if self.canvas.channels != 1:
            raise ValueError("DeadLeavesPatchChart requires a grayscale canvas with channels=1.")

        radius_min, radius_max = self._resolved_radius_range()
        value_min, value_max = self._resolved_value_range()
        self._resolved_seed()

        if self.background_value is not None:
            validate_non_negative_int(self.background_value, "background_value")
            if self.background_value > 255:
                raise ValueError("background_value must be in the range [0, 255].")

        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)
        if origin_x + patch_width > self.canvas.width or origin_y + patch_height > self.canvas.height:
            raise ValueError("Dead-leaves patch does not fit inside the canvas.")

        if radius_min > min(patch_width, patch_height):
            raise ValueError("radius_range minimum must not exceed the patch dimensions.")

        # Force validation results to be resolved during construction.
        _ = value_min, value_max, radius_min, radius_max

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        patch_width, patch_height = self._resolved_patch_size()
        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)
        render_options = options or RenderOptions()
        image = render_circles_in_rectangle(
            canvas=self.canvas,
            rect_x=origin_x,
            rect_y=origin_y,
            rect_width=patch_width,
            rect_height=patch_height,
            circles=self._circles(origin_x, origin_y, patch_width, patch_height),
            background_value=self._resolved_background_value(),
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
        patch_width, patch_height = self._resolved_patch_size()
        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)

        return AnnotationBundle(
            chart_type="dead_leaves_patch",
            image_size=(self.canvas.width, self.canvas.height),
            regions={
                "patch": [
                    rectangle_region(
                        "rectangle",
                        x=origin_x,
                        y=origin_y,
                        width=patch_width,
                        height=patch_height,
                        num_shapes=self.num_shapes,
                        radius_range=self._resolved_radius_range(),
                        value_range=self._resolved_value_range(),
                        seed=self.seed,
                        background_value=self._resolved_background_value(),
                    )
                ]
            },
        )

    def _circles(
        self,
        origin_x: int,
        origin_y: int,
        patch_width: int,
        patch_height: int,
    ) -> list[RasterCircle]:
        radius_min, radius_max = self._resolved_radius_range()
        value_min, value_max = self._resolved_value_range()
        rng = np.random.default_rng(self._resolved_seed())
        circles: list[RasterCircle] = []

        for _ in range(self.num_shapes):
            radius = int(rng.integers(radius_min, radius_max + 1))
            center_x = int(origin_x + rng.integers(0, patch_width))
            center_y = int(origin_y + rng.integers(0, patch_height))
            value = int(rng.integers(value_min, value_max + 1))
            circles.append(
                RasterCircle(
                    center_x=center_x,
                    center_y=center_y,
                    radius=radius,
                    color=value,
                )
            )

        return circles

    def _resolved_patch_size(self) -> tuple[int, int]:
        if len(self.patch_size) != 2:
            raise ValueError("patch_size must be a 2-tuple of positive integers.")
        patch_width, patch_height = self.patch_size
        validate_positive_int(patch_width, "patch_width")
        validate_positive_int(patch_height, "patch_height")
        return patch_width, patch_height

    def _resolved_origin(self, patch_width: int, patch_height: int) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        return (
            (self.canvas.width - patch_width) // 2,
            (self.canvas.height - patch_height) // 2,
        )

    def _resolved_radius_range(self) -> tuple[int, int]:
        if len(self.radius_range) != 2:
            raise ValueError("radius_range must be a 2-tuple of positive integers.")
        radius_min, radius_max = self.radius_range
        validate_positive_int(radius_min, "radius_range[0]")
        validate_positive_int(radius_max, "radius_range[1]")
        if radius_min > radius_max:
            raise ValueError("radius_range minimum must be less than or equal to the maximum.")
        return radius_min, radius_max

    def _resolved_value_range(self) -> tuple[int, int]:
        if len(self.value_range) != 2:
            raise ValueError("value_range must be a 2-tuple of integers in the range [0, 255].")
        value_min, value_max = self.value_range
        if not isinstance(value_min, int) or isinstance(value_min, bool) or not isinstance(value_max, int) or isinstance(value_max, bool):
            raise ValueError("value_range must be a 2-tuple of integers in the range [0, 255].")
        if not 0 <= value_min <= 255 or not 0 <= value_max <= 255:
            raise ValueError("value_range must be a 2-tuple of integers in the range [0, 255].")
        if value_min > value_max:
            raise ValueError("value_range minimum must be less than or equal to the maximum.")
        return value_min, value_max

    def _resolved_background_value(self) -> int:
        if self.background_value is not None:
            return self.background_value
        return self._resolved_value_range()[0]

    def _resolved_seed(self) -> int:
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer.")
        return self.seed
