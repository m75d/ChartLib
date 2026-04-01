from __future__ import annotations

import chartlib
from chartlib import CircleGridChart
from chartlib.charts import CircleGridChart as ChartsCircleGridChart


def test_chartlib_top_level_exports_circle_grid_chart() -> None:
    assert "CircleGridChart" in chartlib.__all__
    assert chartlib.CircleGridChart is CircleGridChart


def test_chartlib_charts_exports_circle_grid_chart() -> None:
    assert ChartsCircleGridChart is CircleGridChart
