from __future__ import annotations

from chartlib import CanvasSpec, GrayscaleStepChart, SiemensStarChart, SlantedEdgeChart


def test_region_annotations_share_common_bounds_fields() -> None:
    canvas = CanvasSpec(width=200, height=160, channels=1, background=255)
    step_chart = GrayscaleStepChart(canvas=canvas, steps=3, step_size=(20, 10), origin=(15, 20))
    slanted_chart = SlantedEdgeChart(canvas=canvas, chart_size=(80, 40), origin=(30, 50))
    star_chart = SiemensStarChart(canvas=canvas, outer_radius=25, num_sectors=12, center=(140, 70))

    step_region = step_chart.get_annotations().regions["steps"][0]
    chart_region = slanted_chart.get_annotations().regions["chart"][0]
    edge_region = slanted_chart.get_annotations().regions["edge"][0]
    star_region = star_chart.get_annotations().regions["star"][0]
    ray_region = star_chart.get_annotations().regions["boundary_ray"][0]

    for region in (step_region, chart_region, edge_region, star_region, ray_region):
        assert set(("type", "x", "y", "width", "height")).issubset(region)
        assert region["width"] >= 0
        assert region["height"] >= 0

    assert step_region["type"] == "rectangle"
    assert chart_region["type"] == "rectangle"
    assert edge_region["type"] == "line_segment"
    assert star_region["type"] == "circle_annulus"
    assert ray_region["type"] == "line_segment"
