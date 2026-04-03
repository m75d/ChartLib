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
        top_band_y = margin_y
        support_y = margin_y + self._grayscale_height() + self._gutter() // 2

        dead_leaves_size = self._dead_leaves_size()
        color_patch_width, color_patch_height = self._color_patch_size()
        grayscale_width = self._grayscale_width()
        grayscale_height = self._grayscale_height()
        primary_edge_width = self._slanted_edge_width()
        primary_edge_height = self._slanted_edge_height()
        primary_star_size = self._primary_star_size()
        secondary_star_size = self._secondary_star_size()

        left_support_x = margin_x
        right_support_x = self.canvas.width - margin_x - color_patch_width
        grayscale_x = (self.canvas.width - grayscale_width) // 2
        left_edge_x = margin_x + self.canvas.width // 30
        right_edge_x = self.canvas.width - margin_x - primary_edge_width - self.canvas.width // 30
        primary_star_x = (self.canvas.width - primary_star_size) // 2
        secondary_star_x = (self.canvas.width - secondary_star_size) // 2
        primary_star_y = self.canvas.height - margin_y - primary_star_size
        left_edge_y = self.canvas.height - margin_y - primary_edge_height - self.canvas.height // 14
        right_edge_y = left_edge_y
        secondary_star_y = support_y + dead_leaves_size - secondary_star_size // 3

        grayscale_canvas = CanvasSpec(
            width=grayscale_width,
            height=grayscale_height,
            channels=1,
            background=230,
        )
        grayscale = GrayscaleStepChart(
            canvas=grayscale_canvas,
            steps=8,
            step_size=(
                max(1, (grayscale_width - 2 * self._inner_margin(grayscale_width, grayscale_height)) // 8),
                max(1, grayscale_height - 2 * self._inner_margin(grayscale_width, grayscale_height)),
            ),
            values=[0, 36, 72, 109, 146, 182, 219, 255],
            background_value=230,
        )

        color_patches = ColorPatchChart(
            canvas=CanvasSpec(
                width=color_patch_width,
                height=color_patch_height,
                channels=3,
                background=self._background_rgb(),
            ),
            rows=4,
            cols=6,
            patch_size=(
                color_patch_width // 6,
                color_patch_height // 4,
            ),
            colors=self._color_patch_palette(),
            labels=self._color_patch_labels(),
        )

        slanted_edge_0 = SlantedEdgeChart(
            canvas=CanvasSpec(width=primary_edge_width, height=primary_edge_height, channels=1, background=235),
            chart_size=(
                max(1, primary_edge_width - 2 * self._inner_margin(primary_edge_width, primary_edge_height)),
                max(1, primary_edge_height - 2 * self._inner_margin(primary_edge_width, primary_edge_height)),
            ),
            edge_angle_degrees=5.0,
            background_value=235,
        )
        slanted_edge_1 = SlantedEdgeChart(
            canvas=CanvasSpec(width=primary_edge_width, height=primary_edge_height, channels=1, background=235),
            chart_size=(
                max(1, primary_edge_width - 2 * self._inner_margin(primary_edge_width, primary_edge_height)),
                max(1, primary_edge_height - 2 * self._inner_margin(primary_edge_width, primary_edge_height)),
            ),
            edge_angle_degrees=-5.0,
            background_value=235,
        )

        dead_leaves = DeadLeavesPatchChart(
            canvas=CanvasSpec(width=dead_leaves_size, height=dead_leaves_size, channels=1, background=235),
            patch_size=(
                max(1, dead_leaves_size - 2 * self._inner_margin(dead_leaves_size, dead_leaves_size)),
                max(1, dead_leaves_size - 2 * self._inner_margin(dead_leaves_size, dead_leaves_size)),
            ),
            num_shapes=280,
            radius_range=(4, max(5, dead_leaves_size // 8)),
            value_range=(24, 232),
            background_value=24,
            seed=self.seed,
        )

        primary_star_radius = max(
            16,
            primary_star_size // 2 - self._inner_margin(primary_star_size, primary_star_size),
        )
        secondary_star_radius = max(
            16,
            secondary_star_size // 2 - self._inner_margin(secondary_star_size, secondary_star_size),
        )
        siemens_star_0 = SiemensStarChart(
            canvas=CanvasSpec(width=primary_star_size, height=primary_star_size, channels=1, background=235),
            outer_radius=primary_star_radius,
            num_sectors=32,
            inner_radius=max(0, primary_star_radius // 8),
            background_value=235,
        )
        siemens_star_1 = SiemensStarChart(
            canvas=CanvasSpec(width=secondary_star_size, height=secondary_star_size, channels=1, background=235),
            outer_radius=secondary_star_radius,
            num_sectors=24,
            inner_radius=max(0, secondary_star_radius // 10),
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
            PlacedChart(name="grayscale", chart=grayscale, origin=(grayscale_x, top_band_y)),
            PlacedChart(name="dead_leaves", chart=dead_leaves, origin=(left_support_x, support_y)),
            PlacedChart(
                name="color_patches",
                chart=color_patches,
                origin=(right_support_x, support_y + self.canvas.height // 36),
            ),
            PlacedChart(name="siemens_star_1", chart=siemens_star_1, origin=(secondary_star_x, secondary_star_y)),
            PlacedChart(name="slanted_edge_0", chart=slanted_edge_0, origin=(left_edge_x, left_edge_y)),
            PlacedChart(name="slanted_edge_1", chart=slanted_edge_1, origin=(right_edge_x, right_edge_y)),
            PlacedChart(name="siemens_star_0", chart=siemens_star_0, origin=(primary_star_x, primary_star_y)),
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

    def _dead_leaves_size(self) -> int:
        return max(220, min(self.canvas.width, self.canvas.height) * 3 // 8)

    def _color_patch_size(self) -> tuple[int, int]:
        patch_width = max(288, self.canvas.width // 4)
        patch_height = max(192, self.canvas.height // 4)
        patch_width -= patch_width % 6
        patch_height -= patch_height % 4
        return (patch_width, patch_height)

    def _grayscale_width(self) -> int:
        return max(240, self.canvas.width * 11 // 20)

    def _grayscale_height(self) -> int:
        return max(80, self.canvas.height // 8)

    def _slanted_edge_width(self) -> int:
        return max(180, self.canvas.width // 5)

    def _slanted_edge_height(self) -> int:
        return max(220, self.canvas.height * 7 // 20)

    def _primary_star_size(self) -> int:
        return max(200, min(self.canvas.width, self.canvas.height) // 3)

    def _secondary_star_size(self) -> int:
        return max(140, min(self.canvas.width, self.canvas.height) // 5)

    def _color_patch_palette(self) -> list[tuple[int, int, int]]:
        return [
            (16, 16, 16),
            (48, 48, 48),
            (96, 96, 96),
            (160, 160, 160),
            (224, 224, 224),
            (245, 245, 245),
            (160, 24, 32),
            (32, 128, 48),
            (24, 72, 176),
            (208, 176, 32),
            (176, 56, 152),
            (32, 160, 176),
            (96, 32, 24),
            (96, 80, 24),
            (40, 96, 40),
            (32, 96, 96),
            (48, 48, 112),
            (112, 48, 96),
            (214, 176, 140),
            (186, 138, 102),
            (224, 128, 48),
            (176, 96, 32),
            (112, 160, 208),
            (200, 208, 216),
        ]

    def _color_patch_labels(self) -> list[str]:
        return [
            "black",
            "dark_gray",
            "gray",
            "light_gray",
            "highlight_gray",
            "white",
            "deep_red",
            "green",
            "blue",
            "yellow",
            "magenta",
            "cyan",
            "brown",
            "olive",
            "dark_green",
            "teal",
            "navy",
            "purple",
            "skin_light",
            "skin_mid",
            "orange",
            "amber",
            "sky",
            "cool_gray",
        ]
