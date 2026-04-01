from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import CanvasSpec, GrayscaleStepChart


def test_grayscale_step_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=255)
    chart = GrayscaleStepChart(
        canvas=canvas,
        steps=4,
        step_size=(20, 10),
        origin=(10, 30),
    )

    image = chart.render()

    assert image.shape == (80, 120)


def test_grayscale_step_intensities_follow_expected_order() -> None:
    canvas = CanvasSpec(width=120, height=60, channels=1, background=255)
    chart = GrayscaleStepChart(
        canvas=canvas,
        steps=4,
        step_size=(20, 10),
        values=[0, 85, 170, 255],
        origin=(10, 20),
    )

    image = chart.render()

    assert image[25, 20] == 0
    assert image[25, 40] == 85
    assert image[25, 60] == 170
    assert image[25, 80] == 255


def test_grayscale_step_annotations_include_centers_and_regions(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=80, channels=1, background=255)
    chart = GrayscaleStepChart(
        canvas=canvas,
        steps=3,
        step_size=(30, 20),
        values=[10, 120, 240],
        origin=(15, 25),
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "grayscale-step.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (80, 160)
    assert output_path.exists()
    assert saved_annotations == annotations

    centers = annotations.landmarks["centers"]
    regions = annotations.regions["steps"]
    assert len(centers) == 3
    assert len(regions) == 3
    assert centers[0] == (30.0, 35.0)
    assert centers[-1] == (90.0, 35.0)
    assert regions[1] == {
        "index": 1,
        "value": 120,
        "x": 45,
        "y": 25,
        "width": 30,
        "height": 20,
    }


def test_grayscale_step_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=100, height=60, channels=1, background=255)
    chart = GrayscaleStepChart(
        canvas=canvas,
        steps=2,
        step_size=20,
        values=[0, 255],
    )

    image = chart.render()

    assert image[30, 40] == 0
    assert image[30, 60] == 255
    assert image[10, 10] == 255


def test_grayscale_step_raises_when_chart_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        GrayscaleStepChart(
            canvas=canvas,
            steps=3,
            step_size=(20, 20),
            origin=(0, 0),
        )


def test_grayscale_step_rejects_invalid_values_length() -> None:
    canvas = CanvasSpec(width=100, height=60, channels=1, background=255)

    with pytest.raises(ValueError, match="values length must match steps"):
        GrayscaleStepChart(
            canvas=canvas,
            steps=3,
            step_size=20,
            values=[0, 255],
        )


def test_grayscale_step_rejects_invalid_grayscale_values() -> None:
    canvas = CanvasSpec(width=100, height=60, channels=1, background=255)

    with pytest.raises(ValueError, match="values must contain integers in the range \\[0, 255\\]"):
        GrayscaleStepChart(
            canvas=canvas,
            steps=3,
            step_size=20,
            values=[0, 128, 300],
        )
