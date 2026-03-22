# JTBD 01: Scanning and Processing Files

## Job Statement
When I digitize a drawing, I want to scan once and process quickly into a publishable JPEG, so that I can continue with curation and publication instead of spending time on repetitive image prep.

## Primary User
Single-user workflow (owner of this repository).

## Context and Trigger
- Trigger: A physical drawing/sketch is ready to be digitized.
- Environment: Scanner connected locally, CLI available.
- Current tools: `zv-scan` (wrapper around `scanimage`), `zv-process` (wrapper around ImageMagick `magick`), optional manual edit in Krita, metadata in digiKam.

## Desired Outcome
- Each scan session results in:
  - one raw PNG (archival original),
  - one processed JPG (working/publishable image),
  - both kept in predictable locations for follow-up steps.

## Current Behavior (Observed)
- `zv-scan` creates `~/Bilder/Zeichnungen/Scan-<timestamp>.png`.
- `zv-process <png...>` creates `<same-stem>.jpg` next to input PNG.
- `zv-process` then moves PNG to legacy `Scan-Rohbilder/<year>/`.

## Target Behavior
- Keep `zv-scan` behavior stable (it already works well).
- `zv-process` must continue generating JPG with existing default levels.
- `zv-process` must not perform archival relocation anymore; relocation belongs to the maintenance utility from JTBD 02.
- Manual Krita edits remain supported as optional branch (outside automation).

## Functional Requirements
### FR-1 Input and Output

- Accept one or more PNG paths.
- For each PNG, create JPG with same stem in same directory.

### FR-2 Processing Preset

- Keep existing scan presets for `drawing` and `sketch`, plus the existing color mode option.
- Default conversion remains grayscale + level correction currently used.
- Preset values are deterministic and versioned in code (no hidden per-host drift).

### FR-3 Safety

- Never overwrite non-identical target JPG silently.
- Return non-zero exit code on failed conversion.

### FR-4 Compatibility with Metadata Step

- Output JPG must be immediately usable in digiKam for title/description/tags/rating/color marker.
- EXIF/XMP transfer from PNG to JPG is not required in this workflow.

## Non-Goals
- Replacing Krita manual retouching.
- Auto-tagging or AI enhancement.
- Cross-machine profile syncing.

## Acceptance Criteria
- Given a valid PNG, `zv-process` creates a JPG with same stem.
- Batch mode (`zv-process a.png b.png`) processes all inputs or fails with clear error reporting.
- Resulting JPG files are discoverable by existing metadata/publishing scripts.
- `zv-process` no longer depends on `Scan-Rohbilder/<year>/`.

## Dependencies
- Scanner drivers and `scanimage`.
- ImageMagick (`magick`).
- Local drawing directory under `~/Bilder/Zeichnungen`.

## Open Questions

- None for v1.
