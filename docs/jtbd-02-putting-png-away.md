# JTBD 02: Filesystem Consistency (`fsck`)

## Job Statement
When I run an on-demand maintenance check, I want filesystem inconsistencies to be detected and fixable in a controlled way, so that my archive layout stays reliable without hidden automation.

## Primary User
Single-user archive and curation workflow.

## Problem

Legacy behavior still assumes `Scan-Rohbilder/<year>/`, while the actual model uses local `_Scans` folders and may gain more consistency checks over time.

## Target Information Architecture
- Example:
  - `Portraits/<image>.jpg`
  - `Portraits/_Scans/<image>.png`
- Nested example:
  - `Portraits/Bekannte Personen/<image>.jpg`
  - `Portraits/Bekannte Personen/_Scans/<image>.png`

Rule for this check: if a JPG exists, the matching PNG should live in `_Scans` adjacent to that JPG directory.

## Scope
- Scan entire `~/Bilder/Zeichnungen` tree.
- Match only `.png` and `.jpg` files (no `.jpeg` support).
- Include relocation checks and repairs for scan originals.
- Include alignment checks so renamed JPG files propagate to their PNG originals.
- Include canonical tag ordering checks for image metadata tags.
- Include storage summary reporting for JPG/PNG usage and JPG rating buckets.
- Leave all unmatched PNGs untouched (references, assets, other inputs).

## Functional Requirements
### FR-1 Relocate-Scans Matching Logic

- Match by exact stem equality (`foo.png` <-> `foo.jpg`).
- Case sensitivity should follow filesystem behavior (Linux default: case-sensitive).

### FR-2 Relocate-Scans Target Path

- If JPG is at `<dir>/<stem>.jpg`, PNG target is `<dir>/_Scans/<stem>.png`.
- Create `_Scans` directory if missing.

### FR-3 Align-Originals Consistency

- If JPG stem changes but references same date-id image, PNG original shall be renamed to match JPG stem.
- Alignment moves use the same `_Scans` destination policy as relocate-scans.
- Missing originals are reported but not treated as fatal global failure.

### FR-4 Conflict Handling

- If target PNG already exists, treat it as an error for that file.
- Never overwrite existing target files.
- Emit actionable conflict report and continue with other files.

### FR-5 Storage Summary Reporting

- Report total bytes consumed by JPG and PNG files.
- Report JPG byte totals grouped by rating (including unrated bucket).
- Reporting mode must not mutate files.

### FR-6 Canonical Tag Ordering

- Define canonical ordering for relevant image metadata tags.
- `check` mode reports files whose stored tags violate canonical order.
- `fix` mode rewrites tag order to canonical order without altering tag values.

### FR-7 Check and Fix Modes

- `check` mode reports proposed changes and errors without mutating files.
- `fix` mode executes safe file operations, then reports final summary.

## CLI Proposal
- Candidate command: `zv-fsck`.
- Arguments:
  - `--root <path>` (default `~/Bilder/Zeichnungen`)
  - `check` (default command)
  - `fix` (apply safe fixes)
  - optional `--only relocate-scans`
  - optional `--only align-originals`
  - optional `--only canonical-tags`
  - optional `--only storage-summary`

## Acceptance Criteria
- Every PNG with matching JPG ends up in adjacent `_Scans`.
- Unmatched PNG files remain in place.
- Renamed JPG files can be reconciled so matching PNG originals get aligned names.
- Script reports counts: scanned PNGs, matched pairs, moved files, conflicts, skipped.
- Script reports size totals for JPG/PNG and JPG rating groups.
- Script reports canonical-tag violations and can fix them deterministically.
- Running twice in a row in apply mode yields zero additional moves on second run.
- Any existing target PNG is reported as a manual-resolution error and left unchanged.

## Risks
- Duplicate stems in different folders are valid and must not cross-match.
- Existing `_Scans` content may include manually curated files; conflicts must be non-destructive.

## Open Questions

- None for v1.
