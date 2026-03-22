# JTBD 05: Preparing References with Grid Overlay

## Job Statement

When I collect reference images for drawing practice, I want to generate a gridded reference variant quickly, so that I can transfer proportions onto paper with less estimation error.

## Primary User

Single-user drawing workflow.

## Context and Trigger

- Reference images are stored under `_Vorlagen` folders adjacent to drawing content, similar to `_Scans`.
- Grid preparation is run on demand per reference image.

## Desired Outcome

- For each chosen reference image:
  - a grid-overlay variant is created,
  - a grayscale helper variant is created,
  - original file remains unchanged.

## Functional Requirements

### FR-1 Input

- Accept one image path as input.
- Validate file existence and report clear errors.

### FR-2 Output Naming

- Save grid variant using stem suffix ` (Gitter)`.
- Save grayscale variant using stem suffix ` (grau)`.

### FR-3 Grid Geometry

- Assume A4 proportions and apply a 2 cm grid.
- Handle portrait and landscape inputs.
- Crop to target ratio when needed before grid computation.

### FR-4 Safety

- Never modify the source image in place.
- If output exists, behavior must be explicit (overwrite or error, to be defined in implementation).

## Non-Goals

- Automatic reference discovery and bulk generation in v1.
- Perspective correction or camera calibration.

## Acceptance Criteria

- Running the utility on a valid image creates both expected output files.
- Visual spacing is consistent with intended A4/2 cm model.
- Source file bytes and timestamp remain unchanged.

## Open Questions

- Should existing output files be overwritten by default, or require `--force`?
