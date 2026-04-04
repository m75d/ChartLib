from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from chartlib import CanvasSpec, RegistrationMarkerChart


def test_registration_marker_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=90, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=10,
        marker_positions=[(10, 10), (30, 20)],
        origin=(10, 15),
        layout_size=(40, 30),
    )

    image = chart.render()

    assert image.shape == (90, 120)


def test_registration_marker_square_placement_sanity() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=8,
        marker_positions=[(10, 10)],
        origin=(20, 15),
        layout_size=(30, 30),
    )

    image = chart.render()

    assert image[25, 30] == 0
    assert image[15, 20] == 255


def test_registration_marker_cross_shape_sanity() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=8,
        marker_shape="cross",
        marker_positions=[(10, 10)],
        origin=(20, 15),
        layout_size=(30, 30),
    )

    image = chart.render()

    assert image[25, 30] == 0
    assert image[21, 26] == 255


def test_registration_marker_cross_supports_explicit_length_and_thickness() -> None:
    canvas = CanvasSpec(width=120, height=100, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=8,
        marker_shape="cross",
        cross_length=21,
        cross_thickness=3,
        marker_positions=[(20, 20)],
        origin=(10, 10),
        layout_size=(40, 40),
    )

    image, annotations = chart.render(return_annotations=True)

    assert image[30, 30] == 0
    assert image[30, 20] == 0
    assert image[20, 30] == 0
    assert image[26, 26] == 255
    assert annotations.regions["markers"][0]["width"] == 21
    assert annotations.regions["markers"][0]["height"] == 21
    assert annotations.regions["markers"][0]["cross_length"] == 21
    assert annotations.regions["markers"][0]["cross_thickness"] == 3


def test_registration_marker_corner_shape_sanity() -> None:
    canvas = CanvasSpec(width=120, height=100, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=8,
        marker_shape="corner",
        cross_length=21,
        cross_thickness=3,
        corner_orientation="top_left",
        marker_positions=[(20, 20)],
        origin=(10, 10),
        layout_size=(40, 40),
    )

    image, annotations = chart.render(return_annotations=True)

    assert image[20, 20] == 0
    assert image[30, 20] == 0
    assert image[20, 30] == 0
    assert image[30, 30] == 255
    assert annotations.regions["markers"][0]["shape"] == "corner"
    assert annotations.regions["markers"][0]["corner_orientation"] == "top_left"
    assert annotations.regions["markers"][0]["cross_length"] == 21
    assert annotations.regions["markers"][0]["cross_thickness"] == 3


def test_registration_marker_corner_orientation_changes_quadrant() -> None:
    canvas = CanvasSpec(width=120, height=100, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=8,
        marker_shape="corner",
        cross_length=21,
        cross_thickness=3,
        corner_orientation="bottom_right",
        marker_positions=[(20, 20)],
        origin=(10, 10),
        layout_size=(40, 40),
    )

    image = chart.render()

    assert image[40, 40] == 0
    assert image[30, 40] == 0
    assert image[40, 30] == 0
    assert image[30, 30] == 255


def test_registration_marker_quadrant_circle_shape_sanity() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=128)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=20,
        marker_shape="quadrant_circle",
        marker_positions=[(20, 20)],
        origin=(10, 10),
        layout_size=(40, 40),
        dark_value=0,
        light_value=255,
    )

    image, annotations = chart.render(return_annotations=True)

    assert image[26, 26] == 0
    assert image[26, 34] == 255
    assert image[34, 26] == 255
    assert image[34, 34] == 0
    assert image[30, 19] == 128
    assert annotations.regions["markers"][0]["shape"] == "quadrant_circle"
    assert annotations.regions["markers"][0]["width"] == 20
    assert annotations.regions["markers"][0]["height"] == 20


def test_registration_marker_annotations_and_save(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=120, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=10,
        marker_shape="square",
        marker_positions=[(10, 10), (30, 20), (45, 35)],
        origin=(15, 25),
        layout_size=(60, 50),
        background_value=240,
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "registration-marker.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (120, 160)
    assert output_path.exists()
    assert saved_annotations == annotations
    assert len(annotations.landmarks["centers"]) == 3
    assert annotations.landmarks["centers"][0] == (25.0, 35.0)
    assert annotations.regions["markers"][1] == {
        "type": "rectangle",
        "x": 40,
        "y": 40,
        "width": 10,
        "height": 10,
        "index": 1,
        "shape": "square",
        "center_x": 45,
        "center_y": 45,
    }


def test_registration_marker_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=10,
        marker_positions=[(5, 5), (25, 25)],
        layout_size=(30, 30),
    )

    image = chart.render()

    assert tuple(chart.get_annotations().landmarks["centers"][0]) == (40.0, 30.0)
    assert image[30, 40] == 0


def test_registration_marker_raises_when_layout_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        RegistrationMarkerChart(
            canvas=canvas,
            marker_size=10,
            layout_size=(50, 20),
        )


def test_registration_marker_rejects_non_grayscale_canvas() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=3, background=(255, 255, 255))

    with pytest.raises(ValueError, match="requires a grayscale canvas"):
        RegistrationMarkerChart(
            canvas=canvas,
            marker_size=10,
        )


def test_registration_marker_rejects_unsupported_shape() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="marker_shape must be 'square', 'cross', 'quadrant_circle', or 'corner'"):
        RegistrationMarkerChart(
            canvas=canvas,
            marker_size=10,
            marker_shape="circle",
        )


def test_registration_marker_rejects_cross_thickness_larger_than_length() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="cross_thickness must not exceed cross_length"):
        RegistrationMarkerChart(
            canvas=canvas,
            marker_size=10,
            marker_shape="cross",
            cross_length=5,
            cross_thickness=6,
        )


def test_registration_marker_rejects_invalid_corner_orientation() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(
        ValueError,
        match="corner_orientation must be 'top_left', 'top_right', 'bottom_left', or 'bottom_right'",
    ):
        RegistrationMarkerChart(
            canvas=canvas,
            marker_size=10,
            marker_shape="corner",
            corner_orientation="left_top",
        )


def test_registration_marker_default_layout_is_deterministic() -> None:
    canvas = CanvasSpec(width=100, height=100, channels=1, background=255)
    chart_a = RegistrationMarkerChart(canvas=canvas, marker_size=10)
    chart_b = RegistrationMarkerChart(canvas=canvas, marker_size=10)

    np.testing.assert_array_equal(chart_a.render(), chart_b.render())
    assert chart_a.get_annotations() == chart_b.get_annotations()


def test_registration_marker_quadrant_circle_default_layout_is_deterministic() -> None:
    canvas = CanvasSpec(width=100, height=100, channels=1, background=200)
    chart_a = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=12,
        marker_shape="quadrant_circle",
        dark_value=0,
        light_value=255,
    )
    chart_b = RegistrationMarkerChart(
        canvas=canvas,
        marker_size=12,
        marker_shape="quadrant_circle",
        dark_value=0,
        light_value=255,
    )

    np.testing.assert_array_equal(chart_a.render(), chart_b.render())
    assert chart_a.get_annotations() == chart_b.get_annotations()
