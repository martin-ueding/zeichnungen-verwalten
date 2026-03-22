# JTBD 04: Exporting Images with Optional Watermark and Publish Text

## Job Statement
When images are selected for social publishing, I want a per-target export directory with resized assets and sidecar text, optionally with watermarking for photos, so that I can post to platforms without reliable APIs using a simple manual upload step.

## Primary User
Single-user social publishing workflow across multiple platforms.

## Context
- Selection source: digiKam metadata (color markers, titles, descriptions, tags).
- Configuration source: TOML definitions for export targets.
- Platform constraints: feed-based uploads, no dependable API integration.

## Desired Outcome
For each configured export target:
- image files prepared to target format/size,
- watermark applied only when configured,
- text sidecar generated with title + description + hashtags,
- output stored in a directory ready for manual upload.

## Content Rules
- Drawings: no watermark by default.
- Photos: watermark by default (target-dependent).
- Both: scaled-down export and publish text file.

## Functional Requirements
### FR-1 Target Definition

- TOML supports multiple named targets with:
  - selector (glob/path + raw digiKam color marker),
  - image transform profile (max size, format, quality),
  - watermark profile (none or file path + placement),
  - output directory,
  - sidecar template path (Jinja template producing plain text).

### FR-2 Selection and Filtering

- Scan configured source trees for candidate JPG files.
- Parse metadata and include only images matching target selector.

### FR-3 Transform Pipeline

- Normalize orientation.
- Resize to configured bounds.
- Apply watermark conditionally.
- Write transformed image to target directory using the original source stem.

### FR-4 Sidecar Text

- Create `<stem>.txt` adjacent to exported image.
- Render sidecar content through Jinja templates.
- Output must be plain text suitable for copy/paste into social feed posts.
- Hashtags are provided via description metadata content, not reconstructed from technical tags.

### FR-5 Safety and Repeatability

- Target directory is created if missing.
- Re-run should update changed exports and automatically prune files no longer selected.

## Existing Implementation Baseline
- `zv-publish` already supports:
  - selector by glob and color label,
  - optional watermark application,
  - directory publishing with sidecar text.
- `zv-apply-watermark` is a legacy one-off tool with hardcoded paths.

## Acceptance Criteria
- Running export command produces complete upload-ready folders per target.
- Drawing targets preserve image without watermark unless explicitly enabled.
- Photo targets include watermark according to target config.
- Every exported image has matching text sidecar.
- Files no longer selected by config or metadata are removed from export targets automatically.

## Non-Goals
- Automated browser uploads to social platforms.
- Per-platform API integrations.
- Editing metadata in-place.

## Open Questions

- None for v1.
