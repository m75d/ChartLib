"""User-facing specifications for canvas and rendering."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from chartlib.utils.validation import (
    normalize_color,
    validate_channels,
    validate_positive_int,
)


@dataclass(frozen=True)
class CanvasSpec:
    """Output image specification."""

    width: int
    height: int
    channels: int = 1
    background: int | float | tuple[int | float, ...] = 255

    def __post_init__(self) -> None:
        validate_positive_int(self.width, "width")
        validate_positive_int(self.height, "height")
        validate_channels(self.channels)
        normalize_color(self.background, self.channels, "background")


@dataclass(frozen=True)
class RenderOptions:
    """Rendering policy for V1 8-bit raster output."""

    dtype: type = np.uint8

    def __post_init__(self) -> None:
        if self.dtype is not np.uint8:
            raise ValueError("RenderOptions.dtype currently supports only numpy.uint8 in V1.")
