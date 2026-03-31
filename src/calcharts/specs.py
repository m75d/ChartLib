"""User-facing specifications for canvas and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from calcharts.utils.validation import (
    normalize_color,
    validate_channels,
    validate_positive_int,
)

if TYPE_CHECKING:
    from typing import Any


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
    """Rendering policy for array creation and file output."""

    dtype: type[Any] = np.uint8
