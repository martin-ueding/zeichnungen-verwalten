import abc
import pathlib
import shutil
from typing import Optional


def combine_bits(bits: list[Optional[str]]) -> str:
    return "\n\n".join(bit for bit in bits if bit)


def hashtags_to_string(hashtags: Optional[list[str]]) -> Optional[str]:
    if hashtags:
        return " ".join(f"#{tag}" for tag in hashtags)


class Publisher(abc.ABC):
    @abc.abstractmethod
    def publish(
        self,
        path: pathlib.Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
        hashtags: Optional[list[str]] = None,
    ) -> None:
        pass


class PrintPublisher(Publisher):
    def publish(
        self,
        path: pathlib.Path,
        title: str | None = None,
        description: str | None = None,
        hashtags: list[str] | None = None,
    ) -> None:
        print("Publishing:")
        print(" ", path)
        print(" ", title)
        print(" ", description)
        print(" ", hashtags)


class DirectoryPublisher(Publisher):
    def __init__(self, target: pathlib.Path) -> None:
        self._target = target

    def publish(
        self,
        path: pathlib.Path,
        title: str | None = None,
        description: str | None = None,
        hashtags: list[str] | None = None,
    ) -> None:
        self._target.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, self._target / path.name)
        with open(self._target / path.with_suffix(".txt").name, "w") as f:
            lines = []
            if title:
                lines.append(title)
                lines.append("\n\n")
            if description:
                lines.append(description)
                lines.append("\n\n")
            if hashtags:
                for tag in hashtags:
                    lines.append(tag)
                    lines.append("\n")
            f.write("".join(lines).strip())
