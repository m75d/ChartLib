from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from calcharts import CanvasSpec, CheckerboardChart, RenderOptions


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


def test_checkerboard_annotation_count_and_sanity(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=140, height=120, channels=1, background=255)
    chart = CheckerboardChart(
        canvas=canvas,
        rows=4,
        cols=5,
        square_size=20,
        origin=(20, 10),
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "checkerboard.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (120, 140)
    assert output_path.exists()
    assert saved_annotations == annotations

    corners = annotations.landmarks["inner_corners"]
    assert len(corners) == (4 - 1) * (5 - 1)
    assert corners[0] == (40.0, 30.0)
    assert corners[-1] == (100.0, 70.0)


def test_checkerboard_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=160, height=120, channels=1, background=255)
    chart = CheckerboardChart(
        canvas=canvas,
        rows=2,
        cols=3,
        square_size=20,
    )

    image = chart.render()

    assert image[40, 50] == 0
    assert image[40, 110] == 255
    assert image[20, 20] == 255


def test_checkerboard_raises_when_chart_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=70, height=70, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        CheckerboardChart(
            canvas=canvas,
            rows=4,
            cols=4,
            square_size=20,
            origin=(0, 0),
        )


def test_render_options_rejects_non_uint8_dtype() -> None:
    with pytest.raises(ValueError, match="supports only numpy.uint8"):
        RenderOptions(dtype=np.float32)
