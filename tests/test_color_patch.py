from __future__ import annotations

from pathlib import Path

import pytest

from chartlib import CanvasSpec, ColorPatchChart


def test_color_patch_output_image_shape() -> None:
    canvas = CanvasSpec(width=120, height=90, channels=3, background=(255, 255, 255))
    chart = ColorPatchChart(
        canvas=canvas,
        rows=2,
        cols=3,
        patch_size=(20, 15),
        origin=(10, 20),
    )

    image = chart.render()

    assert image.shape == (90, 120, 3)


def test_color_patch_patch_colors_appear_in_expected_positions() -> None:
    canvas = CanvasSpec(width=120, height=80, channels=3, background=(9, 9, 9))
    chart = ColorPatchChart(
        canvas=canvas,
        rows=2,
        cols=2,
        patch_size=(20, 20),
        origin=(10, 10),
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255), (250, 250, 0)],
    )

    image = chart.render()

    assert tuple(image[20, 20]) == (255, 0, 0)
    assert tuple(image[20, 40]) == (0, 255, 0)
    assert tuple(image[40, 20]) == (0, 0, 255)
    assert tuple(image[40, 40]) == (250, 250, 0)
    assert tuple(image[5, 5]) == (9, 9, 9)


def test_color_patch_annotations_and_save(tmp_path: Path) -> None:
    canvas = CanvasSpec(width=160, height=100, channels=3, background=(255, 255, 255))
    chart = ColorPatchChart(
        canvas=canvas,
        rows=2,
        cols=3,
        patch_size=(20, 15),
        origin=(10, 20),
        colors=[(10, 20, 30), (40, 50, 60), (70, 80, 90), (100, 110, 120), (130, 140, 150), (160, 170, 180)],
        labels=["a", "b", "c", "d", "e", "f"],
    )

    image, annotations = chart.render(return_annotations=True)
    output_path = tmp_path / "color-patch.png"
    saved_annotations = chart.save(output_path, return_annotations=True)

    assert image.shape == (100, 160, 3)
    assert output_path.exists()
    assert saved_annotations == annotations
    assert len(annotations.landmarks["centers"]) == 6
    assert annotations.landmarks["centers"][0] == (20.0, 27.5)
    assert annotations.landmarks["centers"][-1] == (60.0, 42.5)
    assert annotations.regions["patches"][1] == {
        "type": "rectangle",
        "x": 30,
        "y": 20,
        "width": 20,
        "height": 15,
        "index": 1,
        "color": (40, 50, 60),
        "label": "b",
    }


def test_color_patch_uses_centered_origin_by_default() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=3, background=(255, 255, 255))
    chart = ColorPatchChart(
        canvas=canvas,
        rows=2,
        cols=2,
        patch_size=20,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255), (250, 250, 0)],
    )

    image = chart.render()

    assert tuple(image[30, 40]) == (255, 0, 0)
    assert tuple(image[30, 60]) == (0, 255, 0)
    assert tuple(image[10, 10]) == (255, 255, 255)


def test_color_patch_raises_when_chart_exceeds_canvas() -> None:
    canvas = CanvasSpec(width=40, height=40, channels=3, background=(255, 255, 255))

    with pytest.raises(ValueError, match="does not fit inside the canvas"):
        ColorPatchChart(
            canvas=canvas,
            rows=3,
            cols=3,
            patch_size=20,
            origin=(0, 0),
        )


def test_color_patch_rejects_non_rgb_canvas() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=1, background=255)

    with pytest.raises(ValueError, match="requires an RGB canvas"):
        ColorPatchChart(
            canvas=canvas,
            rows=2,
            cols=2,
            patch_size=20,
        )


def test_color_patch_rejects_invalid_colors_length() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=3, background=(255, 255, 255))

    with pytest.raises(ValueError, match="colors length must match rows \\* cols"):
        ColorPatchChart(
            canvas=canvas,
            rows=2,
            cols=2,
            patch_size=20,
            colors=[(255, 0, 0)],
        )


def test_color_patch_rejects_invalid_rgb_values() -> None:
    canvas = CanvasSpec(width=100, height=80, channels=3, background=(255, 255, 255))

    with pytest.raises(ValueError, match="colors\\[0\\] integer values must be in the range \\[0, 255\\]"):
        ColorPatchChart(
            canvas=canvas,
            rows=1,
            cols=1,
            patch_size=20,
            colors=[(300, 0, 0)],
        )
