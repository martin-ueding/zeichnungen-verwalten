import argparse
import collections

from ..meta_extraction import find_original, parse_drawing

from ..known_paths import DRAWINGS


def main() -> None:
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    all_edited = DRAWINGS.rglob("*.jpg")

    size_per_rating = collections.defaultdict(int)

    for edited_path in all_edited:
        raw_path = find_original(edited_path)
        if raw_path is None:
            continue
        image = parse_drawing(edited_path)
        if image.filesize_bytes:
            size_per_rating[image.rating or 0] += image.filesize_bytes

    for rating, raw_size in sorted(size_per_rating.items()):
        print(f"{rating} stars: {raw_size:13_} B")
