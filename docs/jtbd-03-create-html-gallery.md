# JTBD 03: Creating an HTML Gallery

## Job Statement
When selected drawings are marked in digiKam, I want to generate a static HTML gallery from configured selections, so that I can publish curated collections to my blog with minimal manual assembly.

## Primary User
Single-user publisher of drawing galleries.

## Trigger
- Metadata (title/description/tags/rating/color marker) has been curated in digiKam.
- Gallery extraction config is defined in TOML.

## Current Behavior (Observed)
- `zv-gallery <config.toml>`:
  - reads gallery config,
  - scans JPG files from configured bases,
  - filters by color label and rating,
  - generates resized WebP assets and static HTML pages.
- Rendering uses Jinja templates in `zeichnungsverwaltung/html_gallery`.

## Desired Outcome
- Deterministic static output directory containing:
  - landing page (`index.html`),
  - per-gallery pages,
  - per-image pages,
  - downscaled assets (`small`/`large`) suitable for web publishing.

## Functional Requirements
### FR-1 Selection

- Input is the shared TOML config used by gallery and export pipelines.
- Locale for v1 output is `en-US`.
- Selection supports:
  - one or more base directories,
  - optional recursive traversal,
  - required raw digiKam color marker filter values.

### FR-2 Metadata Use

- For each selected JPG:
  - title and description are read from embedded metadata,
  - rating controls featured vs additional buckets,
  - tags/material info can be rendered in image detail pages.

### FR-3 Output Generation

- Generate overview and per-gallery HTML.
- Generate per-image detail pages.
- Generate web-sized assets (thumbnail + large image).

### FR-4 Reproducibility

- Stable sorting order (newest first or explicitly configured order).
- Re-running with same inputs produces equivalent output.

### FR-5 Failure Modes

- Missing required metadata should fail loudly (or be reportable in strict mode).
- Invalid config should produce actionable errors.

## Non-Goals
- Online CMS integration.
- Dynamic server-side rendering.
- Full digiKam database sync.

## Acceptance Criteria
- Given a valid TOML config, gallery build completes without manual post-processing.
- Only color-marked images selected by config appear in output.
- Output is self-contained static files suitable for deployment to blog hosting.
- For each selected gallery, preview image and detail pages are generated.

## Configuration Notes
- Existing code currently expects gallery TOML as explicit CLI argument (`zv-gallery <config>`).
- Publishing/export pipeline (`zv-publish`) currently uses `~/.config/zeichnungsverwaltung.toml`.
- Target state: one unified schema and one shared config file for both flows.

## Open Questions

- None for v1.
