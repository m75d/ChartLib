from __future__ import annotations

from pathlib import Path

import numpy as np

from chartlib import CanvasSpec, TE42Preset


def test_te42_preset_renders_rgb_image_shape() -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=7,
    )

    image = preset.render()

    assert image.shape == (720, 1280, 3)


def test_te42_preset_annotations_include_expected_groups() -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=7,
    )

    annotations = preset.get_annotations()

    assert annotations.chart_type == "composite"
    assert "grayscale" in annotations.regions
    assert "color_patches" in annotations.regions
    assert "dead_leaves_0" in annotations.regions
    assert "dead_leaves_1" in annotations.regions
    assert "registration_markers" in annotations.regions
    for index in range(9):
        assert f"siemens_star_{index}" in annotations.regions
    for index in range(4):
        assert f"slanted_edge_{index}" in annotations.regions
    assert len(annotations.regions["color_patches"]["patches"]) == 96
    assert len(annotations.regions["registration_markers"]["markers"]) == 18


def test_te42_preset_is_deterministic_for_fixed_seed() -> None:
    canvas = CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128))
    first = TE42Preset(canvas=canvas, seed=11)
    second = TE42Preset(canvas=canvas, seed=11)

    assert np.array_equal(first.render(), second.render())


def test_te42_preset_layout_reflects_reference_style_structure() -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=3,
    )

    annotations = preset.get_annotations()
    grayscale_region = annotations.regions["grayscale"]["steps"][0]
    color_patch_region = annotations.regions["color_patches"]["patches"][0]
    dead_leaves_region = annotations.regions["dead_leaves_0"]["patch"][0]
    center_star_region = annotations.regions["siemens_star_0"]["star"][0]
    top_left_corner_star = annotations.regions["siemens_star_1"]["star"][0]
    top_right_corner_star = annotations.regions["siemens_star_2"]["star"][0]
    bottom_left_corner_star = annotations.regions["siemens_star_3"]["star"][0]
    bottom_right_corner_star = annotations.regions["siemens_star_4"]["star"][0]
    left_side_star = annotations.regions["siemens_star_5"]["star"][0]
    right_side_star = annotations.regions["siemens_star_6"]["star"][0]
    top_left_edge_region = annotations.regions["slanted_edge_0"]["chart"][0]
    bottom_right_edge_region = annotations.regions["slanted_edge_3"]["chart"][0]

    assert grayscale_region["y"] < center_star_region["y"]
    assert dead_leaves_region["x"] < center_star_region["x"] < color_patch_region["x"]
    assert top_left_edge_region["y"] < bottom_right_edge_region["y"]
    assert annotations.regions["dead_leaves_0"]["patch"][0]["width"] != annotations.regions["dead_leaves_1"]["patch"][0]["width"]
    assert top_left_corner_star["x"] < center_star_region["x"] < top_right_corner_star["x"]
    assert top_left_corner_star["y"] < center_star_region["y"]
    assert bottom_left_corner_star["y"] > center_star_region["y"]
    assert left_side_star["x"] < center_star_region["x"] < right_side_star["x"]


def test_te42_preset_circular_family_uses_revised_size_hierarchy() -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=3,
    )

    annotations = preset.get_annotations()
    center_star = annotations.regions["siemens_star_0"]["star"][0]
    corner_star = annotations.regions["siemens_star_1"]["star"][0]
    side_star = annotations.regions["siemens_star_5"]["star"][0]
    small_upper_star = annotations.regions["siemens_star_7"]["star"][0]

    assert center_star["width"] > corner_star["width"] > side_star["width"] > small_upper_star["width"]


def test_te42_preset_center_star_matches_refined_role() -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=3,
    )

    annotations = preset.get_annotations()
    center_star = annotations.regions["siemens_star_0"]["star"][0]
    corner_star = annotations.regions["siemens_star_1"]["star"][0]

    assert center_star["num_sectors"] == 72
    assert center_star["width"] >= int(corner_star["width"] * 1.15)


def test_te42_preset_save_returns_annotations(tmp_path: Path) -> None:
    preset = TE42Preset(
        canvas=CanvasSpec(width=1280, height=720, channels=3, background=(128, 128, 128)),
        seed=5,
    )

    output_path = tmp_path / "te42-preset.png"
    annotations = preset.save(output_path, return_annotations=True)

    assert output_path.exists()
    assert annotations is not None
    assert "registration_markers" in annotations.regions
