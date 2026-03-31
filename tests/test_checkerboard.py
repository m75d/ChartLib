from __future__ import annotations

from pathlib import Path

import numpy as np

from calcharts import CanvasSpec, CheckerboardChart


def test_checkerboard_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=255)
    chart = CheckerboardChart(
        canvas=canvas,
        rows=4,
        cols=5,
        square_size=20,
        origin=(10, 0),
    )

    image = chart.render()

    assert image.shape == (80, 120)


def test_checkerboard_alternates_black_and_white() -> None:
    canvas = CanvasSpec(width=60, height=60, channels=1, background=255)
    chart = CheckerboardChart(
        canvas=canvas,
        rows=3,
        cols=3,
        square_size=20,
        origin=(0, 0),
    )

    image = chart.render()

    sampled = image[10::20, 10::20]
    expected = np.array(
        [
            [0, 255, 0],
            [255, 0, 255],
            [0, 255, 0],
        ],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(sampled, expected)


def test_checkerboard_annotation_count_and_sanity() -> None:
    canvas = CanvasSpec(width=140, height=120, channels=1, background=255)
    chart = CheckerboardChart(
        canvas=canvas,
        rows=4,
        cols=5,
        square_size=20,
        origin=(20, 10),
    )

    image, annotations = chart.render(return_annotations=True)
    output_dir = Path("tests") / "_artifacts"
    output_dir.mkdir(exist_ok=True)
    saved_annotations = chart.save(output_dir / "checkerboard.png", return_annotations=True)

    assert image.shape == (120, 140)
    assert saved_annotations == annotations

    corners = annotations.landmarks["inner_corners"]
    assert len(corners) == (4 - 1) * (5 - 1)
    assert corners[0] == (40.0, 30.0)
    assert corners[-1] == (100.0, 70.0)
