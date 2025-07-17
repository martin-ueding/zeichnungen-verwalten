import argparse
import pathlib
import re


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename the PNG originals like the derived JPEG files. The matching is done by the date-id."
    )
    parser.add_argument("path", nargs="+", type=pathlib.Path)
    parser.add_argument("-f", "--force", action="store_true")
    options = parser.parse_args()

    path: pathlib.Path
    for path in options.path:
        if m := re.search(r"^(\d{4}-\d{2}-\d{2}_\d{2,})", path.stem):
            date_id = m.group(1)
            year = date_id[:4]
            pngs = list(
                (
                    pathlib.Path("/home/mu/Bilder/Zeichnungen/Scan-Rohbilder") / year
                ).glob(f"{date_id} *.png")
            )
            if not pngs:
                continue
            assert len(pngs) <= 1, pngs
            png = pngs[0]
            new_path = png.with_stem(path.stem)
            if new_path != png:
                print(f"{new_path.parent}/ {png.name} → {new_path.name}")
                if options.force:
                    assert not new_path.exists()
                    png.rename(new_path)
