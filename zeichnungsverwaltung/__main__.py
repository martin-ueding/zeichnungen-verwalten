import argparse
import pathlib
import tomllib
import uuid
from typing import Optional

import PIL.Image
import PIL.ImageOps
from tqdm import tqdm

from .meta_extraction import get_hashtags
from .meta_extraction import Image
from .meta_extraction import parse_drawing
from .publishers import DirectoryPublisher
from .publishers import PrintPublisher
from .publishers import Publisher


BASE = pathlib.Path("/home/mu/Bilder/Zeichnungen")


class Formatter:
    def __init__(self, locale: str, include_material: bool = False):
        self.locale = locale
        self.include_material = include_material

    def format(
        self, image: Image
    ) -> tuple[Optional[str], Optional[str], Optional[list[str]]]:
        title = image.title.get(self.locale, None)
        description = image.description.get(self.locale, None)
        if description:
            lines = description.split("\n")
            description = "\n".join(line for line in lines if not line.startswith("#"))
        if self.include_material:
            if not description:
                description = ""
            description += "\n\n"
            description += "\n".join(sorted(image.emoji_tags()))
        hashtags = get_hashtags(image, self.locale)
        return title, description, hashtags


class Selector:
    def __init__(self, glob: str, color_label: Optional[str] = None) -> None:
        self.glob = glob
        self.color_label = color_label

    def get_images(self) -> list[Image]:
        print(f"Get images from {self.glob}.")
        result = []
        for image in tqdm(
            map(parse_drawing, pathlib.Path("/home/mu/Bilder").glob(self.glob)),
            desc="Parse image",
        ):
            if self.color_label and image.color_label != self.color_label:
                continue
            result.append(image)
        result.sort(key=lambda image: image.path.stem)
        return result


class WatermarkApplier:
    def __init__(self, watermark_path: Optional[str] = None) -> None:
        self.watermark_path = watermark_path

    def apply(self, image: Image) -> pathlib.Path:
        pic = PIL.Image.open(image.path)
        pic = PIL.ImageOps.exif_transpose(pic)
        assert pic is not None
        pic = PIL.ImageOps.contain(pic, (2000, 2000))

        if self.watermark_path is not None:
            if pic.mode != "RGBA":
                pic = pic.convert("RGBA")
            watermark_small = PIL.Image.open(self.watermark_path)
            watermark_big = PIL.Image.new("RGBA", pic.size)
            watermark_big.paste(
                watermark_small,
                (
                    pic.size[0] - watermark_small.size[0],
                    pic.size[1] - watermark_small.size[1],
                ),
            )

            pic = PIL.Image.alpha_composite(pic, watermark_big)

            if pic.mode != "RGB":
                pic = pic.convert("RGB")

        dest = pathlib.Path("/tmp") / f"{uuid.uuid4()}.jpg"
        pic.save(dest)
        return dest


class Orchestrator:
    def __init__(
        self,
        selector: Selector,
        publisher: Publisher,
        watermark_applier: WatermarkApplier,
        formatter: Formatter,
    ) -> None:
        self.selector = selector
        self.publisher = publisher
        self.watermark_applier = watermark_applier
        self.formatter = formatter

    def publish_some(self) -> None:
        images_to_publish = self.selector.get_images()
        for image in images_to_publish:
            temp_path = self.watermark_applier.apply(image)
            path_with_watermark = temp_path.with_name(image.path.name)
            temp_path.rename(path_with_watermark)
            title, description, hashtags = self.formatter.format(image)
            self.publisher.publish(path_with_watermark, title, description, hashtags)


def main() -> None:
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    with open("/home/mu/.config/zeichnungsverwaltung.toml", "rb") as f:
        config = tomllib.load(f)

    orchestrators: list[Orchestrator] = []

    for name, data in config.items():
        print(f"Constructing {name}")
        selector = Selector(**data["selector"])
        watermark_applier = WatermarkApplier(**data["watermark_applier"])
        formatter = Formatter(**data["formatter"])

        match data["publisher"]["type"]:
            case "PrintPublisher":
                publisher = PrintPublisher()
            case "DirectoryPublisher":
                publisher = DirectoryPublisher(
                    pathlib.Path(data["publisher"]["target"])
                )
            case _:
                raise NotImplementedError(data["publisher"]["type"])

        orchestrators.append(
            Orchestrator(
                selector=selector,
                publisher=publisher,
                watermark_applier=watermark_applier,
                formatter=formatter,
            )
        )

    for orchestrator in orchestrators:
        orchestrator.publish_some()


def dump() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    parser.add_argument("--locale", default="de-DE")
    options = parser.parse_args()

    drawing = parse_drawing(options.path)
    print(drawing.get_description(options.locale))
