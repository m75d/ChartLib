from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import CanvasSpec, CheckerboardChart, CompositeChart, GrayscaleStepChart, PlacedChart, RegistrationMarkerChart


def test_composite_output_image_shape() -> None:
    composite_canvas = CanvasSpec(width=140, height=100, channels=1, background=200)
    checkerboard = CheckerboardChart(canvas=CanvasSpec(width=40, height=40, channels=1, background=255), rows=2, cols=2, square_size=20, origin=(0, 0))
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[PlacedChart(name="checker", chart=checkerboard, origin=(10, 15))],
    )

    image = chart.render()

    assert image.shape == (100, 140)


def test_composite_places_multiple_child_chart_types() -> None:
    composite_canvas = CanvasSpec(width=160, height=120, channels=1, background=255)
    checkerboard = CheckerboardChart(canvas=CanvasSpec(width=40, height=40, channels=1, background=255), rows=2, cols=2, square_size=20, origin=(0, 0))
    markers = RegistrationMarkerChart(canvas=CanvasSpec(width=30, height=30, channels=1, background=255), marker_size=10)
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[
            PlacedChart(name="checker", chart=checkerboard, origin=(10, 10)),
            PlacedChart(name="markers", chart=markers, origin=(90, 20)),
        ],
    )

    image = chart.render()

    assert image[20, 20] == 0
    assert image[25, 95] == 0


def test_composite_uses_overwrite_order_for_overlap() -> None:
    composite_canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    first = GrayscaleStepChart(
        canvas=CanvasSpec(width=40, height=20, channels=1, background=255),
        steps=1,
        step_size=(40, 20),
        values=[50],
        origin=(0, 0),
    )
    second = GrayscaleStepChart(
        canvas=CanvasSpec(width=40, height=20, channels=1, background=255),
        steps=1,
        step_size=(40, 20),
        values=[200],
        origin=(0, 0),
    )
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[
            PlacedChart(name="first", chart=first, origin=(20, 20)),
            PlacedChart(name="second", chart=second, origin=(20, 20)),
        ],
    )

    image = chart.render()

    assert image[25, 25] == 200


def test_composite_translates_and_groups_annotations() -> None:
    composite_canvas = CanvasSpec(width=180, height=120, channels=1, background=255)
    checkerboard = CheckerboardChart(canvas=CanvasSpec(width=60, height=60, channels=1, background=255), rows=3, cols=3, square_size=20, origin=(0, 0))
    markers = RegistrationMarkerChart(canvas=CanvasSpec(width=30, height=30, channels=1, background=255), marker_size=10)
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[
            PlacedChart(name="checker", chart=checkerboard, origin=(15, 10)),
            PlacedChart(name="markers", chart=markers, origin=(100, 50)),
        ],
    )

    annotations = chart.get_annotations()

    assert annotations.chart_type == "composite"
    assert annotations.landmarks["checker"]["inner_corners"][0] == (35.0, 30.0)
    assert annotations.landmarks["markers"]["centers"][0] == (105.0, 55.0)
    assert annotations.regions["markers"]["markers"][0]["x"] == 100


def test_composite_raises_when_child_does_not_fit_canvas() -> None:
    composite_canvas = CanvasSpec(width=50, height=50, channels=1, background=255)
    checkerboard = CheckerboardChart(canvas=CanvasSpec(width=40, height=40, channels=1, background=255), rows=2, cols=2, square_size=20, origin=(0, 0))

    with pytest.raises(ValueError, match="does not fit inside the composite canvas"):
        CompositeChart(
            canvas=composite_canvas,
            elements=[PlacedChart(chart=checkerboard, origin=(20, 20))],
        )


def test_composite_save_returns_annotations(tmp_path: Path) -> None:
    composite_canvas = CanvasSpec(width=140, height=100, channels=1, background=255)
    checkerboard = CheckerboardChart(canvas=CanvasSpec(width=40, height=40, channels=1, background=255), rows=2, cols=2, square_size=20, origin=(0, 0))
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[PlacedChart(name="checker", chart=checkerboard, origin=(10, 15))],
    )

    output_path = tmp_path / "composite.png"
    annotations = chart.save(output_path, return_annotations=True)

    assert output_path.exists()
    assert annotations is not None
    assert annotations.landmarks["checker"]["inner_corners"] == [(30.0, 35.0)]
