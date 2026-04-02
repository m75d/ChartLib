from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import CanvasSpec, SlantedEdgeChart


def test_slanted_edge_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=255)
    chart = SlantedEdgeChart(
        canvas=canvas,
        chart_size=(60, 40),
        origin=(20, 20),
    )

    image = chart.render()

    assert image.shape == (80, 120)


def test_slanted_edge_opposite_sides_have_expected_intensities() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=200)
    chart = SlantedEdgeChart(
        canvas=canvas,
        chart_size=(60, 40),
        edge_angle_degrees=0.0,
        origin=(20, 20),
    )

    image = chart.render()

    assert image[40, 35] == 0
    assert image[40, 65] == 255
    assert image[10, 10] == 200


def test_slanted_edge_annotations_include_chart_and_edge_geometry(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=100, channels=1, background=255)
    chart = SlantedEdgeChart(
        canvas=canvas,
        chart_size=(80, 50),
        edge_angle_degrees=5.0,
        origin=(20, 25),
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "slanted-edge.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (100, 160)
    assert output_path.exists()
    assert saved_annotations == annotations

    edge_segment = annotations.landmarks["edge_segment"]
    edge_center = annotations.landmarks["edge_center"]
    chart_region = annotations.regions["chart"][0]
    edge_region = annotations.regions["edge"][0]

    assert len(edge_segment) == 2
    assert edge_center == [(60.0, 50.0)]
    assert chart_region == {"x": 20, "y": 25, "width": 80, "height": 50}
    assert edge_region["angle_degrees"] == 5.0
    assert edge_segment[0][1] <= edge_segment[1][1]


def test_slanted_edge_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = SlantedEdgeChart(
        canvas=canvas,
        chart_size=(40, 20),
        edge_angle_degrees=0.0,
    )

    image = chart.render()

    assert image[40, 40] == 0
    assert image[40, 60] == 255
    assert image[10, 10] == 255


def test_slanted_edge_raises_when_chart_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        SlantedEdgeChart(
            canvas=canvas,
            chart_size=(50, 20),
            origin=(0, 0),
        )


def test_slanted_edge_rejects_invalid_grayscale_values() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="dark_value and light_value must be in the range \\[0, 255\\]"):
        SlantedEdgeChart(
            canvas=canvas,
            chart_size=(40, 20),
            dark_value=300,
        )


def test_slanted_edge_positive_angle_moves_lower_edge_rightward() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=1, background=255)
    chart = SlantedEdgeChart(
        canvas=canvas,
        chart_size=(60, 40),
        edge_angle_degrees=10.0,
        origin=(20, 20),
    )

    edge_segment = chart.get_annotations().landmarks["edge_segment"]
    top_point, bottom_point = edge_segment

    assert bottom_point[1] >= top_point[1]
    assert bottom_point[0] > top_point[0]
