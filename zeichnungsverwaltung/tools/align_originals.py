import argparse
import pathlib

from ..meta_extraction import find_original


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename the PNG originals like the derived JPEG files. The matching is done by the date-id."
    )
    parser.add_argument("path", nargs="+", type=pathlib.Path)
    parser.add_argument("-f", "--force", action="store_true")
    options = parser.parse_args()

    path: pathlib.Path
    for path in options.path:
        png = find_original(path)
        if png:
            new_path = path.parent / "_Scans" / (path.stem + ".png")
            if new_path != png:
                print(f"{png} → {new_path}")
                if options.force:
                    assert not new_path.exists()
                    new_path.parent.mkdir(exist_ok=True, parents=True)
                    png.rename(new_path)
