import argparse
import pathlib
import tomllib

import jinja2
import markdown

from ..image_processing import create_square_thumbnail
from ..image_processing import downsize_image
from ..meta_extraction import Image
from ..meta_extraction import parse_drawing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=pathlib.Path)
    options = parser.parse_args()

    with open(options.config, "rb") as f:
        config = tomllib.load(f)
    output_path = pathlib.Path(config["output"])
    locale: str = config["locale"]

    jinja_env = jinja2.Environment(
        loader=jinja2.PackageLoader("zeichnungsverwaltung"),
        autoescape=jinja2.select_autoescape(),
    )

    gallery_template = jinja_env.get_template("gallery.html.j2")
    overview_template = jinja_env.get_template("overview.html.j2")

    for gallery_name, gallery_config in config["featured"].items():
        gallery_name: str
        print(gallery_name)

        images: list[Image] = []
        for base in gallery_config["base"]:
            path_generator = (
                pathlib.Path(base).rglob("*.jpg")
                if gallery_config.get("recursive", False)
                else pathlib.Path(base).glob("*.jpg")
            )
            for image_path in path_generator:
                image = parse_drawing(image_path)
                if (
                    image.date is not None
                    and image.color_label == gallery_config["color_label"]
                ):
                    images.append(image)
        images.sort(key=lambda image: image.date, reverse=True)
        print(images)

        template_context = {
            "gallery_title": config["title"],
            "title": gallery_config["title"],
            "description": markdown.markdown(gallery_config["description"]),
            "images": process_images(
                [image for image in images if image.rating == 5],
                locale,
                output_path / gallery_name,
            ),
            "other_images": process_images(
                [image for image in images if image.rating == 3],
                locale,
                output_path / gallery_name,
            ),
        }

        rendered = gallery_template.render(template_context)
        (output_path / gallery_name).mkdir(parents=True, exist_ok=True)
        with open(output_path / gallery_name / "index.html", "w") as f:
            f.write(rendered)

    gallery_template_context = {
        "title": config["title"],
        "description": markdown.markdown(config["description"]),
        "galleries": [
            {
                "title": gallery_config["title"],
                "directory": gallery_name,
                "preview": pathlib.Path(gallery_config["preview"])
                .with_suffix(".webp")
                .name,
            }
            for gallery_name, gallery_config in config["featured"].items()
        ],
    }

    rendered = overview_template.render(gallery_template_context)
    with open(output_path / "index.html", "w") as f:
        f.write(rendered)


def process_images(
    images: list[Image], locale: str, output_path: pathlib.Path
) -> list[dict]:
    for image in images:
        for size, directory in [(2000, "large"), (500, "small")]:
            target: pathlib.Path = (
                output_path / directory / image.path.name
            ).with_suffix(".webp")
            target.parent.mkdir(exist_ok=True, parents=True)
            if not target.exists():
                print(f"Downsampling {image.path.name} …")
                if directory == "small":
                    create_square_thumbnail(image.path, target, size)
                else:
                    downsize_image(image.path, target, size)
    context = []
    for image in images:
        print(image)
        context.append(
            {
                "filename": image.path.with_suffix(".webp").name,
                "title": image.title[locale],
                "description": markdown.markdown(
                    image.description.get(locale, ""), extensions=["pymdownx.magiclink"]
                ),
                "tags": image.tag_dict(),
            }
        )
    return context
