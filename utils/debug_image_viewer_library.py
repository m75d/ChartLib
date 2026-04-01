"""Small debug image viewer library.

This module is meant for practical image inspection during development and debugging.
It avoids Matplotlib and OpenCV windowing issues by relying on Pillow for display
and file saving, while keeping the code structured enough to grow into a small library.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Union
import tempfile
import time

import numpy as np
from PIL import Image

ArrayLike = np.ndarray
PathLike = Union[str, Path]


class DebugImageError(ValueError):
    """Raised when an image cannot be converted into a supported debug format."""


@dataclass(frozen=True)
class ImageStats:
    shape: tuple[int, ...]
    dtype: str
    min_value: float
    max_value: float

    def format(self, name: str = "img") -> str:
        return (
            f"{name}: shape={self.shape}, dtype={self.dtype}, "
            f"min={self.min_value:.4g}, max={self.max_value:.4g}"
        )


@dataclass(frozen=True)
class DebugImageResult:
    path: Path
    shown: bool
    stats: ImageStats


@dataclass(frozen=True)
class ViewerConfig:
    save_dir: Optional[PathLike] = None
    always_save: bool = True
    try_show: bool = True
    print_info: bool = True
    assume_bgr: bool = False


class DebugImageViewer:
    """Reusable debug image viewer.

    The class is intentionally small and conservative:
    - accepts numpy arrays in HxW, HxWx1, HxWx3, HxWx4 format
    - converts common dtypes into uint8 for viewing
    - optionally treats color inputs as BGR/BGRA
    - shows via Pillow and saves to disk
    """

    def __init__(self, config: Optional[ViewerConfig] = None) -> None:
        self.config = config or ViewerConfig()

    def show(
        self,
        img: ArrayLike,
        *,
        title: str = "debug_image",
        filename: Optional[str] = None,
        save_dir: Optional[PathLike] = None,
        assume_bgr: Optional[bool] = None,
        try_show: Optional[bool] = None,
        always_save: Optional[bool] = None,
        print_info: Optional[bool] = None,
    ) -> DebugImageResult:
        """Show and/or save an image for debugging.

        Returns a DebugImageResult containing the saved path, whether a display
        attempt succeeded, and image statistics.
        """
        actual_assume_bgr = self.config.assume_bgr if assume_bgr is None else assume_bgr
        actual_try_show = self.config.try_show if try_show is None else try_show
        actual_always_save = self.config.always_save if always_save is None else always_save
        actual_print_info = self.config.print_info if print_info is None else print_info

        stats = get_image_stats(img)
        if actual_print_info:
            print(stats.format(title))

        arr = _to_uint8_image_array(img, assume_bgr=actual_assume_bgr)
        pil_img = _to_pil_image(arr)

        target_dir = _resolve_save_dir(save_dir or self.config.save_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = _make_filename(title)

        save_path = target_dir / filename
        shown = False
        saved = False

        if actual_always_save or not actual_try_show:
            pil_img.save(save_path)
            saved = True

        if actual_try_show:
            try:
                pil_img.show(title=title)
                shown = True
            except Exception as exc:
                if actual_print_info:
                    print(f"PIL show failed: {exc}")
                if not saved:
                    pil_img.save(save_path)
                    saved = True

        if actual_print_info and saved:
            print(f"Saved debug image to: {save_path}")

        return DebugImageResult(path=save_path, shown=shown, stats=stats)

    def save(
        self,
        img: ArrayLike,
        *,
        title: str = "debug_image",
        filename: Optional[str] = None,
        save_dir: Optional[PathLike] = None,
        assume_bgr: Optional[bool] = None,
        print_info: Optional[bool] = None,
    ) -> DebugImageResult:
        """Save an image without trying to open an external viewer."""
        return self.show(
            img,
            title=title,
            filename=filename,
            save_dir=save_dir,
            assume_bgr=assume_bgr,
            try_show=False,
            always_save=True,
            print_info=print_info,
        )


def show_image(
    img: ArrayLike,
    *,
    title: str = "debug_image",
    filename: Optional[str] = None,
    save_dir: Optional[PathLike] = None,
    assume_bgr: bool = False,
    try_show: bool = True,
    always_save: bool = True,
    print_info: bool = True,
) -> DebugImageResult:
    """Convenience function for one-off use."""
    viewer = DebugImageViewer(
        ViewerConfig(
            save_dir=save_dir,
            always_save=always_save,
            try_show=try_show,
            print_info=print_info,
            assume_bgr=assume_bgr,
        )
    )
    return viewer.show(img, title=title, filename=filename)


def save_image(
    img: ArrayLike,
    *,
    title: str = "debug_image",
    filename: Optional[str] = None,
    save_dir: Optional[PathLike] = None,
    assume_bgr: bool = False,
    print_info: bool = True,
) -> DebugImageResult:
    """Convenience function for save-only behavior."""
    viewer = DebugImageViewer(
        ViewerConfig(
            save_dir=save_dir,
            always_save=True,
            try_show=False,
            print_info=print_info,
            assume_bgr=assume_bgr,
        )
    )
    return viewer.save(img, title=title, filename=filename)


def get_image_stats(img: ArrayLike) -> ImageStats:
    arr = np.asarray(img)
    if arr.size == 0:
        raise DebugImageError("Empty image array")

    if np.issubdtype(arr.dtype, np.floating):
        finite_mask = np.isfinite(arr)
        if not finite_mask.any():
            raise DebugImageError("Image contains no finite values")
        finite_vals = arr[finite_mask]
        min_val = float(finite_vals.min())
        max_val = float(finite_vals.max())
    else:
        min_val = float(arr.min())
        max_val = float(arr.max())

    return ImageStats(
        shape=tuple(arr.shape),
        dtype=str(arr.dtype),
        min_value=min_val,
        max_value=max_val,
    )


def _to_uint8_image_array(img: ArrayLike, *, assume_bgr: bool = False) -> np.ndarray:
    arr = np.asarray(img)

    if arr.ndim not in (2, 3):
        raise DebugImageError(f"Unsupported image shape: {arr.shape}")

    if arr.ndim == 3 and arr.shape[2] not in (1, 3, 4):
        raise DebugImageError(f"Unsupported image shape: {arr.shape}")

    if arr.ndim == 3 and arr.shape[2] == 1:
        arr = arr[:, :, 0]

    arr = _convert_dtype_to_uint8(arr)

    if assume_bgr and arr.ndim == 3 and arr.shape[2] >= 3:
        if arr.shape[2] == 3:
            arr = arr[:, :, ::-1]
        else:
            arr = arr[:, :, [2, 1, 0, 3]]

    return arr


def _convert_dtype_to_uint8(arr: np.ndarray) -> np.ndarray:
    if arr.dtype == np.uint8:
        return arr

    if np.issubdtype(arr.dtype, np.floating):
        finite_mask = np.isfinite(arr)
        if not finite_mask.any():
            raise DebugImageError("Image contains no finite values")

        finite_vals = arr[finite_mask]
        vmin = float(finite_vals.min())
        vmax = float(finite_vals.max())

        if 0.0 <= vmin and vmax <= 1.0:
            arr = arr * 255.0

        arr = np.nan_to_num(arr, nan=0.0, posinf=255.0, neginf=0.0)
        return np.clip(arr, 0.0, 255.0).astype(np.uint8)

    if arr.dtype == np.uint16:
        return (arr / 257.0).astype(np.uint8)

    if np.issubdtype(arr.dtype, np.integer):
        return np.clip(arr, 0, 255).astype(np.uint8)

    raise DebugImageError(f"Unsupported dtype: {arr.dtype}")


def _to_pil_image(arr: np.ndarray) -> Image.Image:
    if arr.ndim == 2:
        return Image.fromarray(arr, mode="L")
    if arr.ndim == 3 and arr.shape[2] == 3:
        return Image.fromarray(arr, mode="RGB")
    if arr.ndim == 3 and arr.shape[2] == 4:
        return Image.fromarray(arr, mode="RGBA")
    raise DebugImageError(f"Unsupported PIL conversion shape: {arr.shape}")


def _resolve_save_dir(save_dir: Optional[PathLike]) -> Path:
    if save_dir is None:
        return Path(tempfile.gettempdir()) / "python_debug_images"
    return Path(save_dir)


def _make_filename(title: str) -> str:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
    return f"{safe_title}_{timestamp}.png"


__all__: Sequence[str] = [
    "DebugImageError",
    "DebugImageResult",
    "DebugImageViewer",
    "ImageStats",
    "ViewerConfig",
    "get_image_stats",
    "save_image",
    "show_image",
]
