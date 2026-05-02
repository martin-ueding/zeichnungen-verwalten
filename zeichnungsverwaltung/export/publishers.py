import abc
import pathlib
import shutil


def combine_bits(bits: list[str | None]) -> str:
    return "\n\n".join(bit for bit in bits if bit)


def hashtags_to_string(hashtags: list[str] | None) -> str | None:
    if hashtags:
        return " ".join(f"#{tag}" for tag in hashtags)
    return None


class Publisher(abc.ABC):
    @abc.abstractmethod
    def publish(
        self,
        path: pathlib.Path,
        title: str | None = None,
        description: str | None = None,
        hashtags: list[str] | None = None,
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
