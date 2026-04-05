from pathlib import Path

from chartlib import (
    CanvasSpec,
    ColorPatchChart,
    CompositeChart,
    DeadLeavesPatchChart,
    GrayscaleStepChart,
    PlacedChart,
    RegistrationMarkerChart,
    SiemensStarChart,
    SlantedEdgeChart,
)


def create_cross_marker(cross_length: int, cross_thickness: int) -> RegistrationMarkerChart:
    return RegistrationMarkerChart(
        canvas=CanvasSpec(width=cross_length, height=cross_length, channels=1, background=128),
        marker_size=cross_length,
        marker_shape="cross",
        marker_positions=[(cross_length // 2, cross_length // 2)],
        origin=(0, 0),
        layout_size=(cross_length, cross_length),
        dark_value=0,
        cross_length=cross_length,
        cross_thickness=cross_thickness,
    )


def create_quadrant_marker(size: int) -> RegistrationMarkerChart:
    return RegistrationMarkerChart(
        canvas=CanvasSpec(width=size, height=size, channels=1, background=128),
        marker_size=size,
        marker_shape="quadrant_circle",
        marker_positions=[(size // 2, size // 2)],
        origin=(0, 0),
        layout_size=(size, size),
        dark_value=0,
        light_value=255,
    )


def create_corner_marker(length: int, thickness: int, orientation: str) -> RegistrationMarkerChart:
    return RegistrationMarkerChart(
        canvas=CanvasSpec(width=length, height=length, channels=1, background=128),
        marker_size=length,
        marker_shape="corner",
        marker_positions=[(length // 2, length // 2)],
        origin=(0, 0),
        layout_size=(length, length),
        dark_value=0,
        cross_length=length,
        cross_thickness=thickness,
        corner_orientation=orientation,
    )


def main() -> None:
    width, height = 1920, 1080
    background_gray = 128
    background_rgb = (background_gray, background_gray, background_gray)

    center_x, center_y = width // 2, height // 2
    outer_radius = 184
    num_sectors = 144

    marker_offset = 161
    cross_thickness = 5
    cross_length = 49

    left_cross_x = center_x - marker_offset
    right_cross_x = center_x + marker_offset
    top_cross_y = center_y - marker_offset
    bottom_cross_y = center_y + marker_offset

    row_left = left_cross_x
    row_right = right_cross_x
    row_width = row_right - row_left
    patch_size = row_width // 5
    top_row_top = 268
    top_patch_values = [255, 240, 224, 208, 192]
    bottom_row_top = 748
    bottom_patch_values = [96, 72, 48, 24, 0]

    color_patch_size = 42
    color_chart_width = 6 * color_patch_size
    color_chart_height = 4 * color_patch_size
    color_chart_left = center_x - color_chart_width // 2
    color_chart_top = top_row_top - 20 - color_chart_height
    color_chart_center_x = color_chart_left + color_chart_width // 2
    color_chart_center_y = color_chart_top + color_chart_height // 2
    lower_color_chart_top = bottom_row_top + patch_size + 20
    lower_color_chart_center_y = lower_color_chart_top + color_chart_height // 2

    macbeth_marker_size = 18
    macbeth_marker_gap = 20
    left_macbeth_marker_center_x = color_chart_left - macbeth_marker_gap - macbeth_marker_size // 2
    right_macbeth_marker_center_x = color_chart_left + color_chart_width + macbeth_marker_gap + macbeth_marker_size // 2
    left_lower_marker_center_x = left_macbeth_marker_center_x
    right_lower_marker_center_x = right_macbeth_marker_center_x

    top_macbeth_marker_size = 40
    top_macbeth_marker_center_y = color_chart_top - 24 - top_macbeth_marker_size // 2
    bottom_macbeth_marker_center_y = height - top_macbeth_marker_center_y
    central_star_diameter = 2 * outer_radius

    center_marker_size = 20

    corner_marker_size = 40
    corner_marker_radius = corner_marker_size // 2
    corner_marker_margin_x = 18
    corner_marker_margin_y = 18
    corner_markers = [
        (corner_marker_margin_x + corner_marker_radius, corner_marker_margin_y + corner_marker_radius),
        (width - corner_marker_margin_x - corner_marker_radius, corner_marker_margin_y + corner_marker_radius),
        (corner_marker_margin_x + corner_marker_radius, height - corner_marker_margin_y - corner_marker_radius),
        (width - corner_marker_margin_x - corner_marker_radius, height - corner_marker_margin_y - corner_marker_radius),
    ]
    upper_left_half_star_square_left = corner_markers[0][0]
    upper_left_half_star_square_top = corner_markers[0][1]
    upper_left_half_star_square_size = central_star_diameter
    upper_right_half_star_square_left = corner_markers[1][0] - central_star_diameter
    upper_right_half_star_square_top = corner_markers[1][1]
    lower_left_half_star_square_left = corner_markers[2][0]
    lower_left_half_star_square_top = corner_markers[2][1] - central_star_diameter
    lower_right_half_star_square_left = corner_markers[3][0] - central_star_diameter
    lower_right_half_star_square_top = corner_markers[3][1] - central_star_diameter
    upper_left_half_star_center = (
        upper_left_half_star_square_left + upper_left_half_star_square_size // 2,
        upper_left_half_star_square_top + upper_left_half_star_square_size // 2,
    )
    upper_right_half_star_center = (
        upper_right_half_star_square_left + upper_left_half_star_square_size // 2,
        upper_right_half_star_square_top + upper_left_half_star_square_size // 2,
    )
    lower_left_half_star_center = (
        lower_left_half_star_square_left + upper_left_half_star_square_size // 2,
        lower_left_half_star_square_top + upper_left_half_star_square_size // 2,
    )
    lower_right_half_star_center = (
        lower_right_half_star_square_left + upper_left_half_star_square_size // 2,
        lower_right_half_star_square_top + upper_left_half_star_square_size // 2,
    )
    right_mid_marker_center = (width - corner_marker_margin_x - corner_marker_radius, center_y)
    upper_right_side_marker_center = (
        width - corner_marker_margin_x - corner_marker_radius,
        corner_markers[1][1] + central_star_diameter,
    )
    lower_right_side_marker_center = (
        width - corner_marker_margin_x - corner_marker_radius,
        corner_markers[3][1] - central_star_diameter,
    )
    right_small_star_diameter = round(0.45 * central_star_diameter * 0.8)
    right_small_star_radius = right_small_star_diameter // 2
    upper_right_small_star_diameter = round(right_small_star_diameter * 1.1)
    upper_right_small_star_radius = upper_right_small_star_diameter // 2
    lower_right_small_star_diameter = round(right_small_star_diameter * 1.1)
    lower_right_small_star_radius = lower_right_small_star_diameter // 2
    right_small_star_center = (
        upper_right_half_star_center[0],
        upper_right_side_marker_center[1] + upper_right_small_star_radius - top_macbeth_marker_size // 2,
    )
    upper_right_small_star_marker_square_size = round(upper_right_small_star_diameter * 0.90)
    upper_right_small_star_marker_half_span = upper_right_small_star_marker_square_size / 2.0
    lower_right_small_star_center = (
        upper_right_half_star_center[0],
        lower_right_side_marker_center[1] - lower_right_small_star_radius + top_macbeth_marker_size // 2,
    )
    left_small_star_center = (
        upper_left_half_star_center[0],
        right_small_star_center[1],
    )
    lower_left_small_star_center = (
        upper_left_half_star_center[0],
        lower_right_small_star_center[1],
    )

    def small_star_corner_specs(center_x: int, center_y: int) -> list[tuple[str, float, float]]:
        return [
            ("top_left", center_x - upper_right_small_star_marker_half_span, center_y - upper_right_small_star_marker_half_span),
            ("top_right", center_x + upper_right_small_star_marker_half_span, center_y - upper_right_small_star_marker_half_span),
            ("bottom_left", center_x - upper_right_small_star_marker_half_span, center_y + upper_right_small_star_marker_half_span),
            ("bottom_right", center_x + upper_right_small_star_marker_half_span, center_y + upper_right_small_star_marker_half_span),
        ]

    upper_right_small_star_corner_marker_specs = small_star_corner_specs(*right_small_star_center)
    upper_left_small_star_corner_marker_specs = small_star_corner_specs(*left_small_star_center)
    lower_right_small_star_corner_marker_specs = small_star_corner_specs(*lower_right_small_star_center)
    lower_left_small_star_corner_marker_specs = small_star_corner_specs(*lower_left_small_star_center)

    color_chart_values = [
        [(115, 82, 68), (194, 150, 130), (98, 122, 157), (87, 108, 67), (133, 128, 177), (103, 189, 170)],
        [(214, 126, 44), (80, 91, 166), (193, 90, 99), (94, 60, 108), (157, 188, 64), (224, 163, 46)],
        [(56, 61, 150), (70, 148, 73), (175, 54, 60), (231, 199, 31), (187, 86, 149), (8, 133, 161)],
        [(243, 243, 242), (200, 200, 200), (160, 160, 160), (122, 122, 121), (85, 85, 85), (52, 52, 52)],
    ]
    lower_color_chart_values = [
        [(52, 52, 52), (85, 85, 85), (122, 122, 121), (160, 160, 160), (200, 200, 200), (243, 243, 242)],
        [(78, 60, 50), (108, 82, 65), (140, 105, 82), (172, 132, 104), (202, 162, 132), (228, 202, 184)],
        [(39, 132, 77), (74, 165, 92), (47, 126, 170), (82, 152, 196), (190, 148, 53), (223, 183, 88)],
        [(150, 58, 60), (201, 116, 98), (95, 76, 148), (128, 116, 182), (176, 111, 150), (214, 157, 186)],
    ]

    left_column_left = 684
    left_column_top = top_cross_y
    left_column_bottom = bottom_cross_y
    left_column_height = left_column_bottom - left_column_top
    left_column_patch_height = left_column_height // 5
    left_column_values = [180, 152, 125, 98, 70]
    right_column_left = width - left_column_left - patch_size
    right_column_values = [value - 10 for value in left_column_values]

    vertical_color_patch_size = 30
    vertical_color_chart_width = 3 * vertical_color_patch_size
    vertical_color_chart_height = 8 * vertical_color_patch_size
    vertical_color_chart_gap = 22
    left_vertical_color_left = left_column_left - vertical_color_chart_gap - vertical_color_chart_width
    left_vertical_color_top = center_y - vertical_color_chart_height // 2
    right_vertical_color_left = right_column_left + patch_size + vertical_color_chart_gap
    left_vertical_color_center_x = left_vertical_color_left + vertical_color_chart_width // 2
    right_vertical_color_center_x = right_vertical_color_left + vertical_color_chart_width // 2
    vertical_marker_gap = 16
    top_vertical_marker_center_y = left_vertical_color_top - vertical_marker_gap - macbeth_marker_size // 2
    bottom_vertical_marker_center_y = left_vertical_color_top + vertical_color_chart_height + vertical_marker_gap + macbeth_marker_size // 2

    left_vertical_color_values = [
        [(236, 236, 236), (214, 214, 214), (196, 196, 196)],
        [(180, 156, 214), (118, 188, 224), (232, 232, 232)],
        [(188, 94, 164), (92, 180, 212), (182, 182, 182)],
        [(120, 78, 178), (76, 156, 206), (168, 168, 168)],
        [(74, 148, 186), (66, 126, 170), (150, 150, 150)],
        [(56, 168, 112), (46, 108, 74), (126, 126, 126)],
        [(224, 196, 62), (128, 82, 30), (96, 96, 96)],
        [(248, 248, 248), (34, 34, 34), (64, 64, 64)],
    ]
    right_vertical_color_values = [
        [(248, 248, 248), (230, 230, 230), (212, 212, 212)],
        [(170, 42, 44), (214, 62, 62), (244, 118, 84)],
        [(176, 54, 56), (226, 82, 54), (240, 132, 62)],
        [(188, 76, 52), (232, 116, 46), (242, 164, 50)],
        [(206, 112, 44), (236, 156, 34), (238, 194, 30)],
        [(190, 150, 36), (182, 184, 32), (150, 188, 44)],
        [(130, 130, 130), (96, 96, 96), (68, 68, 68)],
        [(246, 246, 246), (34, 34, 34), (72, 72, 72)],
    ]

    dead_leaves_size = 180
    dead_leaves_left = left_column_left + patch_size - dead_leaves_size
    dead_leaves_top = top_row_top + patch_size - dead_leaves_size
    dead_leaves_marker_size = 18
    dead_leaves_corner_markers = [
        (dead_leaves_left, dead_leaves_top),
        (dead_leaves_left + dead_leaves_size, dead_leaves_top),
        (dead_leaves_left, dead_leaves_top + dead_leaves_size),
        (dead_leaves_left + dead_leaves_size, dead_leaves_top + dead_leaves_size),
    ]
    lower_dead_leaves_left = width - dead_leaves_left - dead_leaves_size
    lower_dead_leaves_top = height - dead_leaves_top - dead_leaves_size
    lower_dead_leaves_corner_markers = [
        (lower_dead_leaves_left, lower_dead_leaves_top),
        (lower_dead_leaves_left + dead_leaves_size, lower_dead_leaves_top),
        (lower_dead_leaves_left, lower_dead_leaves_top + dead_leaves_size),
        (lower_dead_leaves_left + dead_leaves_size, lower_dead_leaves_top + dead_leaves_size),
    ]
    slanted_edge_width = patch_size
    slanted_edge_height = 240
    upper_left_slanted_edge_left = right_column_left
    upper_left_slanted_edge_top = top_row_top + patch_size - slanted_edge_height
    upper_right_slanted_edge_width = slanted_edge_height
    upper_right_slanted_edge_height = slanted_edge_width
    upper_right_slanted_edge_left = upper_left_slanted_edge_left + slanted_edge_width
    upper_right_slanted_edge_top = upper_left_slanted_edge_top + slanted_edge_height - upper_right_slanted_edge_height
    lower_left_slanted_edge_left = width - upper_right_slanted_edge_left - upper_right_slanted_edge_width
    lower_left_slanted_edge_top = height - upper_right_slanted_edge_top - upper_right_slanted_edge_height
    lower_right_slanted_edge_left = width - upper_left_slanted_edge_left - slanted_edge_width
    lower_right_slanted_edge_top = height - upper_left_slanted_edge_top - slanted_edge_height
    slanted_corner_marker_size = 36
    slanted_corner_marker_thickness = 4

    composite_canvas = CanvasSpec(width=width, height=height, channels=3, background=background_rgb)
    elements: list[PlacedChart] = []

    star_size = 2 * outer_radius
    elements.append(
        PlacedChart(
            name="center_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(width=star_size, height=star_size, channels=1, background=background_gray),
                outer_radius=outer_radius,
                num_sectors=num_sectors,
            ),
            origin=(center_x - outer_radius, center_y - outer_radius),
        )
    )

    elements.append(
        PlacedChart(
            name="upper_color_chart",
            chart=ColorPatchChart(
                canvas=CanvasSpec(width=color_chart_width, height=color_chart_height, channels=3, background=(0, 0, 0)),
                rows=4,
                cols=6,
                patch_size=color_patch_size,
                colors=[color for row in color_chart_values for color in row],
                origin=(0, 0),
            ),
            origin=(color_chart_left, color_chart_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_color_chart",
            chart=ColorPatchChart(
                canvas=CanvasSpec(width=color_chart_width, height=color_chart_height, channels=3, background=(0, 0, 0)),
                rows=4,
                cols=6,
                patch_size=color_patch_size,
                colors=[color for row in lower_color_chart_values for color in row],
                origin=(0, 0),
            ),
            origin=(color_chart_left, lower_color_chart_top),
        )
    )

    elements.append(
        PlacedChart(
            name="top_gray_row",
            chart=GrayscaleStepChart(
                canvas=CanvasSpec(width=row_width, height=patch_size, channels=1, background=background_gray),
                steps=5,
                step_size=(patch_size, patch_size),
                orientation="horizontal",
                values=top_patch_values,
                origin=(0, 0),
            ),
            origin=(row_left, top_row_top),
        )
    )
    elements.append(
        PlacedChart(
            name="bottom_gray_row",
            chart=GrayscaleStepChart(
                canvas=CanvasSpec(width=row_width, height=patch_size, channels=1, background=background_gray),
                steps=5,
                step_size=(patch_size, patch_size),
                orientation="horizontal",
                values=bottom_patch_values,
                origin=(0, 0),
            ),
            origin=(row_left, bottom_row_top),
        )
    )
    elements.append(
        PlacedChart(
            name="left_gray_column",
            chart=GrayscaleStepChart(
                canvas=CanvasSpec(width=patch_size, height=left_column_height, channels=1, background=background_gray),
                steps=5,
                step_size=(patch_size, left_column_patch_height),
                orientation="vertical",
                values=left_column_values,
                origin=(0, 0),
            ),
            origin=(left_column_left, left_column_top),
        )
    )
    elements.append(
        PlacedChart(
            name="right_gray_column",
            chart=GrayscaleStepChart(
                canvas=CanvasSpec(width=patch_size, height=left_column_height, channels=1, background=background_gray),
                steps=5,
                step_size=(patch_size, left_column_patch_height),
                orientation="vertical",
                values=right_column_values,
                origin=(0, 0),
            ),
            origin=(right_column_left, left_column_top),
        )
    )

    elements.append(
        PlacedChart(
            name="left_vertical_color_chart",
            chart=ColorPatchChart(
                canvas=CanvasSpec(width=vertical_color_chart_width, height=vertical_color_chart_height, channels=3, background=(0, 0, 0)),
                rows=8,
                cols=3,
                patch_size=vertical_color_patch_size,
                colors=[color for row in left_vertical_color_values for color in row],
                origin=(0, 0),
            ),
            origin=(left_vertical_color_left, left_vertical_color_top),
        )
    )
    elements.append(
        PlacedChart(
            name="right_vertical_color_chart",
            chart=ColorPatchChart(
                canvas=CanvasSpec(width=vertical_color_chart_width, height=vertical_color_chart_height, channels=3, background=(0, 0, 0)),
                rows=8,
                cols=3,
                patch_size=vertical_color_patch_size,
                colors=[color for row in right_vertical_color_values for color in row],
                origin=(0, 0),
            ),
            origin=(right_vertical_color_left, left_vertical_color_top),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_left_dead_leaves",
            chart=DeadLeavesPatchChart(
                canvas=CanvasSpec(width=dead_leaves_size, height=dead_leaves_size, channels=1, background=background_gray),
                patch_size=(dead_leaves_size, dead_leaves_size),
                origin=(0, 0),
                num_shapes=220,
                radius_range=(6, 26),
                value_range=(90, 165),
                background_value=118,
                seed=0,
            ),
            origin=(dead_leaves_left, dead_leaves_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_right_dead_leaves",
            chart=DeadLeavesPatchChart(
                canvas=CanvasSpec(width=dead_leaves_size, height=dead_leaves_size, channels=1, background=background_gray),
                patch_size=(dead_leaves_size, dead_leaves_size),
                origin=(0, 0),
                num_shapes=220,
                radius_range=(6, 26),
                value_range=(90, 165),
                background_value=118,
                seed=1,
            ),
            origin=(lower_dead_leaves_left, lower_dead_leaves_top),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_left_half_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_left_half_star_square_size,
                    height=upper_left_half_star_square_size,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=outer_radius,
                num_sectors=num_sectors,
                center=(upper_left_half_star_square_size // 2, upper_left_half_star_square_size // 2),
                start_angle_degrees=45.0,
                sweep_angle_degrees=180.0,
                background_value=background_gray,
            ),
            origin=(upper_left_half_star_square_left, upper_left_half_star_square_top),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_right_half_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_left_half_star_square_size,
                    height=upper_left_half_star_square_size,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=outer_radius,
                num_sectors=num_sectors,
                center=(upper_left_half_star_square_size // 2, upper_left_half_star_square_size // 2),
                start_angle_degrees=315.0,
                sweep_angle_degrees=180.0,
                background_value=background_gray,
            ),
            origin=(upper_right_half_star_square_left, upper_right_half_star_square_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_left_half_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_left_half_star_square_size,
                    height=upper_left_half_star_square_size,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=outer_radius,
                num_sectors=num_sectors,
                center=(upper_left_half_star_square_size // 2, upper_left_half_star_square_size // 2),
                start_angle_degrees=135.0,
                sweep_angle_degrees=180.0,
                background_value=background_gray,
            ),
            origin=(lower_left_half_star_square_left, lower_left_half_star_square_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_right_half_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_left_half_star_square_size,
                    height=upper_left_half_star_square_size,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=outer_radius,
                num_sectors=num_sectors,
                center=(upper_left_half_star_square_size // 2, upper_left_half_star_square_size // 2),
                start_angle_degrees=225.0,
                sweep_angle_degrees=180.0,
                background_value=background_gray,
            ),
            origin=(lower_right_half_star_square_left, lower_right_half_star_square_top),
        )
    )
    elements.append(
        PlacedChart(
            name="right_small_full_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_right_small_star_diameter,
                    height=upper_right_small_star_diameter,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=upper_right_small_star_radius,
                num_sectors=num_sectors,
                center=(upper_right_small_star_radius, upper_right_small_star_radius),
                background_value=background_gray,
            ),
            origin=(
                right_small_star_center[0] - upper_right_small_star_radius,
                right_small_star_center[1] - upper_right_small_star_radius,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="left_small_full_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=upper_right_small_star_diameter,
                    height=upper_right_small_star_diameter,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=upper_right_small_star_radius,
                num_sectors=num_sectors,
                center=(upper_right_small_star_radius, upper_right_small_star_radius),
                background_value=background_gray,
            ),
            origin=(
                left_small_star_center[0] - upper_right_small_star_radius,
                left_small_star_center[1] - upper_right_small_star_radius,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_right_small_full_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=lower_right_small_star_diameter,
                    height=lower_right_small_star_diameter,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=lower_right_small_star_radius,
                num_sectors=num_sectors,
                center=(lower_right_small_star_radius, lower_right_small_star_radius),
                background_value=background_gray,
            ),
            origin=(
                lower_right_small_star_center[0] - lower_right_small_star_radius,
                lower_right_small_star_center[1] - lower_right_small_star_radius,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_left_small_full_siemens_star",
            chart=SiemensStarChart(
                canvas=CanvasSpec(
                    width=lower_right_small_star_diameter,
                    height=lower_right_small_star_diameter,
                    channels=1,
                    background=background_gray,
                ),
                outer_radius=lower_right_small_star_radius,
                num_sectors=num_sectors,
                center=(lower_right_small_star_radius, lower_right_small_star_radius),
                background_value=background_gray,
            ),
            origin=(
                lower_left_small_star_center[0] - lower_right_small_star_radius,
                lower_left_small_star_center[1] - lower_right_small_star_radius,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_left_slanted_edge_corner_marker",
            chart=create_corner_marker(
                slanted_corner_marker_size,
                slanted_corner_marker_thickness,
                "top_left",
            ),
            origin=(
                upper_left_slanted_edge_left - slanted_corner_marker_thickness,
                upper_left_slanted_edge_top - slanted_corner_marker_thickness,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_right_slanted_edge_corner_marker",
            chart=create_corner_marker(
                slanted_corner_marker_size,
                slanted_corner_marker_thickness,
                "bottom_right",
            ),
            origin=(
                upper_right_slanted_edge_left + upper_right_slanted_edge_width - slanted_corner_marker_size + slanted_corner_marker_thickness,
                upper_right_slanted_edge_top + upper_right_slanted_edge_height - slanted_corner_marker_size + slanted_corner_marker_thickness,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_left_slanted_edge",
            chart=SlantedEdgeChart(
                canvas=CanvasSpec(
                    width=slanted_edge_width,
                    height=slanted_edge_height,
                    channels=1,
                    background=background_gray,
                ),
                chart_size=(slanted_edge_width, slanted_edge_height),
                edge_angle_degrees=5.0,
                dark_value=210,
                light_value=92,
                background_value=background_gray,
            ),
            origin=(upper_left_slanted_edge_left, upper_left_slanted_edge_top),
        )
    )
    elements.append(
        PlacedChart(
            name="upper_right_slanted_edge",
            chart=SlantedEdgeChart(
                canvas=CanvasSpec(
                    width=upper_right_slanted_edge_width,
                    height=upper_right_slanted_edge_height,
                    channels=1,
                    background=background_gray,
                ),
                chart_size=(upper_right_slanted_edge_width, upper_right_slanted_edge_height),
                edge_angle_degrees=-85.0,
                dark_value=0,
                light_value=255,
                background_value=background_gray,
            ),
            origin=(upper_right_slanted_edge_left, upper_right_slanted_edge_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_left_slanted_edge_corner_marker",
            chart=create_corner_marker(
                slanted_corner_marker_size,
                slanted_corner_marker_thickness,
                "top_left",
            ),
            origin=(
                lower_left_slanted_edge_left - slanted_corner_marker_thickness,
                lower_left_slanted_edge_top - slanted_corner_marker_thickness,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_left_slanted_edge",
            chart=SlantedEdgeChart(
                canvas=CanvasSpec(
                    width=upper_right_slanted_edge_width,
                    height=upper_right_slanted_edge_height,
                    channels=1,
                    background=background_gray,
                ),
                chart_size=(upper_right_slanted_edge_width, upper_right_slanted_edge_height),
                edge_angle_degrees=-85.0,
                dark_value=210,
                light_value=92,
                background_value=background_gray,
            ),
            origin=(lower_left_slanted_edge_left, lower_left_slanted_edge_top),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_right_slanted_edge_corner_marker",
            chart=create_corner_marker(
                slanted_corner_marker_size,
                slanted_corner_marker_thickness,
                "bottom_right",
            ),
            origin=(
                lower_right_slanted_edge_left + slanted_edge_width - slanted_corner_marker_size + slanted_corner_marker_thickness,
                lower_right_slanted_edge_top + slanted_edge_height - slanted_corner_marker_size + slanted_corner_marker_thickness,
            ),
        )
    )
    elements.append(
        PlacedChart(
            name="lower_right_slanted_edge",
            chart=SlantedEdgeChart(
                canvas=CanvasSpec(
                    width=slanted_edge_width,
                    height=slanted_edge_height,
                    channels=1,
                    background=background_gray,
                ),
                chart_size=(slanted_edge_width, slanted_edge_height),
                edge_angle_degrees=5.0,
                dark_value=0,
                light_value=255,
                background_value=background_gray,
            ),
            origin=(lower_right_slanted_edge_left, lower_right_slanted_edge_top),
        )
    )
    for index, (cross_x, cross_y) in enumerate(
        [
            (left_cross_x, top_cross_y),
            (right_cross_x, top_cross_y),
            (left_cross_x, bottom_cross_y),
            (right_cross_x, bottom_cross_y),
        ]
    ):
        elements.append(
            PlacedChart(
                name=f"cross_{index}",
                chart=create_cross_marker(cross_length, cross_thickness),
                origin=(cross_x - cross_length // 2, cross_y - cross_length // 2),
            )
        )

    small_quadrant_centers = [
        (left_macbeth_marker_center_x, color_chart_center_y),
        (right_macbeth_marker_center_x, color_chart_center_y),
        (left_lower_marker_center_x, lower_color_chart_center_y),
        (right_lower_marker_center_x, lower_color_chart_center_y),
        (left_vertical_color_center_x, top_vertical_marker_center_y),
        (left_vertical_color_center_x, bottom_vertical_marker_center_y),
        (right_vertical_color_center_x, top_vertical_marker_center_y),
        (right_vertical_color_center_x, bottom_vertical_marker_center_y),
        *dead_leaves_corner_markers,
        *lower_dead_leaves_corner_markers,
    ]
    for index, (marker_x, marker_y) in enumerate(small_quadrant_centers):
        elements.append(
            PlacedChart(
                name=f"small_quadrant_{index}",
                chart=create_quadrant_marker(macbeth_marker_size),
                origin=(marker_x - macbeth_marker_size // 2, marker_y - macbeth_marker_size // 2),
            )
        )

    for index, (marker_x, marker_y) in enumerate(
        [
            (color_chart_center_x, top_macbeth_marker_center_y),
            (color_chart_center_x, bottom_macbeth_marker_center_y),
            (corner_markers[0][0] + central_star_diameter, corner_markers[0][1]),
            (corner_markers[1][0] - central_star_diameter, corner_markers[1][1]),
            (corner_markers[2][0] + central_star_diameter, corner_markers[2][1]),
            (corner_markers[3][0] - central_star_diameter, corner_markers[3][1]),
            (corner_marker_margin_x + corner_marker_radius, center_y),
            (width - corner_marker_margin_x - corner_marker_radius, center_y),
            (corner_marker_margin_x + corner_marker_radius, corner_markers[0][1] + central_star_diameter),
            (width - corner_marker_margin_x - corner_marker_radius, corner_markers[1][1] + central_star_diameter),
            (corner_marker_margin_x + corner_marker_radius, corner_markers[2][1] - central_star_diameter),
            (width - corner_marker_margin_x - corner_marker_radius, corner_markers[3][1] - central_star_diameter),
            *corner_markers,
        ]
    ):
        elements.append(
            PlacedChart(
                name=f"large_quadrant_{index}",
                chart=create_quadrant_marker(top_macbeth_marker_size),
                origin=(marker_x - top_macbeth_marker_size // 2, marker_y - top_macbeth_marker_size // 2),
            )
        )

    elements.append(
        PlacedChart(
            name="center_quadrant",
            chart=create_quadrant_marker(center_marker_size),
            origin=(center_x - center_marker_size // 2, center_y - center_marker_size // 2),
        )
    )
    for index, (marker_x, marker_y) in enumerate(
        [
            upper_left_half_star_center,
            upper_right_half_star_center,
            lower_left_half_star_center,
            lower_right_half_star_center,
        ]
    ):
        elements.append(
            PlacedChart(
                name=f"half_star_center_quadrant_{index}",
                chart=create_quadrant_marker(center_marker_size),
                origin=(marker_x - center_marker_size // 2, marker_y - center_marker_size // 2),
            )
        )
    for index, (orientation, marker_x, marker_y) in enumerate(upper_right_small_star_corner_marker_specs):
        elements.append(
            PlacedChart(
                name=f"upper_right_small_star_corner_marker_{index}",
                chart=create_corner_marker(center_marker_size, 3, orientation),
                origin=(
                    int(round(marker_x - center_marker_size / 2.0)),
                    int(round(marker_y - center_marker_size / 2.0)),
                ),
            )
        )
    for index, (orientation, marker_x, marker_y) in enumerate(upper_left_small_star_corner_marker_specs):
        elements.append(
            PlacedChart(
                name=f"upper_left_small_star_corner_marker_{index}",
                chart=create_corner_marker(center_marker_size, 3, orientation),
                origin=(
                    int(round(marker_x - center_marker_size / 2.0)),
                    int(round(marker_y - center_marker_size / 2.0)),
                ),
            )
        )
    for index, (orientation, marker_x, marker_y) in enumerate(lower_right_small_star_corner_marker_specs):
        elements.append(
            PlacedChart(
                name=f"lower_right_small_star_corner_marker_{index}",
                chart=create_corner_marker(center_marker_size, 3, orientation),
                origin=(
                    int(round(marker_x - center_marker_size / 2.0)),
                    int(round(marker_y - center_marker_size / 2.0)),
                ),
            )
        )
    for index, (orientation, marker_x, marker_y) in enumerate(lower_left_small_star_corner_marker_specs):
        elements.append(
            PlacedChart(
                name=f"lower_left_small_star_corner_marker_{index}",
                chart=create_corner_marker(center_marker_size, 3, orientation),
                origin=(
                    int(round(marker_x - center_marker_size / 2.0)),
                    int(round(marker_y - center_marker_size / 2.0)),
                ),
            )
        )
    for index, (marker_x, marker_y) in enumerate(
        [
            right_small_star_center,
            left_small_star_center,
            lower_right_small_star_center,
            lower_left_small_star_center,
        ]
    ):
        elements.append(
            PlacedChart(
                name=f"small_full_star_center_quadrant_{index}",
                chart=create_quadrant_marker(center_marker_size),
                origin=(marker_x - center_marker_size // 2, marker_y - center_marker_size // 2),
            )
        )

    composite = CompositeChart(canvas=composite_canvas, elements=elements)

    output = Path("artifacts/te42_outputs/te42_center_star_with_macbeth_chart_1920x1080.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    composite.save(output)
    print(output.resolve())


if __name__ == "__main__":
    main()
