# CalCharts V1 — Implementation Order for Codex

This document defines the recommended implementation order for V1.

The goal is to maximize early usefulness while keeping architecture clean.

## Guiding principle

Build the smallest vertical slice that proves the architecture:
- one chart type,
- one renderer,
- one annotation path,
- one save path,
- tests.

Do not start by implementing all chart types at once.

## Step 1 — Project skeleton

Codex should first create:
- package directory structure,
- `pyproject.toml`,
- `README.md`,
- a minimal test setup,
- core `__init__.py` exports.

Deliverable:
- importable package
- empty but coherent module layout

## Step 2 — Core specs and utility layer

Implement:
- `CanvasSpec`
- `RenderOptions`
- basic validation helpers
- image save helper

Deliverable:
- validated canvas configuration
- a stable place for rendering parameters

## Step 3 — Minimal scene and annotation representations

Implement:
- lightweight scene container
- basic scene element dataclasses
- `AnnotationBundle`

Keep this simple.
Do not build a complex scene-graph engine in V1.

Deliverable:
- chart builders can return structured geometry and annotations

## Step 4 — Raster renderer

Implement the first working raster renderer that can draw:
- filled rectangles
- circles
- polygons
- simple grayscale / RGB backgrounds

Optional in first pass:
- anti-aliasing via supersampling

Deliverable:
- renderer returns NumPy arrays
- renderer can save PNG via helper

## Step 5 — First vertical slice: checkerboard chart

Implement `CheckerboardChart` end-to-end.

It should support at least:
- rows / cols
- square size or fit-to-canvas behavior
- margin
- foreground / background colors
- rendering to image
- corner annotations

Required tests:
- number of squares
- alternating color pattern
- image size correctness
- annotation count / positions sanity

This is the most important milestone.

## Step 6 — Second chart: circle grid

Implement `CircleGridChart`.

It should support:
- rows / cols
- radius
- spacing
- background / foreground colors
- center annotations

Required tests:
- number of circles
- center positions
- image bounds

## Step 7 — Composite chart container

Implement `CompositeChart`.

This enables composition of multiple chart elements or blocks into one canvas.

Scope for V1:
- ordered placement of already resolved chart blocks or primitive elements
- no complex constraint solving

Deliverable:
- ability to create mixed chart scenes later

## Step 8 — Siemens star

Implement `SiemensStarChart`.

Support:
- center
- radius
- number of sectors
- phase offset if useful

Required tests:
- sector count
- basic geometry validity
- rendered image size

## Step 9 — Grayscale step chart

Implement `GrayscaleStepChart`.

Support:
- number of steps
- horizontal or vertical orientation
- optional custom levels

Required tests:
- step count
- level ordering
- annotation region sanity

## Step 10 — Slanted edge chart

Implement `SlantedEdgeChart`.

Support:
- edge angle
- edge position
- contrast polarity
- optional ROI metadata

Required tests:
- edge geometry sanity
- output size
- deterministic rendering

## Step 11 — Save and convenience API polish

Add or refine:
- `render()`
- `save()`
- `render(return_annotations=True)` or equivalent
- clean public imports
- example scripts

Deliverable:
- a usable V1 library experience

## Step 12 — Regression tests and examples

Add:
- golden-image tests where reasonable
- example notebooks or scripts
- docs for all implemented chart types

This is where Codex should improve reliability instead of expanding scope.

## Out-of-scope for V1

Do not implement yet:
- camera intrinsics / extrinsics
- chart capture simulation
- lens distortion
- optics / PSF
- illumination modeling
- sensor noise / CFA / ISP
- vector exporters
- text-heavy labeling systems
- complex auto-layout engines

## Suggested prompts for Codex by stage

### First prompt

Ask Codex to create only the package skeleton and core specs.
Do not ask for all chart types immediately.

### Second prompt

Ask Codex to implement the checkerboard vertical slice with tests.

### Third prompt

Ask Codex to add circle grid and keep existing public API stable.

This staged workflow will produce better results than one giant request.

## Acceptance criteria for V1

A V1 build is successful if:
- the package installs cleanly,
- each implemented chart renders deterministically,
- annotations are available for relevant features,
- at least checkerboard, circle grid, Siemens star, grayscale step chart, and slanted edge work,
- examples run without manual patching,
- tests pass.

## Recommended immediate next action

Start Codex with only these tasks:
1. create project skeleton,
2. implement core specs,
3. implement checkerboard chart end-to-end with tests.

That is the right first coding milestone.
