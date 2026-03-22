# Spec: Filename Metadata Contract

## Purpose

Define the filename schema as a first-class data contract used across scanning, curation, synchronization, and publishing.

## Why This Is Core

The filename is the durable metadata carrier across tools and directories. It must remain stable and parseable even when sidecar or embedded metadata changes.

## Contract

Each image stem encodes:
- date (`YYYY-MM-DD`),
- image number per day,
- human-readable title,
- normalized product/tag slugs (paper, pens, scanner/digitizer, other material).

## Functional Requirements

### FR-1 Canonical Ordering

- Date and day-sequence appear first.
- Title words remain human-readable in the middle.
- Product/tag slugs are appended by group order `Paper -> Pen -> Digitizer`, then slug order inside each group.

### FR-2 Product Slug Sources

- Slugs are sourced exclusively from filename tokens.
- No slug extraction from digiKam tags is performed.
- Filename normalization preserves all recognized slug tokens and canonicalizes ordering only.

### FR-3 Deterministic Normalization

- Running normalization repeatedly yields identical filename output after first fix.
- Unknown tags do not silently corrupt filename output.
- `zv-fsck` performs filename canonicalization during its full check/fix run.

### FR-4 Safety

- Rename only when computed canonical stem differs from current stem.
- On target collision, fail the file and continue; no overwrite.

### FR-5 Interop with PNG Originals

- When JPG stem changes, corresponding PNG original must be alignable through `zv-fsck align-originals`.

## Scope

- Applies to JPG working files and related PNG originals.
- Uses `.png` and `.jpg` only.

## Non-Goals

- EXIF/XMP as source of truth.
- `.jpeg` support.
- Automatic correction of unknown taxonomy values without explicit mapping.

## Acceptance Criteria

- Canonicalization produces stable stems on repeated runs.
- Product slugs are fully represented from filename tokens alone.
- Existing filename slugs are preserved unless normalized ordering changes.
- Collisions are reported and require manual resolution.

## Open Questions

- None for v1.
