#!/usr/bin/env python

import dataclasses
import re
from typing import Optional
import pathlib
import argparse
import pprint
from libxmp.utils import file_to_dict
import os
import shutil
import yaml

BASE = pathlib.Path("/home/mu/Bilder/Zeichnungen")
BLOG_GALLERY = pathlib.Path(
    "/home/mu/Projekte/eigene-webseite/galleries/Bleistiftzeichnungen"
)
ROOTS = [
    "Architektur & Landschaft",
    "Assoziatives Zeug",
    "Gefühle",
    "Immobilienhaie",
    "Infografiken",
    "Motorrad vor Telekom",
    "Pelikan auf Fahrrad",
    "Portraits",
    "Technik & Material",
    "Übungsbücher",
]


@dataclasses.dataclass
class Drawing:
    date: str
    name: str
    path: pathlib.Path
    rating: Optional[int]
    paper: Optional[str]


def main():
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    drawings: list[Drawing] = []

    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(BASE / root):
            if os.path.basename(dirpath) in ["Vorlagen"]:
                continue

            for filename in filenames:
                if not filename.endswith(".jpg"):
                    continue
                path = pathlib.Path(dirpath) / filename
                date = path.stem[:10]
                name = extract_name(path.stem)
                metadata = file_to_dict(str(path))
                rating = get_rating(metadata)
                paper = get_paper(metadata)
                if rating and rating >= 3:
                    drawings.append(Drawing(date, name, path, rating, paper))

    drawings.sort(key=lambda drawing: drawing.path.stem, reverse=True)

    metadata_for_nikola = []
    for drawing in drawings:
        hints = [drawing.name, drawing.date]
        if drawing.paper:
            hints.append(drawing.paper)
        caption = " | ".join(hints)
        metadata_for_nikola.append({"name": drawing.path.name, "caption": caption})
    print(metadata_for_nikola)

    with open(BLOG_GALLERY / "metadata.yml", "w") as f:
        yaml.dump_all(metadata_for_nikola, f, explicit_start=True)

    target_files = {drawing.path.name for drawing in drawings}
    actual_files = set(BLOG_GALLERY.glob("*.jpg"))

    for file in actual_files - target_files:
        os.unlink(BLOG_GALLERY / file)

    for drawing in drawings:
        if drawing.path.name not in actual_files:
            shutil.copy(drawing.path, BLOG_GALLERY / drawing.path.name)


def get_rating(metadata: dict):
    ns = metadata.get("http://ns.adobe.com/xap/1.0/", [])
    for key, value, _ in ns:
        if key == "xmp:Rating":
            return int(value)


def get_paper(metadata) -> Optional[str]:
    digikam_ns = metadata.get("http://www.digikam.org/ns/1.0/", [])
    for key, value, _ in digikam_ns:
        key: str
        value: str
        if not key.startswith("digiKam:TagsList["):
            continue
        if value.startswith("Zeichenpapier/"):
            return value.replace("Zeichenpapier/", "")


def extract_name(stem: str) -> str:
    name = re.sub(r"^[-\d_]+ ", "", stem)
    paper_codes = r"(XLS|CO|CAG|CGS|HN|SSB)"
    name = re.sub("^" + paper_codes + " ", "", name)
    name = re.sub(" " + paper_codes + "$", "", name)
    return name


if __name__ == "__main__":
    main()
