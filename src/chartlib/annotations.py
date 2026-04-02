"""Structured annotation outputs for chart rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias


RegionValue: TypeAlias = int | float | str | bool
LandmarkValue: TypeAlias = list[tuple[float, float]] | dict[str, object]
RegionGroupValue: TypeAlias = list[dict[str, object]] | dict[str, object]


@dataclass(frozen=True)
class RegionRecord:
    """Small helper for regular region-style annotation payloads."""

    type: str
    x: int | float
    y: int | float
    width: int | float
    height: int | float
    extras: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return a stable dictionary payload for AnnotationBundle.regions."""

        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            **self.extras,
        }


def rectangle_region(
    region_type: str,
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
    **extras: object,
) -> dict[str, object]:
    """Create a rectangle-like region payload with standard bounds fields."""

    return RegionRecord(
        type=region_type,
        x=x,
        y=y,
        width=width,
        height=height,
        extras=extras,
    ).to_dict()


def line_region(
    x0: int | float,
    y0: int | float,
    x1: int | float,
    y1: int | float,
    **extras: object,
) -> dict[str, object]:
    """Create a line-segment region payload with standard bounds fields."""

    return RegionRecord(
        type="line_segment",
        x=min(x0, x1),
        y=min(y0, y1),
        width=abs(x1 - x0),
        height=abs(y1 - y0),
        extras={
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            **extras,
        },
    ).to_dict()


@dataclass(frozen=True)
class AnnotationBundle:
    """Machine-friendly annotations returned by a chart render."""

    chart_type: str
    image_size: tuple[int, int]
    landmarks: dict[str, LandmarkValue] = field(default_factory=dict)
    regions: dict[str, RegionGroupValue] = field(default_factory=dict)
