import argparse
import pathlib

from ..meta_extraction import parse_drawing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--locale", default="de-DE")
    options = parser.parse_args()

    drawing = parse_drawing(options.path)
    print(drawing.get_description(options.locale))
