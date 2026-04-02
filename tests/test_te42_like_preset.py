from __future__ import annotations

from pathlib import Path

import numpy as np

from chartlib import CanvasSpec, TE42LikePreset


def test_te42_like_preset_renders_rgb_image_shape() -> None:
    preset = TE42LikePreset(
        canvas=CanvasSpec(width=960, height=540, channels=3, background=(128, 128, 128)),
        seed=7,
    )

    image = preset.render()

    assert image.shape == (540, 960, 3)


def test_te42_like_preset_annotations_include_expected_groups() -> None:
    preset = TE42LikePreset(
        canvas=CanvasSpec(width=960, height=540, channels=3, background=(128, 128, 128)),
        seed=7,
    )

    annotations = preset.get_annotations()

    assert annotations.chart_type == "composite"
    assert "grayscale" in annotations.landmarks
    assert "color_patches" in annotations.landmarks
    assert "slanted_edge_0" in annotations.landmarks
    assert "siemens_star_0" in annotations.landmarks
    assert "dead_leaves" in annotations.regions
    assert "registration_markers" in annotations.regions


def test_te42_like_preset_is_deterministic_for_fixed_seed() -> None:
    canvas = CanvasSpec(width=960, height=540, channels=3, background=(128, 128, 128))
    first = TE42LikePreset(canvas=canvas, seed=11)
    second = TE42LikePreset(canvas=canvas, seed=11)

    first_image = first.render()
    second_image = second.render()

    assert np.array_equal(first_image, second_image)


def test_te42_like_preset_layout_regions_are_distinct() -> None:
    preset = TE42LikePreset(
        canvas=CanvasSpec(width=960, height=540, channels=3, background=(128, 128, 128)),
        seed=3,
    )

    annotations = preset.get_annotations()
    grayscale_region = annotations.regions["grayscale"]["steps"][0]
    color_patch_region = annotations.regions["color_patches"]["patches"][0]
    slanted_edge_region = annotations.regions["slanted_edge_0"]["chart"][0]
    dead_leaves_region = annotations.regions["dead_leaves"]["patch"][0]
    star_region = annotations.regions["siemens_star_0"]["star"][0]

    assert grayscale_region["y"] < slanted_edge_region["y"]
    assert grayscale_region["x"] < color_patch_region["x"]
    assert slanted_edge_region["x"] < dead_leaves_region["x"] < star_region["x"]


def test_te42_like_preset_save_returns_annotations(tmp_path: Path) -> None:
    preset = TE42LikePreset(
        canvas=CanvasSpec(width=960, height=540, channels=3, background=(128, 128, 128)),
        seed=5,
    )

    output_path = tmp_path / "te42-like-preset.png"
    annotations = preset.save(output_path, return_annotations=True)

    assert output_path.exists()
    assert annotations is not None
    assert "registration_markers" in annotations.landmarks
