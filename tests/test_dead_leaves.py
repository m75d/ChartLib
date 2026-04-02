from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from chartlib import CanvasSpec, DeadLeavesPatchChart


def test_dead_leaves_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=90, channels=1, background=255)
    chart = DeadLeavesPatchChart(
        canvas=canvas,
        patch_size=(40, 30),
        origin=(10, 20),
        num_shapes=10,
    )

    image = chart.render()

    assert image.shape == (90, 120)


def test_dead_leaves_is_deterministic_for_same_seed() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart_a = DeadLeavesPatchChart(canvas=canvas, patch_size=(40, 30), origin=(10, 10), seed=7)
    chart_b = DeadLeavesPatchChart(canvas=canvas, patch_size=(40, 30), origin=(10, 10), seed=7)

    np.testing.assert_array_equal(chart_a.render(), chart_b.render())


def test_dead_leaves_differs_for_different_seeds() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart_a = DeadLeavesPatchChart(canvas=canvas, patch_size=(40, 30), origin=(10, 10), seed=1)
    chart_b = DeadLeavesPatchChart(canvas=canvas, patch_size=(40, 30), origin=(10, 10), seed=2)

    assert not np.array_equal(chart_a.render(), chart_b.render())


def test_dead_leaves_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = DeadLeavesPatchChart(
        canvas=canvas,
        patch_size=(40, 20),
        num_shapes=5,
        seed=3,
        value_range=(10, 20),
    )

    image = chart.render()
    annotations = chart.get_annotations()

    assert annotations.regions["patch"][0]["x"] == 30
    assert annotations.regions["patch"][0]["y"] == 30
    assert image[10, 10] == 255


def test_dead_leaves_raises_when_patch_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=1, background=255)

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        DeadLeavesPatchChart(
            canvas=canvas,
            patch_size=(50, 20),
            origin=(0, 0),
        )


def test_dead_leaves_rejects_non_grayscale_canvas() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=3, background=(255, 255, 255))

    with pytest.raises(ValueError, match="requires a grayscale canvas"):
        DeadLeavesPatchChart(
            canvas=canvas,
            patch_size=(40, 30),
        )


def test_dead_leaves_rejects_invalid_radius_range() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="radius_range minimum must be less than or equal to the maximum"):
        DeadLeavesPatchChart(
            canvas=canvas,
            patch_size=(40, 30),
            radius_range=(10, 5),
        )


def test_dead_leaves_rejects_invalid_value_range() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="value_range must be a 2-tuple of integers in the range \\[0, 255\\]"):
        DeadLeavesPatchChart(
            canvas=canvas,
            patch_size=(40, 30),
            value_range=(0, 300),
        )


def test_dead_leaves_annotations_and_save(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=100, channels=1, background=255)
    chart = DeadLeavesPatchChart(
        canvas=canvas,
        patch_size=(60, 40),
        origin=(20, 25),
        num_shapes=25,
        radius_range=(3, 8),
        value_range=(10, 200),
        background_value=12,
        seed=11,
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "dead-leaves.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (100, 160)
    assert output_path.exists()
    assert saved_annotations == annotations
    assert annotations.regions["patch"][0] == {
        "type": "rectangle",
        "x": 20,
        "y": 25,
        "width": 60,
        "height": 40,
        "num_shapes": 25,
        "radius_range": (3, 8),
        "value_range": (10, 200),
        "seed": 11,
        "background_value": 12,
    }


def test_dead_leaves_uses_value_range_lower_bound_as_default_background() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)
    chart = DeadLeavesPatchChart(
        canvas=canvas,
        patch_size=(30, 20),
        origin=(10, 10),
        num_shapes=1,
        radius_range=(1, 1),
        value_range=(30, 40),
        seed=0,
    )

    annotations = chart.get_annotations()

    assert annotations.regions["patch"][0]["background_value"] == 30
