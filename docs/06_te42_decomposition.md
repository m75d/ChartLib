# TE42 Decomposition

This note captures the practical TE42 structure used to drive the first replication-oriented preset.
It is based on Image Engineering's public TE42 V2 overview/datasheet and is intentionally implementation-focused rather than standards-focused.

## Main Layout Zones

- Top edge band: distributed black/white registration marks for distortion geometry.
- Upper-left quadrant: grayscale/OECF region.
- Upper-right quadrant: large color patch region.
- Central field: primary resolution targets, dominated by one large Siemens star and multiple slanted-edge subcharts.
- Side/upper support regions: smaller Siemens stars and texture/detail targets.
- Lower edge band: repeated registration marks matching the top distribution.
- Full chart plane: neutral gray background used for shading/uniformity evaluation.

## Target Families And Counts

- Grayscale strip: 20 steps.
- Color patch region: 96 patches.
- Siemens stars: 9 total in the reference chart.
  - 1 center star, full circle, full contrast.
  - 4 corner stars, half-circle in the reference.
  - 2 small full-contrast stars.
  - 2 small low-contrast stars.
- Slanted edges: 4 subcharts.
  - two orientations
  - low/high contrast pairings
- Dead-leaves / texture patches: 2 regions.
  - one higher-contrast texture block
  - one lower-contrast texture block
- Registration marks: 10 black/white marks distributed along the top and bottom chart edges.
- Visual appraisal imagery: faces / grass / stones in the reference chart.

## Relative Size And Placement Logic

- The grayscale and color-patch regions are large reference blocks in the upper half.
- The main Siemens star is the dominant central analysis target.
- Smaller Siemens stars are distributed around the chart perimeter and support the main center star.
- Slanted-edge subcharts flank the central structure and appear as repeated paired subtargets rather than isolated single blocks.
- Dead-leaves regions are substantial support targets, not tiny accents.
- Registration marks are structural edge elements, not decorative corner accents.

## Mapping To Current ChartLib Blocks

- Neutral gray background: already supported via `CanvasSpec` / composite background.
- Grayscale strip: already supported by `GrayscaleStepChart`.
- Color patch region: approximately supported by `ColorPatchChart`.
  - Needs a richer explicit 96-patch palette at the preset level.
- Siemens stars: approximately supported by `SiemensStarChart`.
  - Full-circle stars are supported directly.
  - Half-circle corner stars are not supported; these remain approximated by smaller full-circle stars near the corners.
  - Low-contrast stars can be approximated with `dark_value` / `light_value`.
- Slanted edges: approximately supported by `SlantedEdgeChart`.
  - High/low contrast pairings are supported through grayscale value choices.
  - Subchart repetition is handled by `CompositeChart`.
- Dead-leaves regions: approximately supported by `DeadLeavesPatchChart`.
  - High/low contrast variants can be approximated by different `value_range` choices.
- Registration marks: already supported by `RegistrationMarkerChart`.
  - Explicit repeated top/bottom placement is already possible.
- Visual appraisal imagery (faces / grass / stones): missing.
  - Not added in this milestone to avoid introducing photographic/textured content primitives beyond the current synthetic scope.

## Small Missing Capabilities Accepted In This Pass

- A TE42-specific richer preset palette and labels for the 96-patch color region.
- More faithful repeated placement of registration markers and small stars at the preset level.

## Still Approximate In This Pass

- Exact physical dimensions and print geometry.
- Exact half-circle corner stars.
- Exact commercial/standards colorimetry.
- Visual appraisal photographic subtargets.
