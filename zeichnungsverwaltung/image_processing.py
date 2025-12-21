import pathlib
import subprocess


def downsize_image(
    source: pathlib.Path, target: pathlib.Path, size: int = 2000
) -> None:
    subprocess.run(
        [
            "magick",
            str(source.absolute()),
            "-resize",
            f"{size}x{size}>",
            str(target.absolute()),
        ],
        check=True,
    )


def create_square_thumbnail(
    source: pathlib.Path, target: pathlib.Path, size: int = 500
) -> None:
    subprocess.run(
        [
            "magick",
            str(source.absolute()),
            "-gravity",
            "Center",
            "-extent",
            "1:1",
            "-resize",
            f"{size}x{size}>",
            str(target.absolute()),
        ],
        check=True,
    )
