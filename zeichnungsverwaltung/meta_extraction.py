import collections
import dataclasses
import datetime
import itertools
import os
import pathlib
import re
import typing
from typing import Callable
from typing import Optional

from libxmp.utils import file_to_dict  # type: ignore


@dataclasses.dataclass
class Image:
    path: pathlib.Path
    date: Optional[datetime.date] = None
    filesize_bytes: Optional[int] = None
    title: dict[str, str] = dataclasses.field(default_factory=dict)
    description: dict[str, str] = dataclasses.field(default_factory=dict)
    tags: list[str] = dataclasses.field(default_factory=list)
    rating: Optional[int] = None
    color_label: Optional[str] = None

    def get_description(self, locale: str) -> str:
        description = self.description.get(locale, None) or self.description.get(
            "", None
        )
        tags = "\n".join(sorted(self.emoji_tags()))
        return "\n\n".join(filter(None, [description, tags]))

    def emoji_tags(self) -> list[str]:
        tags = [
            tag.replace("Stifte/", "✏️ ")
            .replace("Zeichenpapier/", "📔 ")
            .replace("Kamera/", "📷 ")
            .replace(" g)", " g/m²)")
            for tag in self.tags
        ]
        if self.date:
            tags.append(f"🗓️ {self.date.isoformat()}")
        return tags

    def tag_dict(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = collections.defaultdict(list)
        for tag in self.tags:
            if tag.startswith("Kamera/"):
                result["Kamera"].append(tag.replace("Kamera/", ""))
            if tag.startswith("Stifte/"):
                result["Stifte"].append(tag.replace("Stifte/", ""))
            if tag.startswith("Zeichenpapier/"):
                result["Zeichenpapier"].append(
                    tag.replace("Zeichenpapier/", "").replace(" g)", " g/m²)")
                )
        result["Datum"].append(self.date.isoformat())
        return result


def get_hashtags(image: Image, locale: str) -> list[str]:
    return [s[1:] for s in re.findall(r"#\w+", image.description.get(locale, ""))]


def parse_drawing(path: pathlib.Path) -> Image:
    xmp_dict = file_to_dict(str(path))
    result = Image(path)
    try:
        result.date = datetime.date.fromisoformat(path.stem[:10])
    except ValueError:
        pass
    result.filesize_bytes = get_filesize_bytes(path)
    result.rating = apply_if_just(
        int, get_scalar(xmp_dict.get("http://ns.adobe.com/xap/1.0/", []), "xmp:Rating")
    )
    result.color_label = get_scalar(
        xmp_dict.get("http://ns.adobe.com/xap/1.0/", []), "xmp:Label"
    )
    result.title = get_title(xmp_dict, "title")
    result.description = get_title(xmp_dict, "description")
    result.tags = get_tags(xmp_dict)
    return result


T1 = typing.TypeVar("T1")
T2 = typing.TypeVar("T2")


def apply_if_just(f: Callable[[T1], T2], maybe: Optional[T1]) -> Optional[T2]:
    if maybe is not None:
        return f(maybe)


def get_scalar(ns_list: list, target: str):
    try:
        for key, value, extra in ns_list:
            if key == target:
                return value
    except KeyError as e:
        pass


def get_tags(xmp_dict: dict) -> list[str]:
    result = []
    for key, value, extra in xmp_dict.get("http://www.digikam.org/ns/1.0/", []):
        if key.startswith("digiKam:TagsList["):
            result.append(value)
    for key, value, extra in xmp_dict.get("http://ns.adobe.com/tiff/1.0/", []):
        if key == "tiff:Model":
            result.append(f"Kamera/{value}")
    return result


def get_filesize_bytes(path) -> int:
    stat = os.stat(path)
    return stat.st_size


def get_title(xmp_dict: dict, base: str) -> dict[str, str]:
    result = {}
    if "http://purl.org/dc/elements/1.1/" not in xmp_dict:
        return result
    ns_dict = {
        key: (value, extra)
        for key, value, extra in xmp_dict["http://purl.org/dc/elements/1.1/"]
    }
    for i in itertools.count(1):
        if f"dc:{base}[{i}]" not in ns_dict:
            break
        if ns_dict[f"dc:{base}[{i}]"][1]["HAS_LANG"]:
            result[ns_dict[f"dc:{base}[{i}]/?xml:lang"][0]] = ns_dict[
                f"dc:{base}[{i}]"
            ][0]
        else:
            result[""] = ns_dict[f"dc:{base}[{i}]"][0]
    return result
