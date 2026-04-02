"""Composite chart/layout implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chartlib.annotations import AnnotationBundle
from chartlib.specs import CanvasSpec, RenderOptions
from chartlib.utils.image import save_png
from chartlib.utils.validation import normalize_color, validate_non_negative_int


@dataclass(frozen=True)
class PlacedChart:
    """A child chart placed on a composite canvas."""

    chart: object
    origin: tuple[int, int]
    name: str | None = None

    def __post_init__(self) -> None:
        origin_x, origin_y = self.origin
        validate_non_negative_int(origin_x, "origin[0]")
        validate_non_negative_int(origin_y, "origin[1]")
        if self.name is not None and not self.name:
            raise ValueError("name must be a non-empty string when provided.")


@dataclass(frozen=True)
class CompositeChart:
    """Render multiple chart blocks onto a single composite canvas."""

    canvas: CanvasSpec
    elements: list[PlacedChart]
    background_value: int | tuple[int, int, int] | None = None

    def __post_init__(self) -> None:
        if self.background_value is not None:
            normalize_color(self.background_value, self.canvas.channels, "background_value")

        seen_names: set[str] = set()
        for index, element in enumerate(self.elements):
            name = self._element_name(index, element)
            if name in seen_names:
                raise ValueError("CompositeChart element names must be unique.")
            seen_names.add(name)

            child_canvas = self._child_canvas(element.chart)
            if child_canvas.channels != self.canvas.channels:
                raise ValueError("All placed charts must use the same channel count as the composite canvas.")

            origin_x, origin_y = element.origin
            if origin_x + child_canvas.width > self.canvas.width or origin_y + child_canvas.height > self.canvas.height:
                raise ValueError("Placed chart does not fit inside the composite canvas.")

    def render(
        self,
        return_annotations: bool = False,
        options: RenderOptions | None = None,
    ) -> np.ndarray | tuple[np.ndarray, AnnotationBundle]:
        render_options = options or RenderOptions()
        background = normalize_color(
            self.canvas.background if self.background_value is None else self.background_value,
            self.canvas.channels,
            "background_value",
        )
        dtype = render_options.dtype

        if self.canvas.channels == 1:
            image = np.full((self.canvas.height, self.canvas.width), background[0], dtype=dtype)
        else:
            image = np.full((self.canvas.height, self.canvas.width, self.canvas.channels), background, dtype=dtype)

        for element in self.elements:
            child_image = element.chart.render(options=render_options)
            origin_x, origin_y = element.origin
            child_canvas = self._child_canvas(element.chart)
            image[
                origin_y:origin_y + child_canvas.height,
                origin_x:origin_x + child_canvas.width,
            ] = child_image

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
        landmarks: dict[str, dict[str, object]] = {}
        regions: dict[str, dict[str, object]] = {}

        for index, element in enumerate(self.elements):
            name = self._element_name(index, element)
            annotations = element.chart.get_annotations()
            dx, dy = element.origin
            landmarks[name] = self._translate_landmarks(annotations.landmarks, dx, dy)
            regions[name] = self._translate_regions(annotations.regions, dx, dy)

        return AnnotationBundle(
            chart_type="composite",
            image_size=(self.canvas.width, self.canvas.height),
            landmarks=landmarks,
            regions=regions,
        )

    def _element_name(self, index: int, element: PlacedChart) -> str:
        if element.name is not None:
            return element.name
        return f"element_{index}"

    def _child_canvas(self, chart: object) -> CanvasSpec:
        child_canvas = getattr(chart, "canvas", None)
        if not isinstance(child_canvas, CanvasSpec):
            raise ValueError("Placed charts must expose a CanvasSpec via the 'canvas' attribute.")
        return child_canvas

    def _translate_landmarks(
        self,
        landmarks: dict[str, object],
        dx: int,
        dy: int,
    ) -> dict[str, object]:
        translated: dict[str, object] = {}
        for key, points in landmarks.items():
            if isinstance(points, list):
                translated[key] = [(float(x + dx), float(y + dy)) for x, y in points]
            else:
                translated[key] = points
        return translated

    def _translate_regions(
        self,
        regions: dict[str, object],
        dx: int,
        dy: int,
    ) -> dict[str, object]:
        translated: dict[str, object] = {}
        for key, entries in regions.items():
            if isinstance(entries, list):
                translated[key] = [self._translate_region_entry(entry, dx, dy) for entry in entries]
            else:
                translated[key] = entries
        return translated

    def _translate_region_entry(self, entry: dict[str, object], dx: int, dy: int) -> dict[str, object]:
        translated: dict[str, object] = {}
        for key, value in entry.items():
            if key in {"x", "center_x", "x0", "x1"} and isinstance(value, (int, float)):
                translated[key] = value + dx
            elif key in {"y", "center_y", "y0", "y1"} and isinstance(value, (int, float)):
                translated[key] = value + dy
            else:
                translated[key] = value
        return translated
