from __future__ import annotations

import chartlib
from chartlib import (
    CompositeChart,
    DeadLeavesPatchChart,
    CircleGridChart,
    CheckerboardChart,
    ColorPatchChart,
    GrayscaleStepChart,
    PlacedChart,
    RegistrationMarkerChart,
    SiemensStarChart,
    SlantedEdgeChart,
    TE42LikePreset,
)
from chartlib.charts import CheckerboardChart as ChartsCheckerboardChart
from chartlib.charts import CircleGridChart as ChartsCircleGridChart
from chartlib.charts import CompositeChart as ChartsCompositeChart
from chartlib.charts import ColorPatchChart as ChartsColorPatchChart
from chartlib.charts import DeadLeavesPatchChart as ChartsDeadLeavesPatchChart
from chartlib.charts import GrayscaleStepChart as ChartsGrayscaleStepChart
from chartlib.charts import PlacedChart as ChartsPlacedChart
from chartlib.charts import RegistrationMarkerChart as ChartsRegistrationMarkerChart
from chartlib.charts import SiemensStarChart as ChartsSiemensStarChart
from chartlib.charts import SlantedEdgeChart as ChartsSlantedEdgeChart


def test_chartlib_top_level_exports_builtin_chart_classes() -> None:
    assert "CheckerboardChart" in chartlib.__all__
    assert "CircleGridChart" in chartlib.__all__
    assert "CompositeChart" in chartlib.__all__
    assert "ColorPatchChart" in chartlib.__all__
    assert "DeadLeavesPatchChart" in chartlib.__all__
    assert "GrayscaleStepChart" in chartlib.__all__
    assert "PlacedChart" in chartlib.__all__
    assert "RegistrationMarkerChart" in chartlib.__all__
    assert "SiemensStarChart" in chartlib.__all__
    assert "SlantedEdgeChart" in chartlib.__all__
    assert "TE42LikePreset" in chartlib.__all__
    assert chartlib.CheckerboardChart is CheckerboardChart
    assert chartlib.CircleGridChart is CircleGridChart
    assert chartlib.CompositeChart is CompositeChart
    assert chartlib.ColorPatchChart is ColorPatchChart
    assert chartlib.DeadLeavesPatchChart is DeadLeavesPatchChart
    assert chartlib.GrayscaleStepChart is GrayscaleStepChart
    assert chartlib.PlacedChart is PlacedChart
    assert chartlib.RegistrationMarkerChart is RegistrationMarkerChart
    assert chartlib.SiemensStarChart is SiemensStarChart
    assert chartlib.SlantedEdgeChart is SlantedEdgeChart
    assert chartlib.TE42LikePreset is TE42LikePreset


def test_chartlib_charts_exports_builtin_chart_classes() -> None:
    assert ChartsCheckerboardChart is CheckerboardChart
    assert ChartsCircleGridChart is CircleGridChart
    assert ChartsCompositeChart is CompositeChart
    assert ChartsColorPatchChart is ColorPatchChart
    assert ChartsDeadLeavesPatchChart is DeadLeavesPatchChart
    assert ChartsGrayscaleStepChart is GrayscaleStepChart
    assert ChartsPlacedChart is PlacedChart
    assert ChartsRegistrationMarkerChart is RegistrationMarkerChart
    assert ChartsSiemensStarChart is SiemensStarChart
    assert ChartsSlantedEdgeChart is SlantedEdgeChart
