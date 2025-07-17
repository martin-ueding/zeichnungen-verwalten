import dataclasses
import pathlib
from collections.abc import Iterable


@dataclasses.dataclass
class Product:
    slug: str
    manufacturer: str
    product: str

    def __hash__(self) -> int:
        return hash(self.slug)


@dataclasses.dataclass
class Paper(Product):
    weight: int

    def __hash__(self) -> int:
        return hash(self.slug)


@dataclasses.dataclass
class Pen(Product):
    kind: str

    def __hash__(self) -> int:
        return hash(self.slug)


PAPERS = [
    Paper("Cn1512", "Canson", "1557", 120),
    Paper("CnCA13", "Canson", '"C" à grain', 125),
    Paper("CnGS10", "Canson", "Graduate Sketching", 96),
    Paper("CnOA10", "Canson", "One Art Book", 100),
    Paper("CnXS09", "Canson", "XL Sketch", 90),
    Paper("FaBr25", "Fabriano", "Bristol", 250),
    Paper("HaNo19", "Hahnemühle", "Nostalgie", 190),
    Paper("RhTB21", "Rhodia", "Touch Bristol Book", 205),
    Paper("RöPR10", "Rössler Papier", "Parchment Rosé", 100),
    Paper("SaSB14", "Sakura", "Sketch Note Book", 140),
    Paper("SfMF12", "Staufen", "Multifunktionspapier", 120),
    Paper("SIJo12", "Stationary Island", "Plain Journal", 120),
    Paper("XXRe08", "Unbekannt", "Recycling-Kopierpaier", 80),
    Paper("XXKo08", "Unbekannt", "Kopierpaier", 80),
    Paper("XXPS17", "Unbekannt", "Pinkes Skizzenbuch", 170),
]

PENS = [
    Pen("FC900", "Faber-Castell", "Castell 9000", "Holzbleistift"),
    Pen("FCTK9", "Faber-Castell", "TK-9400", "Fallminenstift"),
    Pen("FCTKF", "Faber-Castell", "TK-Fine", "Drückbleistift"),
    Pen("FCPGM", "Faber-Castell", "Pitt Graphite Matt", "Holzbleistift"),
    Pen("LaLog", "Lamy", "Logo", "Drückbleistift"),
    Pen("LyRCa", "Lyra", "Rembrandt Carbon", "Karbonstift"),
    Pen("LyRCh", "Lyra", "Rembrandt Charcoal", "Kohlestift"),
    Pen("LyRSa", "Lyra", "Rembrandt Sanguine", "Sanguine-Stift"),
    Pen("LyRSe", "Lyra", "Rembrandt Sepia", "Sepia-Stift"),
    Pen("MaRaC", "Marco", "Raffiné Charcoal", "Kohlestift"),
    Pen("MaRaG", "Marco", "Raffiné 7001", "Holzbleistift"),
    Pen("StGra", "Staedler", "Unbekannt", "Holzbleistift"),
]

PRODUCTS = PAPERS + PENS


PRODUCT_DICT = {product.slug: product for product in PRODUCTS}


DIGIKAM_TAGS = {
    "Stifte/Lyra Rembrandt Sepia": "LyRSe",
    "Stifte/Lyra Rembrandt Sanguine": "LyRSa",
    "Stifte/Lamy Drückbleistift 0.5 mm": "LaLog",
    "Zeichenpapier/Multifunktionspapier (120 g)": "SfMF12",
    "Zeichenpapier/Rhodia Touch Bristol (205 g)": "RhTB21",
    "Zeichenpapier/Canson 1557 (120 g)": "Cn1512",
    "Zeichenpapier/Staufen Multifunktionspapier (120 g)": "SfMF12",
    "Stifte/Staedtler Bleistift": "StGra",
    "Stifte/Faber-Castell Pitt Graphite Matt": "FCPGM",
    "Zeichenpapier/Sakura Sketchbook (140 g)": "SaSB14",
    "Zeichenpapier/Hahnemühle Nostalgie (190 g)": "HaNo19",
    "Zeichenpapier/Stationary Island Journal (120 g)": "SIJo12",
    "Stifte/Faber-Castell 9000 Bleistift": "FC900",
    "Stifte/Faber-Castell TK 9400": "FCTK9",
    "Stifte/Faber-Castell TK-Fine 9710": "FCTKF",
    "Stifte/Lyra Rembrandt Carbon": "LyRCa",
    "Stifte/Lyra Rembrandt Kohle": "LyRCh",
    "Stifte/Marco Raffiné Graphit": "MaRaG",
    "Stifte/Marco Raffiné Kohle": "MaRaC",
    "Zeichenpapier/Canson C à grain (125 g)": "CnCA13",
    "Zeichenpapier/Canson Graduate Sketching (96 g)": "CnGS10",
    "Zeichenpapier/Canson One (100 g)": "CnOA10",
    "Zeichenpapier/Canson XL Skizze (90 g)": "CnXS09",
    "Zeichenpapier/Kopierpapier (80 g)": "XXKo08",
    "Zeichenpapier/Kopierpapier Recycling (80 g)": "XXRe08",
    "Zeichenpapier/Parchment Rose (100 g)": "RöPR10",
    "Zeichenpapier/Pinkes Skizzenbuch (170 g)": "XXPS17",
}


def products_from_filename(path: pathlib.Path) -> list[Product]:
    words = path.stem.split()
    result = []
    for word in words:
        if word in PRODUCT_DICT:
            result.append(PRODUCT_DICT[word])
    return result


def products_from_metadata(tags: list[str]) -> list[Product]:
    result = []
    for tag in tags:
        if (
            tag.startswith("Kamera/")
            or tag.startswith("Personen/")
            or tag in ["Stifte"]
        ):
            continue
        slug = DIGIKAM_TAGS[tag]
        product = PRODUCT_DICT[slug]
        result.append(product)
    return result


def filename_from_products(
    path: pathlib.Path, products: Iterable[Product]
) -> pathlib.Path:
    words = path.stem.split()
    words = [word for word in words if word not in PRODUCT_DICT]
    words += [
        product.slug
        for product in sorted(
            products, key=lambda product: (str(type(product)), product.slug)
        )
    ]
    return path.with_stem(" ".join(words))
