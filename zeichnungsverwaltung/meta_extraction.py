import dataclasses
import itertools
import pathlib
import pprint
from typing import Callable, Optional
import typing
from libxmp.utils import file_to_dict  # type: ignore
import os


@dataclasses.dataclass
class Drawing:
    path: pathlib.Path
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
        return [
            tag.replace("Stifte/", "✏️ ").replace("Zeichenpapier/", "📔 ")
            for tag in self.tags
        ]


def parse_drawing(path: pathlib.Path) -> Drawing:
    xmp_dict = file_to_dict(str(path))
    pprint.pprint(xmp_dict)

    result = Drawing(path)
    result.filesize_bytes = get_filesize_bytes(path)
    result.rating = apply_if_just(
        int, get_scalar(xmp_dict["http://ns.adobe.com/xap/1.0/"], "xmp:Rating")
    )
    result.color_label = get_scalar(
        xmp_dict["http://ns.adobe.com/xap/1.0/"], "xmp:Label"
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
    for key, value, extra in xmp_dict["http://www.digikam.org/ns/1.0/"]:
        if key.startswith("digiKam:TagsList["):
            result.append(value)
    return result


def get_filesize_bytes(path) -> int:
    stat = os.stat(path)
    return stat.st_size


def get_title(xmp_dict: dict, base: str) -> dict[str, str]:
    result = {}
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
