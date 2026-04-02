from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import (
    CanvasSpec,
    CheckerboardChart,
    CircleGridChart,
    CompositeChart,
    DeadLeavesPatchChart,
    GrayscaleStepChart,
    PlacedChart,
    RegistrationMarkerChart,
    SiemensStarChart,
    SlantedEdgeChart,
)


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


def test_composite_promotes_grayscale_child_into_rgb_canvas() -> None:
    composite_canvas = CanvasSpec(width=120, height=80, channels=3, background=(128, 128, 128))
    grayscale = GrayscaleStepChart(
        canvas=CanvasSpec(width=40, height=20, channels=1, background=255),
        steps=1,
        step_size=(30, 10),
        values=[64],
    )
    chart = CompositeChart(
        canvas=composite_canvas,
        elements=[PlacedChart(name="gray", chart=grayscale, origin=(20, 20))],
    )

    image = chart.render()

    assert image.shape == (80, 120, 3)
    assert tuple(image[30, 40]) == (64, 64, 64)


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


def test_composite_overview_layout_1920x1080(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=1920, height=1080, channels=1, background=255)

    checker = CheckerboardChart(
        canvas=CanvasSpec(width=360, height=280, channels=1, background=255),
        rows=7,
        cols=9,
        square_size=40,
        origin=(0, 0),
    )
    circle_grid = CircleGridChart(
        canvas=CanvasSpec(width=360, height=280, channels=1, background=255),
        rows=5,
        cols=6,
        radius=18,
        spacing=(55, 50),
        origin=(28, 40),
    )
    siemens = SiemensStarChart(
        canvas=CanvasSpec(width=320, height=320, channels=1, background=255),
        outer_radius=140,
        num_sectors=48,
        center=(160, 160),
        inner_radius=16,
    )
    slanted = SlantedEdgeChart(
        canvas=CanvasSpec(width=360, height=220, channels=1, background=255),
        chart_size=(320, 180),
        origin=(20, 20),
        edge_angle_degrees=5.0,
    )
    steps = GrayscaleStepChart(
        canvas=CanvasSpec(width=420, height=120, channels=1, background=255),
        steps=8,
        step_size=(50, 80),
        origin=(10, 20),
    )
    dead_leaves = DeadLeavesPatchChart(
        canvas=CanvasSpec(width=320, height=240, channels=1, background=255),
        patch_size=(260, 180),
        origin=(30, 30),
        num_shapes=180,
        radius_range=(4, 18),
        value_range=(20, 235),
        seed=5,
    )

    marker_block_large = RegistrationMarkerChart(
        canvas=CanvasSpec(width=60, height=60, channels=1, background=255),
        marker_size=18,
    )
    marker_block_small = RegistrationMarkerChart(
        canvas=CanvasSpec(width=48, height=48, channels=1, background=255),
        marker_size=14,
    )

    def frame(name_prefix: str, block_width: int, block_height: int, block_origin: tuple[int, int]) -> list[PlacedChart]:
        left = block_origin[0] - 70
        top = block_origin[1] - 70
        right = block_origin[0] + block_width + 10
        bottom = block_origin[1] + block_height + 10
        return [
            PlacedChart(name=f"{name_prefix}_tl", chart=marker_block_large, origin=(left, top)),
            PlacedChart(name=f"{name_prefix}_tr", chart=marker_block_large, origin=(right, top)),
            PlacedChart(name=f"{name_prefix}_bl", chart=marker_block_large, origin=(left, bottom)),
            PlacedChart(name=f"{name_prefix}_br", chart=marker_block_large, origin=(right, bottom)),
        ]

    elements = [
        PlacedChart(name="checkerboard", chart=checker, origin=(120, 120)),
        *frame("checkerboard_markers", 360, 280, (120, 120)),
        PlacedChart(name="circle_grid", chart=circle_grid, origin=(620, 120)),
        *frame("circle_grid_markers", 360, 280, (620, 120)),
        PlacedChart(name="siemens_star", chart=siemens, origin=(1120, 90)),
        *frame("siemens_star_markers", 320, 320, (1120, 90)),
        PlacedChart(name="slanted_edge", chart=slanted, origin=(120, 610)),
        *frame("slanted_edge_markers", 360, 220, (120, 610)),
        PlacedChart(name="grayscale_step", chart=steps, origin=(620, 690)),
        *frame("grayscale_step_markers", 420, 120, (620, 690)),
        PlacedChart(name="dead_leaves", chart=dead_leaves, origin=(1180, 610)),
        *frame("dead_leaves_markers", 320, 240, (1180, 610)),
        PlacedChart(name="registration_markers", chart=marker_block_small, origin=(1700, 880)),
    ]

    chart = CompositeChart(canvas=canvas, elements=elements)

    output_path = tmp_path / "composite-overview-1920x1080.png"
    image, annotations = chart.render(return_annotations=True)
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (1080, 1920)
    assert output_path.exists()
    assert saved_annotations == annotations
    assert annotations.chart_type == "composite"
    assert "checkerboard" in annotations.landmarks
    assert "circle_grid" in annotations.landmarks
    assert "siemens_star" in annotations.landmarks
    assert "dead_leaves" in annotations.regions
    assert image[140, 140] == 0
    assert image[720, 700] < 255
