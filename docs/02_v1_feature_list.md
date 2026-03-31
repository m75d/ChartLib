# CalCharts — V1 Feature List

## 1. V1 Objective

Deliver a first usable version of CalCharts that can generate ideal 2D calibration/reference charts as raster images, with deterministic behavior and optional structured annotations.

## 2. Functional Requirements

### 2.1 Canvas configuration
V1 should support:
- arbitrary image width and height in pixels
- grayscale and RGB canvases
- configurable background color / intensity
- deterministic output for identical inputs

### 2.2 Chart types
V1 should include the following built-in chart types:
- Checkerboard chart
- Circle grid chart
- Siemens star chart
- Grayscale step chart
- Slanted-edge chart
- Composite chart container

### 2.3 Composite layout
The library should support composing multiple chart elements on one canvas.
Examples:
- checkerboard + fiducials
- Siemens star + grayscale strip
- multiple independent chart blocks on one image

### 2.4 Rendering
V1 raster rendering should support:
- grayscale output
- RGB output
- PNG save/export
- optional anti-aliasing mode
- explicit dtype policy for output arrays/images

### 2.5 Annotations
Where relevant, chart objects should provide annotations such as:
- checkerboard inner corners
- circle centers
- chart bounding boxes
- polygons/regions for patches
- slanted-edge geometry
- named landmarks or fiducials if present

### 2.6 Validation
V1 should validate:
- illegal dimensions
- inconsistent geometry parameters
- out-of-canvas placement when forbidden
- invalid chart-specific parameters

## 3. Non-Goals for V1

The following are intentionally excluded from V1:
- camera intrinsics/extrinsics
- perspective projection
- illumination simulation
- lens distortion
- blur / PSF / defocus
- sensor noise
- CFA / demosaic / ISP modeling
- PDF/SVG-first print workflows
- exact compliance claims for commercial or formal standards

## 4. Quality Requirements

V1 should aim for:
- clean, typed Python API
- modular internal structure
- deterministic rendering
- solid test coverage
- image regression tests for key charts
- no unnecessary abstraction explosion

## 5. Suggested Priority Order

### Priority 1 — foundation
- canvas spec
- color handling
- base chart abstraction
- scene/element abstraction
- raster renderer
- PNG export

### Priority 2 — first useful charts
- checkerboard
- circle grid
- grayscale step chart
- Siemens star
- slanted-edge chart

### Priority 3 — composition and annotations
- composite chart
- landmark annotations
- region annotations
- masks where natural and cheap to provide

### Priority 4 — robustness
- parameter validation
- image regression tests
- geometry/property tests
- example scripts / docs

## 6. Testing Strategy for V1

### 6.1 Unit tests
Test individual geometry and parameter computations.

### 6.2 Property tests
Examples:
- checkerboard alternates correctly
- circle centers lie on the intended grid
- output stays inside the canvas when requested
- step chart patch counts match parameters

### 6.3 Regression tests
Keep canonical rendered outputs for selected configurations and compare against reference images with controlled tolerances.

### 6.4 API tests
Verify that:
- render returns the correct shapes/types
- annotations are structured and stable
- save writes expected files

## 7. Minimal Viable V1 Deliverable

A strong V1 is considered complete if it provides:
- canvas definition
- raster rendering
- PNG export
- checkerboard
- circle grid
- Siemens star
- grayscale step chart
- slanted-edge chart
- optional annotations
- tests

That is enough to make the library genuinely useful and to validate the architecture.
