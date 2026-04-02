"""Small built-in presets composed from existing chart blocks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle
from chartlib.charts.composite import CompositeChart, PlacedChart
from chartlib.charts.color_patch import ColorPatchChart
from chartlib.charts.dead_leaves import DeadLeavesPatchChart
from chartlib.charts.grayscale import GrayscaleStepChart
from chartlib.charts.registration_marker import RegistrationMarkerChart
from chartlib.charts.siemens_star import SiemensStarChart
from chartlib.charts.slanted_edge import SlantedEdgeChart
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True)
class TE42LikePreset:
    """A small TE42-inspired composite preset built from existing chart blocks."""

    canvas: CanvasSpec
    background_value: int = 128
    seed: int = 0

    def __post_init__(self) -> None:
        if self.canvas.channels != 3:
            raise ValueError("TE42LikePreset requires an RGB canvas with channels=3.")

        validate_non_negative_int(self.background_value, "background_value")
        validate_non_negative_int(self.seed, "seed")
        if self.background_value > 255:
            raise ValueError("background_value must be in the range [0, 255].")

        cell_width, cell_height = self._cell_size()
        validate_positive_int(cell_width, "cell_width")
        validate_positive_int(cell_height, "cell_height")
        if cell_width < 120 or cell_height < 120:
            raise ValueError("Canvas is too small for the TE42-like preset layout.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        return self._composite_chart().render(return_annotations=return_annotations, options=options)

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
        return self._composite_chart().get_annotations()

    def _composite_chart(self) -> CompositeChart:
        return CompositeChart(
            canvas=self.canvas,
            elements=self._elements(),
            background_value=self._background_rgb(),
        )

    def _elements(self) -> list[PlacedChart]:
        margin_x, margin_y = self._outer_margin()
        gutter = self._gutter()
        cell_width, cell_height = self._cell_size()

        top_left_x = margin_x
        top_row_y = margin_y
        middle_x = margin_x + cell_width + gutter
        right_x = margin_x + 2 * (cell_width + gutter)
        bottom_row_y = margin_y + cell_height + gutter

        grayscale_width = 2 * cell_width + gutter
        grayscale_canvas = CanvasSpec(
            width=grayscale_width,
            height=cell_height,
            channels=1,
            background=230,
        )
        grayscale = GrayscaleStepChart(
            canvas=grayscale_canvas,
            steps=8,
            step_size=(max(1, (grayscale_width - 2 * self._inner_margin(cell_width, cell_height)) // 8), max(1, cell_height - 2 * self._inner_margin(cell_width, cell_height))),
            values=[0, 36, 72, 109, 146, 182, 219, 255],
            background_value=230,
        )

        color_patches = ColorPatchChart(
            canvas=CanvasSpec(width=cell_width, height=cell_height, channels=3, background=self._background_rgb()),
            rows=2,
            cols=3,
            patch_size=(
                max(1, (cell_width - 2 * self._inner_margin(cell_width, cell_height)) // 3),
                max(1, (cell_height - 2 * self._inner_margin(cell_width, cell_height)) // 2),
            ),
            labels=["black", "white", "red", "green", "blue", "gray"],
        )

        slanted_edge = SlantedEdgeChart(
            canvas=CanvasSpec(width=cell_width, height=cell_height, channels=1, background=235),
            chart_size=(
                max(1, cell_width - 2 * self._inner_margin(cell_width, cell_height)),
                max(1, cell_height - 2 * self._inner_margin(cell_width, cell_height)),
            ),
            edge_angle_degrees=5.0,
            background_value=235,
        )

        dead_leaves = DeadLeavesPatchChart(
            canvas=CanvasSpec(width=cell_width, height=cell_height, channels=1, background=235),
            patch_size=(
                max(1, cell_width - 2 * self._inner_margin(cell_width, cell_height)),
                max(1, cell_height - 2 * self._inner_margin(cell_width, cell_height)),
            ),
            num_shapes=200,
            radius_range=(4, max(5, min(cell_width, cell_height) // 8)),
            value_range=(24, 232),
            background_value=24,
            seed=self.seed,
        )

        star_radius = max(16, min(cell_width, cell_height) // 2 - self._inner_margin(cell_width, cell_height))
        siemens_star = SiemensStarChart(
            canvas=CanvasSpec(width=cell_width, height=cell_height, channels=1, background=235),
            outer_radius=star_radius,
            num_sectors=32,
            inner_radius=max(0, star_radius // 8),
            background_value=235,
        )

        marker_size = max(16, min(self.canvas.width, self.canvas.height) // 36)
        marker_offset = marker_size // 2 + min(margin_x, margin_y) // 2
        registration_markers = RegistrationMarkerChart(
            canvas=CanvasSpec(
                width=self.canvas.width,
                height=self.canvas.height,
                channels=1,
                background=self.background_value,
            ),
            marker_size=marker_size,
            marker_shape="cross",
            marker_positions=[
                (marker_offset, marker_offset),
                (self.canvas.width // 2, marker_offset),
                (self.canvas.width - marker_offset, marker_offset),
                (marker_offset, self.canvas.height // 2),
                (self.canvas.width - marker_offset, self.canvas.height // 2),
                (marker_offset, self.canvas.height - marker_offset),
                (self.canvas.width // 2, self.canvas.height - marker_offset),
                (self.canvas.width - marker_offset, self.canvas.height - marker_offset),
            ],
            origin=(0, 0),
            layout_size=(self.canvas.width, self.canvas.height),
        )

        return [
            PlacedChart(name="registration_markers", chart=registration_markers, origin=(0, 0)),
            PlacedChart(name="grayscale", chart=grayscale, origin=(top_left_x, top_row_y)),
            PlacedChart(name="color_patches", chart=color_patches, origin=(right_x, top_row_y)),
            PlacedChart(name="slanted_edge_0", chart=slanted_edge, origin=(top_left_x, bottom_row_y)),
            PlacedChart(name="dead_leaves", chart=dead_leaves, origin=(middle_x, bottom_row_y)),
            PlacedChart(name="siemens_star_0", chart=siemens_star, origin=(right_x, bottom_row_y)),
        ]

    def _background_rgb(self) -> tuple[int, int, int]:
        return (self.background_value, self.background_value, self.background_value)

    def _outer_margin(self) -> tuple[int, int]:
        return (
            max(24, self.canvas.width // 32),
            max(24, self.canvas.height // 24),
        )

    def _gutter(self) -> int:
        margin_x, margin_y = self._outer_margin()
        return max(16, min(margin_x, margin_y) // 2)

    def _cell_size(self) -> tuple[int, int]:
        margin_x, margin_y = self._outer_margin()
        gutter = self._gutter()
        usable_width = self.canvas.width - 2 * margin_x - 2 * gutter
        usable_height = self.canvas.height - 2 * margin_y - gutter
        return (usable_width // 3, usable_height // 2)

    def _inner_margin(self, cell_width: int, cell_height: int) -> int:
        return max(10, min(cell_width, cell_height) // 12)
