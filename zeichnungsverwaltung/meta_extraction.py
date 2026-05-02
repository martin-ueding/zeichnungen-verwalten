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

from .drawings_products import products_from_filename


@dataclasses.dataclass
class Image:
    path: pathlib.Path
    date: Optional[datetime.date] = None
    filesize_bytes: Optional[int] = None
    title: dict[str, str] = dataclasses.field(default_factory=dict)
    description: dict[str, str] = dataclasses.field(default_factory=dict)
    rating: Optional[int] = None
    color_label: Optional[str] = None

    def get_description(self, locale: str) -> str:
        description = self.description.get(locale, None) or self.description.get(
            "", None
        )
        tags = "\n".join(sorted(self.emoji_tags()))
        return "\n\n".join(filter(None, [description, tags]))

    def emoji_tags(self) -> list[str]:
        products = products_from_filename(self.path)
        tags = [product.to_markdown() for product in products]
        if self.date:
            tags.append(f"🗓️ {self.date.isoformat()}")
        return tags

    @property
    def slug(self) -> str:
        return self.path.stem.split()[0]


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
    except KeyError:
        pass


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
