import argparse
import collections
import pathlib
import re
from dataclasses import dataclass

from ..drawings_products import filename_from_products
from ..drawings_products import products_from_filename
from ..meta_extraction import parse_drawing

DATE_ID_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}_\d{2,})")


@dataclass
class RunContext:
    root: pathlib.Path
    fix: bool
    errors: int = 0
    warnings: int = 0

    def error(self, message: str) -> None:
        self.errors += 1
        print(f"ERROR: {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"WARN: {message}")


def parse_date_id(stem: str) -> str | None:
    match = DATE_ID_PATTERN.search(stem)
    return match.group(1) if match else None


def gather_paths(root: pathlib.Path) -> tuple[list[pathlib.Path], list[pathlib.Path]]:
    def include(path: pathlib.Path) -> bool:
        return path.is_file() and ".dtrash" not in path.parts

    jpg_paths = sorted(path for path in root.rglob("*.jpg") if include(path))
    png_paths = sorted(path for path in root.rglob("*.png") if include(path))
    return jpg_paths, png_paths


def move_file(ctx: RunContext, source: pathlib.Path, target: pathlib.Path, reason: str) -> bool:
    if source == target:
        return False
    if target.exists():
        ctx.error(f"{reason}: target exists, manual resolution needed: {target}")
        return False
    print(f"{reason}: {source} -> {target}")
    if ctx.fix:
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
    return True


def check_relocate_scans(ctx: RunContext) -> None:
    print("\n[relocate-scans]")
    jpg_paths, png_paths = gather_paths(ctx.root)
    jpg_by_stem: dict[str, list[pathlib.Path]] = collections.defaultdict(list)
    for jpg in jpg_paths:
        jpg_by_stem[jpg.stem].append(jpg)

    matched = 0
    moved = 0
    for png in png_paths:
        matches = jpg_by_stem.get(png.stem, [])
        if not matches:
            continue
        if len(matches) > 1:
            choices = ", ".join(str(path) for path in matches)
            ctx.error(f"relocate-scans: ambiguous JPG match for {png}: {choices}")
            continue
        matched += 1
        target = matches[0].parent / "_Scans" / png.name
        if move_file(ctx, png, target, "relocate-scans"):
            moved += 1

    print(f"relocate-scans: matched={matched}, moved={moved}")


def check_align_originals(ctx: RunContext) -> None:
    print("\n[align-originals]")
    jpg_paths, png_paths = gather_paths(ctx.root)
    png_by_date_id: dict[str, list[pathlib.Path]] = collections.defaultdict(list)
    for png in png_paths:
        date_id = parse_date_id(png.stem)
        if date_id:
            png_by_date_id[date_id].append(png)

    matched = 0
    moved = 0
    missing = 0
    for jpg in jpg_paths:
        date_id = parse_date_id(jpg.stem)
        if not date_id:
            continue
        candidates = png_by_date_id.get(date_id, [])
        if not candidates:
            missing += 1
            continue
        matched += 1
        target = jpg.parent / "_Scans" / f"{jpg.stem}.png"
        if target in candidates:
            if len(candidates) > 1:
                ctx.warn(f"align-originals: duplicate originals for {jpg}")
            continue
        if len(candidates) > 1:
            choices = ", ".join(str(path) for path in candidates)
            ctx.error(f"align-originals: ambiguous PNG match for {jpg}: {choices}")
            continue
        source = candidates[0]
        if move_file(ctx, source, target, "align-originals"):
            moved += 1

    print(f"align-originals: matched={matched}, moved={moved}, missing={missing}")


def check_canonical_filename_slugs(ctx: RunContext) -> None:
    print("\n[canonical-filename-slugs]")
    jpg_paths, _ = gather_paths(ctx.root)
    violations = 0
    fixed = 0
    for path in jpg_paths:
        products = set(products_from_filename(path))
        target = filename_from_products(path, products)
        if target == path:
            continue
        violations += 1
        if target.exists():
            ctx.error(
                f"canonical-filename-slugs: target exists, manual resolution needed: {target}"
            )
            continue
        print(f"canonical-filename-slugs: {path} -> {target}")
        if ctx.fix:
            path.rename(target)
            fixed += 1
    print(f"canonical-filename-slugs: violations={violations}, fixed={fixed}")


def check_storage_summary(ctx: RunContext) -> None:
    print("\n[storage-summary]")
    jpg_paths, png_paths = gather_paths(ctx.root)
    jpg_bytes = sum(path.stat().st_size for path in jpg_paths)
    png_bytes = sum(path.stat().st_size for path in png_paths)
    rating_bytes: dict[int, int] = collections.defaultdict(int)
    for jpg in jpg_paths:
        try:
            image = parse_drawing(jpg)
        except Exception as exc:  # pragma: no cover - metadata backend errors
            ctx.warn(f"storage-summary: cannot parse metadata for {jpg}: {exc}")
            continue
        rating = image.rating or 0
        rating_bytes[rating] += image.filesize_bytes or 0

    print(f"jpg total: {jpg_bytes:_} B")
    print(f"png total: {png_bytes:_} B")
    for rating in sorted(rating_bytes):
        print(f"{rating} stars: {rating_bytes[rating]:_} B")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check and repair drawing archive consistency.")
    parser.add_argument("mode", nargs="?", choices=["check", "fix"], default="check")
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=pathlib.Path.home() / "Bilder" / "Zeichnungen",
    )
    options = parser.parse_args()

    ctx = RunContext(root=options.root, fix=(options.mode == "fix"))
    print(f"mode={options.mode} root={ctx.root}")

    if not ctx.root.exists():
        print(f"ERROR: root does not exist: {ctx.root}")
        raise SystemExit(2)

    check_relocate_scans(ctx)
    check_align_originals(ctx)
    check_canonical_filename_slugs(ctx)
    check_storage_summary(ctx)

    print(f"\nsummary: errors={ctx.errors}, warnings={ctx.warnings}")
    if ctx.errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
