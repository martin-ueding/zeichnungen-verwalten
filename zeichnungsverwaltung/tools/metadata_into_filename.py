import argparse
import pathlib

from ..drawings_products import filename_from_products
from ..drawings_products import products_from_filename
from ..drawings_products import products_from_metadata
from ..meta_extraction import parse_drawing


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add all product slugs from the file name and Digikam metadata into the filename."
    )
    parser.add_argument("path", nargs="+", type=pathlib.Path)
    parser.add_argument("-f", "--force", action="store_true")
    options = parser.parse_args()

    for path in options.path:
        image = parse_drawing(path)

        p1 = products_from_filename(image.path)
        p2 = products_from_metadata(image.tags)
        products = set(p1) | set(p2)

        new_path = filename_from_products(image.path, products)
        if new_path != image.path:
            print(new_path)
            if options.force:
                assert not new_path.exists()
                image.path.rename(new_path)
