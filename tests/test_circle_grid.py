from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import CanvasSpec, CircleGridChart


def test_circle_grid_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=255)
    chart = CircleGridChart(
        canvas=canvas,
        rows=2,
        cols=3,
        radius=8,
        spacing=24,
        origin=(10, 10),
    )

    image = chart.render()

    assert image.shape == (80, 120)


def test_circle_grid_basic_circle_placement_sanity() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = CircleGridChart(
        canvas=canvas,
        rows=2,
        cols=2,
        radius=6,
        spacing=(20, 24),
        origin=(10, 8),
    )

    image = chart.render()

    assert image[14, 16] == 0
    assert image[38, 36] == 0
    assert image[14, 26] == 255
    assert image[8, 10] == 255


def test_circle_grid_annotation_count_and_coordinate_sanity(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=140, height=120, channels=1, background=255)
    chart = CircleGridChart(
        canvas=canvas,
        rows=3,
        cols=4,
        radius=5,
        spacing=(18, 20),
        origin=(12, 16),
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "circle-grid.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (120, 140)
    assert output_path.exists()
    assert saved_annotations == annotations

    centers = annotations.landmarks["centers"]
    assert len(centers) == 12
    assert centers[0] == (17.0, 21.0)
    assert centers[-1] == (71.0, 61.0)


def test_circle_grid_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=80, height=60, channels=1, background=255)
    chart = CircleGridChart(
        canvas=canvas,
        rows=2,
        cols=2,
        radius=5,
        spacing=20,
    )

    image = chart.render()

    assert image[20, 25] == 0
    assert image[40, 45] == 0
    assert image[20, 15] == 255


def test_circle_grid_raises_when_chart_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        CircleGridChart(
            canvas=canvas,
            rows=3,
            cols=3,
            radius=8,
            spacing=18,
            origin=(0, 0),
        )
