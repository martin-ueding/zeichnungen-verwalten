import argparse
import os
import pathlib
from collections.abc import Iterable

import yaml
from tqdm import tqdm

from ..image_processing import downsize_image
from ..meta_extraction import Image
from ..meta_extraction import parse_drawing

BLOG_GALLERY = pathlib.Path("/home/mu/Projekte/eigene-webseite/galleries")


def main() -> None:
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    drawings = [
        parse_drawing(path)
        for path in tqdm(
            pathlib.Path("/home/mu/Bilder/Zeichnungen").rglob("*.jpg"),
            desc="Extracting metadata",
        )
    ]
    drawings.sort(key=lambda drawing: drawing.path.stem, reverse=True)

    publish_to_nikola(
        [drawing for drawing in drawings if drawing.color_label == "Green"],
        "Bleistiftzeichnungen",
    )


def publish_to_nikola(images: Iterable[Image], nikola_gallery: str) -> None:
    gallery_path = BLOG_GALLERY / nikola_gallery
    metadata_for_nikola = []
    for image in images:
        assert "de-DE" in image.title, f"Image {image.path} lacks a title!"
        metadata_for_nikola.append(
            {
                "name": image.path.name,
                "caption": image.title["de-DE"]
                + "\n—\n"
                + image.get_description("de-DE"),
            }
        )

    with open(gallery_path / "metadata.yml", "w") as f:
        yaml.dump_all(metadata_for_nikola, f, explicit_start=True)

    target_files = {drawing.path.name for drawing in images}
    actual_files = {path.name for path in gallery_path.glob("*.jpg")}

    for file in actual_files - target_files:
        os.unlink(gallery_path / file)

    for image in images:
        if image.path.name not in actual_files:
            downsize_image(image.path, gallery_path / image.path.name)
