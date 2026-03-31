# AGENTS.md — ChartLib

## Project identity

This project is called **ChartLib**.

ChartLib is a Python library for generating **ideal 2D calibration/reference charts** as raster images, together with optional structured annotations.

The library is intended for **computer vision / imaging / synthetic data workflows**.

## Current scope

Follow the project documentation in `docs/` before making code changes.

The authoritative specification files are:

- `docs/01_project_scope_and_architecture.md`
- `docs/02_v1_feature_list.md`
- `docs/03_public_api_proposal.md`
- `docs/04_internal_package_structure.md`
- `docs/05_implementation_order.md`

Read these files first, and treat them as the source of truth for V1.

## V1 goal

Implement a clean and minimal V1 that can generate ideal chart images and annotations.

V1 should focus on:

- simple, explicit, typed design
- deterministic output
- raster rendering
- reusable chart primitives and composition
- optional annotation export

## Explicit non-goals for V1

Do **not** implement or partially implement the following unless explicitly requested:

- camera simulation
- intrinsics / extrinsics support
- perspective projection
- illumination simulation
- blur / optics / PSF
- lens distortion
- sensor noise
- CFA / demosaic / ISP modeling
- physically printed chart workflows
- PDF-first print pipeline
- unnecessary plugin systems
- premature optimization
- over-generalized abstractions

## Design principles

1. Keep the public API **simple, typed, and explicit**.
2. Prefer **dataclasses** and straightforward composition.
3. Build on reusable primitives rather than chart-specific hacks.
4. Separate:
   - specification
   - layout / geometry
   - rendering
   - annotations
5. Keep code readable and easy to review.
6. Avoid cleverness when a direct implementation is sufficient.
7. Do not rewrite unrelated code.
8. Preserve backward-compatible public APIs once introduced.

## Expected output style

When implementing a requested milestone:

1. First summarize the implementation plan briefly.
2. Then implement only the requested scope.
3. Keep patches small and reviewable.
4. Add tests for every new public feature.
5. State any assumptions clearly.

## Preferred technology choices

Use Python with a minimal dependency footprint.

Preferred defaults for V1:

- `numpy` for image arrays and numeric work
- `Pillow` for PNG saving / loading if needed
- `pytest` for tests
- type hints throughout the codebase
- standard library where practical

Avoid heavy frameworks unless explicitly requested.

## Rendering expectations

For V1, prioritize:

- correct geometry
- deterministic raster output
- clear coordinate handling
- predictable annotation generation

Do not introduce advanced rendering systems unless they are clearly needed.

## Annotation expectations

Where relevant, charts should be able to provide structured annotations such as:

- keypoints
- corners
- centers
- bounding boxes
- semantic labels
- chart-space and image-space coordinates where appropriate

Annotations should be simple and machine-friendly.

## Implementation constraints

- Do not implement the whole library at once unless explicitly asked.
- Implement one milestone at a time.
- For the first milestone, prove the architecture with a small vertical slice.
- Prefer a working minimal solution over an elaborate unfinished design.
- Do not add features outside the requested milestone.

## Code quality rules

- Keep modules focused.
- Use clear names.
- Validate user-facing inputs.
- Add docstrings where they improve clarity.
- Add unit tests and simple regression-style checks where appropriate.
- Do not silently swallow errors.
- Raise clear exceptions on invalid specifications.

## When uncertain

If something is ambiguous:

1. Check the spec files in `docs/`.
2. Choose the simpler V1-compatible interpretation.
3. State the assumption in the response or code comments.
4. Do not expand scope on your own.

## First recommended milestone

Unless explicitly told otherwise, begin with a minimal end-to-end slice:

- package skeleton
- project configuration
- core specs
- raster rendering foundation
- one chart type end-to-end
- annotations for that chart
- tests

The preferred first chart is:

- `CheckerboardChart`

Do not implement multiple chart families in the first milestone.
