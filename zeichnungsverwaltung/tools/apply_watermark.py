import argparse
import pathlib
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply watermark to images.")
    parser.add_argument("files", nargs="+", type=pathlib.Path)
    options = parser.parse_args()

    watermark_path = (
        pathlib.Path.home() / "Dokumente/Zeichnen/Signatur/Signatur-250.png"
    )
    output_dir = (
        pathlib.Path.home() / "Projekte/eigene-webseite/galleries/Bleistiftzeichnungen"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in options.files:
        output_path = output_dir / file_path.name
        command = [
            "magick",
            str(file_path),
            "-resize",
            "1920x1080>",
            "-gravity",
            "SouthEast",
            str(watermark_path),
            "-composite",
            "-quality",
            "90",
            str(output_path),
        ]
        print(f"Processing {file_path} -> {output_path}")
        subprocess.run(command, check=True)
