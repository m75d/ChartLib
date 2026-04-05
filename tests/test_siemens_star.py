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
        "type": "circle_annulus",
        "x": 50,
        "y": 30,
        "width": 60,
        "height": 60,
        "center_x": 80,
        "center_y": 60,
        "outer_radius": 30,
        "inner_radius": 10,
        "num_sectors": 12,
        "start_angle_degrees": 0.0,
        "sweep_angle_degrees": 360.0,
    }
    assert annotations.regions["boundary_ray"][0] == {
        "type": "line_segment",
        "x": 80.0,
        "y": 60.0,
        "width": 30.0,
        "height": 0.0,
        "x0": 80.0,
        "y0": 60.0,
        "x1": 110.0,
        "y1": 60.0,
        "angle_degrees": 0.0,
    }
    assert image[60, 80] == 180


def test_siemens_star_can_render_partial_sector_span() -> None:
    canvas = CanvasSpec(width=140, height=140, channels=1, background=200)
    chart = SiemensStarChart(
        canvas=canvas,
        outer_radius=40,
        num_sectors=8,
        center=(70, 70),
        start_angle_degrees=0.0,
        sweep_angle_degrees=180.0,
    )

    image, annotations = chart.render(return_annotations=True)

    x_right, y_right = _sample_point((70, 70), 20, 10.0)
    x_upper_left, y_upper_left = _sample_point((70, 70), 20, 135.0)
    x_left, y_left = _sample_point((70, 70), 20, 190.0)

    assert image[y_right, x_right] == 0
    assert image[y_upper_left, x_upper_left] == 255
    assert image[y_left, x_left] == 200
    assert annotations.regions["star"][0]["start_angle_degrees"] == 0.0
    assert annotations.regions["star"][0]["sweep_angle_degrees"] == 180.0
    assert annotations.regions["boundary_ray"][0]["angle_degrees"] == 0.0


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

    with pytest.raises(ValueError, match="sweep_angle_degrees must be in the range \\(0, 360\\]"):
        SiemensStarChart(
            canvas=canvas,
            outer_radius=20,
            num_sectors=8,
            sweep_angle_degrees=0.0,
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
