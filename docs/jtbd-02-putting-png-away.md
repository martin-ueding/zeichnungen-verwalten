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
- Only move PNG files that have a JPG with exact same stem.
- Leave all unmatched PNGs untouched (references, assets, other inputs).

## Functional Requirements
### FR-1 Matching Logic

- Match by exact stem equality (`foo.png` <-> `foo.jpg`).
- Case sensitivity should follow filesystem behavior (Linux default: case-sensitive).

### FR-2 Target Path

- If JPG is at `<dir>/<stem>.jpg`, PNG target is `<dir>/_Scans/<stem>.png`.
- Create `_Scans` directory if missing.

### FR-3 Traversal and Idempotency

- Traverse recursively from configured root.
- Re-running the script should perform no additional changes once files are in correct locations.

### FR-4 Conflict Handling

- If target PNG already exists, treat it as an error for that file.
- Never overwrite existing target files.
- Emit actionable conflict report and continue with other files.

### FR-5 Check and Fix Modes

- Support check mode (default) to print planned moves and errors.
- Support explicit fix mode to execute moves.

## CLI Proposal
- Candidate command: `zv-fsck`.
- Arguments:
  - `--root <path>` (default `~/Bilder/Zeichnungen`)
  - `check` (default command)
  - `fix` (apply safe fixes)
  - optional `--only relocate-scans` for targeted runs

## Acceptance Criteria
- Every PNG with matching JPG ends up in adjacent `_Scans`.
- Unmatched PNG files remain in place.
- Script reports counts: scanned PNGs, matched pairs, moved files, conflicts, skipped.
- Running twice in a row in apply mode yields zero additional moves on second run.
- Any existing target PNG is reported as a manual-resolution error and left unchanged.

## Risks
- Duplicate stems in different folders are valid and must not cross-match.
- Existing `_Scans` content may include manually curated files; conflicts must be non-destructive.

## Open Questions

- Additional `zv-fsck` checks beyond scan relocation are intentionally deferred for now.
