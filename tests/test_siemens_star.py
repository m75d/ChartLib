from __future__ import annotations

from math import cos, radians, sin
from pathlib import Path

import pytest

from chartlib import CanvasSpec, SiemensStarChart


def _sample_point(center: tuple[int, int], radius: int, angle_degrees: float) -> tuple[int, int]:
    angle = radians(angle_degrees)
    x = int(round(center[0] + radius * cos(angle)))
    y = int(round(center[1] - radius * sin(angle)))
    return x, y


def test_siemens_star_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=100, channels=1, background=200)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=30,
        num_sectors=8,
        center=(60, 50),
    )

    image = chart.render()

    assert image.shape == (100, 120)


def test_siemens_star_alternating_sector_intensities() -> None:
    canvas = CanvasSpec(width=140, height=140, channels=1, background=200)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=40,
        num_sectors=8,
        center=(70, 70),
    )

    image = chart.render()

    x0, y0 = _sample_point((70, 70), 20, 10.0)
    x1, y1 = _sample_point((70, 70), 20, 50.0)
    x2, y2 = _sample_point((70, 70), 20, 100.0)

    assert image[y0, x0] == 0
    assert image[y1, x1] == 255
    assert image[y2, x2] == 0
    assert image[10, 10] == 200


def test_siemens_star_annotations_and_save(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=120, channels=1, background=255)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=30,
        inner_radius=10,
        num_sectors=12,
        center=(80, 60),
        background_value=180,
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "siemens-star.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (120, 160)
    assert output_path.exists()
    assert saved_annotations == annotations
    assert annotations.landmarks["center"] == [(80.0, 60.0)]
    assert annotations.landmarks["boundary_ray"] == [(80.0, 60.0), (110.0, 60.0)]
    assert annotations.regions["star"][0] == {
        "center_x": 80,
        "center_y": 60,
        "outer_radius": 30,
        "inner_radius": 10,
        "num_sectors": 12,
        "start_angle_degrees": 0.0,
    }
    assert image[60, 80] == 180


def test_siemens_star_uses_centered_placement_by_default() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=20,
        num_sectors=8,
    )

    image = chart.render()
    sample_x, sample_y = _sample_point((50, 40), 12, 10.0)

    assert chart.get_annotations().landmarks["center"] == [(50.0, 40.0)]
    assert image[sample_y, sample_x] == 0


def test_siemens_star_raises_when_star_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        SiemensStarChart(
            canvas=canvas,
            outer_radius=25,
            num_sectors=8,
            center=(20, 20),
        )


def test_siemens_star_rejects_invalid_radius_and_sector_values() -> None:
    canvas = CanvasSpec(width=120, height=120, channels=1, background=255)

    with pytest.raises(ValueError, match="inner_radius must be smaller than outer_radius"):
        SiemensStarChart(
            canvas=canvas,
            outer_radius=20,
            inner_radius=20,
            num_sectors=8,
        )

    with pytest.raises(ValueError, match="num_sectors must be a positive integer"):
        SiemensStarChart(
            canvas=canvas,
            outer_radius=20,
            num_sectors=0,
        )


def test_siemens_star_uses_documented_angular_convention() -> None:
    canvas = CanvasSpec(width=140, height=140, channels=1, background=255)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=40,
        num_sectors=4,
        center=(70, 70),
    )

    image = chart.render()
    x_right, y_right = _sample_point((70, 70), 20, 10.0)
    x_upper_left, y_upper_left = _sample_point((70, 70), 20, 135.0)

    assert image[y_right, x_right] == 0
    assert image[y_upper_left, x_upper_left] == 255
