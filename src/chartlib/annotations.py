"""Structured annotation outputs for chart rendering."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnnotationBundle:
    """Machine-friendly annotations returned by a chart render."""

    chart_type: str
    image_size: tuple[int, int]
    landmarks: dict[str, list[tuple[float, float]]] = field(default_factory=dict)
    regions: dict[str, list[dict[str, object]]] = field(default_factory=dict)
