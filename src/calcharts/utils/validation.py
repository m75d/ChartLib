"""Shared validation and normalization helpers."""

from __future__ import annotations


def validate_positive_int(value: int, name: str) -> None:
    """Require a strictly positive integer."""

    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def validate_non_negative_int(value: int, name: str) -> None:
    """Require a non-negative integer."""

    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer.")


def validate_channels(channels: int) -> None:
    """Restrict V1 rendering to grayscale or RGB canvases."""

    if channels not in (1, 3):
        raise ValueError("channels must be 1 for grayscale or 3 for RGB.")


def normalize_color(
    value: int | float | tuple[int | float, ...],
    channels: int,
    name: str,
) -> tuple[int, ...]:
    """Normalize scalar or tuple color values into uint8 channel tuples."""

    if channels == 1:
        if isinstance(value, tuple):
            if len(value) != 1:
                raise ValueError(f"{name} must be a scalar or a 1-tuple for grayscale.")
            return (_normalize_channel(value[0], name),)
        return (_normalize_channel(value, name),)

    if not isinstance(value, tuple) or len(value) != channels:
        raise ValueError(f"{name} must be a {channels}-tuple for RGB canvases.")

    return tuple(_normalize_channel(channel, name) for channel in value)


def _normalize_channel(value: int | float, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must not be boolean.")

    if isinstance(value, int):
        if not 0 <= value <= 255:
            raise ValueError(f"{name} integer values must be in the range [0, 255].")
        return value

    if isinstance(value, float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} float values must be in the range [0.0, 1.0].")
        return int(round(value * 255))

    raise ValueError(f"{name} must be an int, float, or tuple of channel values.")

