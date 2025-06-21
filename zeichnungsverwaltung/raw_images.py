import collections
import re
import pathlib
import argparse

from zeichnungsverwaltung.meta_extraction import get_filesize_bytes, get_rating


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=pathlib.Path)
    options = parser.parse_args()

    base: pathlib.Path = options.base

    all_raw = (base / "Scan-Rohbilder").rglob("*.png")
    all_edited = base.rglob("*.jpg")

    edited_basenames = {path.name: path for path in all_edited}

    size_per_rating = collections.defaultdict(int)

    for raw_path in all_raw:
        corresponding_edited_name = raw_path.with_suffix(".jpg").name
        if corresponding_edited_name in edited_basenames:
            edited_path = edited_basenames[corresponding_edited_name]
            rating = get_rating(edited_path)
            raw_size = get_filesize_bytes(raw_path)
            size_per_rating[rating] += raw_size
            # print(raw_path.name, rating)
        else:
            print(raw_path.name)

    for rating, raw_size in sorted(size_per_rating.items()):
        print(f"{rating} stars: {raw_size:_} B")


if __name__ == "__main__":
    main()
