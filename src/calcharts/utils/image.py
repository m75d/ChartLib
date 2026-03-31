"""Image output helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def save_png(image: np.ndarray, path: str | Path) -> None:
    """Save an image array as a PNG file."""

    output_path = Path(path)
    image_to_save = np.asarray(image, dtype=np.uint8)
    Image.fromarray(image_to_save).save(output_path, format="PNG")

