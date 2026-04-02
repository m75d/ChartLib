"""Color patch chart implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle, rectangle_region
from chartlib.renderers.raster import RasterRectangle, render_rectangles
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import normalize_color, validate_non_negative_int, validate_positive_int

_DEFAULT_PATCH_PALETTE: tuple[tuple[int, int, int], ...] = (
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 128, 128),
    (255, 128, 0),
    (128, 0, 255),
    (0, 128, 255),
)


@dataclass(frozen=True)
class ColorPatchChart:
    """Render an ideal axis-aligned RGB color patch grid."""

    canvas: CanvasSpec
    rows: int
    cols: int
    patch_size: tuple[int, int] | int
    colors: list[tuple[int, int, int]] | None = None
    origin: tuple[int, int] | None = None
    background_color: tuple[int, int, int] | None = None
    labels: list[str] | None = None

    def __post_init__(self) -> None:
        validate_positive_int(self.rows, "rows")
        validate_positive_int(self.cols, "cols")
        patch_width, patch_height = self._resolved_patch_size()

        if self.canvas.channels != 3:
            raise ValueError("ColorPatchChart requires an RGB canvas with channels=3.")

        if self.background_color is not None:
            normalize_color(self.background_color, 3, "background_color")

        self._resolved_colors()
        self._resolved_labels()

        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)
        chart_width, chart_height = self._chart_size(patch_width, patch_height)
        if origin_x + chart_width > self.canvas.width or origin_y + chart_height > self.canvas.height:
            raise ValueError("Color patch chart does not fit inside the canvas.")

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
        patch_width, patch_height = self._resolved_patch_size()
        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)
        colors = self._resolved_colors()
        labels = self._resolved_labels()
        centers: list[tuple[float, float]] = []
        patches: list[dict[str, object]] = []

        for index, color in enumerate(colors):
            x, y = self._patch_origin(index, origin_x, origin_y, patch_width, patch_height)
            centers.append((float(x + patch_width / 2), float(y + patch_height / 2)))
            patch_region = rectangle_region(
                "rectangle",
                x=x,
                y=y,
                width=patch_width,
                height=patch_height,
                index=index,
                color=color,
            )
            if labels is not None:
                patch_region["label"] = labels[index]
            patches.append(patch_region)

        return AnnotationBundle(
            chart_type="color_patch",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks={"centers": centers},
            regions={"patches": patches},
        )

    def _rectangles(self) -> list[RasterRectangle]:
        patch_width, patch_height = self._resolved_patch_size()
        origin_x, origin_y = self._resolved_origin(patch_width, patch_height)
        colors = self._resolved_colors()
        rectangles: list[RasterRectangle] = []

        if self.background_color is not None:
            chart_width, chart_height = self._chart_size(patch_width, patch_height)
            rectangles.append(
                RasterRectangle(
                    x=origin_x,
                    y=origin_y,
                    width=chart_width,
                    height=chart_height,
                    color=self.background_color,
                )
            )

        for index, color in enumerate(colors):
            x, y = self._patch_origin(index, origin_x, origin_y, patch_width, patch_height)
            rectangles.append(
                RasterRectangle(
                    x=x,
                    y=y,
                    width=patch_width,
                    height=patch_height,
                    color=color,
                )
            )

        return rectangles

    def _resolved_patch_size(self) -> tuple[int, int]:
        if isinstance(self.patch_size, tuple):
            if len(self.patch_size) != 2:
                raise ValueError("patch_size must be a positive integer or a 2-tuple of positive integers.")
            patch_width, patch_height = self.patch_size
        else:
            patch_width = self.patch_size
            patch_height = self.patch_size

        validate_positive_int(patch_width, "patch_width")
        validate_positive_int(patch_height, "patch_height")
        return patch_width, patch_height

    def _resolved_colors(self) -> list[tuple[int, int, int]]:
        count = self.rows * self.cols
        if self.colors is None:
            return [
                _DEFAULT_PATCH_PALETTE[index % len(_DEFAULT_PATCH_PALETTE)]
                for index in range(count)
            ]

        if len(self.colors) != count:
            raise ValueError("colors length must match rows * cols.")

        resolved: list[tuple[int, int, int]] = []
        for index, color in enumerate(self.colors):
            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("colors must contain RGB 3-tuples with integer values in the range [0, 255].")
            normalized = normalize_color(color, 3, f"colors[{index}]")
            resolved.append((normalized[0], normalized[1], normalized[2]))
        return resolved

    def _resolved_labels(self) -> list[str] | None:
        if self.labels is None:
            return None

        if len(self.labels) != self.rows * self.cols:
            raise ValueError("labels length must match rows * cols.")

        resolved: list[str] = []
        for index, label in enumerate(self.labels):
            if not isinstance(label, str):
                raise ValueError(f"labels[{index}] must be a string.")
            resolved.append(label)
        return resolved

    def _chart_size(self, patch_width: int, patch_height: int) -> tuple[int, int]:
        return (self.cols * patch_width, self.rows * patch_height)

    def _resolved_origin(self, patch_width: int, patch_height: int) -> tuple[int, int]:
        if self.origin is not None:
            origin_x, origin_y = self.origin
            validate_non_negative_int(origin_x, "origin[0]")
            validate_non_negative_int(origin_y, "origin[1]")
            return origin_x, origin_y

        chart_width, chart_height = self._chart_size(patch_width, patch_height)
        return (
            (self.canvas.width - chart_width) // 2,
            (self.canvas.height - chart_height) // 2,
        )

    def _patch_origin(
        self,
        index: int,
        origin_x: int,
        origin_y: int,
        patch_width: int,
        patch_height: int,
    ) -> tuple[int, int]:
        row = index // self.cols
        col = index % self.cols
        return (origin_x + col * patch_width, origin_y + row * patch_height)
