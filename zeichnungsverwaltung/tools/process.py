import argparse
import pathlib
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description="Process raw scanned images.")
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    options = parser.parse_args()

    for path in options.paths:
        print(path)
        output_path = path.with_suffix(".jpg")

        command = [
            "magick",
            str(path),
            "-grayscale",
            "Rec709Luma",
            "-level",
            "43%,98%",
            str(output_path),
        ]
        subprocess.run(command, check=True)
