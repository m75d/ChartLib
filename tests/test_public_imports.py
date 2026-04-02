from __future__ import annotations

import chartlib
from chartlib import CircleGridChart, CheckerboardChart, GrayscaleStepChart, SlantedEdgeChart
from chartlib.charts import CheckerboardChart as ChartsCheckerboardChart
from chartlib.charts import CircleGridChart as ChartsCircleGridChart
from chartlib.charts import GrayscaleStepChart as ChartsGrayscaleStepChart
from chartlib.charts import SlantedEdgeChart as ChartsSlantedEdgeChart


def test_chartlib_top_level_exports_builtin_chart_classes() -> None:
    assert "CheckerboardChart" in chartlib.__all__
    assert "CircleGridChart" in chartlib.__all__
    assert "GrayscaleStepChart" in chartlib.__all__
    assert "SlantedEdgeChart" in chartlib.__all__
    assert chartlib.CheckerboardChart is CheckerboardChart
    assert chartlib.CircleGridChart is CircleGridChart
    assert chartlib.GrayscaleStepChart is GrayscaleStepChart
    assert chartlib.SlantedEdgeChart is SlantedEdgeChart


def test_chartlib_charts_exports_builtin_chart_classes() -> None:
    assert ChartsCheckerboardChart is CheckerboardChart
    assert ChartsCircleGridChart is CircleGridChart
    assert ChartsGrayscaleStepChart is GrayscaleStepChart
    assert ChartsSlantedEdgeChart is SlantedEdgeChart
