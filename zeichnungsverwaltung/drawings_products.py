import dataclasses
import pathlib
from collections.abc import Iterable


@dataclasses.dataclass
class Product:
    slug: str
    manufacturer: str
    product: str
    kind: str | None = None

    def __hash__(self) -> int:
        return hash(self.slug)

    def to_markdown(self) -> str:
        words = []
        if self.manufacturer:
            words.append(f"{self.manufacturer}")
        if self.product:
            words.append(f"_{self.product}_")
        if self.kind:
            words.append(f"({self.kind})")
        return " ".join(words)

    @staticmethod
    def product_type() -> str:
        return "Produkt"


@dataclasses.dataclass
class Paper(Product):
    weight: int

    @staticmethod
    def product_type() -> str:
        return "Zeichenpapier"

    def to_markdown(self) -> str:
        return f"{super().to_markdown()} ({self.weight} g/m²)"


@dataclasses.dataclass
class Pen(Product):
    @staticmethod
    def product_type() -> str:
        return "Stifte"


@dataclasses.dataclass
class Digitizer(Product):
    @staticmethod
    def product_type() -> str:
        return "Digitalisierung"


PAPERS = [
    Paper("ClAl12", "Clairefontaine", "Clairalfa/1952C", 120),
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
    Paper("XXKo08", "", "Kopierpaier", 80),
    Paper("XXPS17", "", "Pinkes Skizzenbuch", 170),
    Paper("XXRe08", "", "Recycling-Kopierpaier", 80),
]

PENS = [
    Pen("FC900", "Faber-Castell", "Castell 9000", "Holzbleistift"),
    Pen("FCPEP", "Faber-Castell", "Precision Eraser Pen", "Radierstift"),
    Pen("FCPer", "Faber-Castell", "Perfection 7056", "Radierstift"),
    Pen("FCPGM", "Faber-Castell", "Pitt Graphite Matt", "Holzbleistift"),
    Pen("FCTK9", "Faber-Castell", "TK-9400", "Fallminenstift"),
    Pen("FCTKF", "Faber-Castell", "TK-Fine", "Drückbleistift"),
    Pen("LaLog", "Lamy", "Logo", "Drückbleistift"),
    Pen("LyRCa", "Lyra", "Rembrandt Carbon", "Karbonstift"),
    Pen("LyRCh", "Lyra", "Rembrandt Charcoal", "Kohlestift"),
    Pen("LyRSa", "Lyra", "Rembrandt Sanguine", "Sanguine-Stift"),
    Pen("LyRSL", "Lyra", "Rembrandt Sepia Light", "Sepia-Stift"),
    Pen("LyRWP", "Lyra", "Rembrandt White Pastel", "Pastel-Stift"),
    Pen("MaRaC", "Marco", "Raffiné Charcoal", "Kohlestift"),
    Pen("MaRaG", "Marco", "Raffiné 7001", "Holzbleistift"),
    Pen("PsPrä", "Pssopp", "Prägestift", "Prägestift"),
    Pen("StGra", "Staedler", "", "Holzbleistift"),
]

OTHERS = [
    Digitizer("BrADS", "Brother", "ADS-1800W", "Einzugsscanner"),
    Digitizer("CaE3D", "Canon", "EOS 350D", "Spiegelreflexkamera"),
    Digitizer("CaPG5", "Canon", "PowerShot G5 X Mark II", "Kompaktkamera"),
    Digitizer("CaPMX", "Canon", "Pixma MX340", "Flachbettscanner"),
]

PRODUCTS = PAPERS + PENS + OTHERS


PRODUCT_DICT = {product.slug: product for product in PRODUCTS}


def products_from_filename(path: pathlib.Path) -> list[Product]:
    words = path.stem.split()
    result = []
    for word in words:
        if word in PRODUCT_DICT:
            result.append(PRODUCT_DICT[word])
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
