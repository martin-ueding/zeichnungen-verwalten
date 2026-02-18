import argparse
import pathlib
import subprocess
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a drawing or a sketch.")
    parser.add_argument(
        "type", choices=["drawing", "sketch"], help="Type of scan to perform."
    )
    parser.add_argument("--color", action="store_true")
    options = parser.parse_args()

    timestamp = int(time.time())

    resolution = 600 if options.type == "drawing" else 300
    mode = "Color" if options.color else "Gray"

    output_dir = pathlib.Path.home() / "Bilder" / "Zeichnungen"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"Scan-{timestamp}.png"

    command = [
        "scanimage",
        f"--device-name=pixma:04A91741_32B3B8",
        "--format=png",
        "--progress",
        "-x",
        "210",
        "-y",
        "297",
        f"--resolution={resolution}",
        f"--mode={mode}",
        f"--output-file={output_file}",
    ]

    subprocess.run(command, check=True)
