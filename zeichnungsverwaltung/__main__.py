import argparse
import pathlib

from .meta_extraction import parse_drawing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)

    options = parser.parse_args()

    drawing = parse_drawing(options.path)
    print()
    print(drawing)
    print()
    print(drawing.get_description("de-DE"))
