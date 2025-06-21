from zeichnungsverwaltung.meta_extraction import get_filesize_bytes, get_rating, get_tags


def test_get_rating_1() -> None:
    assert get_rating("tests/2024-11-20 Fensterprofil 2.jpg") == 1


def test_get_rating_5() -> None:
    assert get_rating("tests/2024-07-15 Blatt.jpg") == 5


def test_get_tags() -> None:
    assert get_tags("tests/2024-11-20 Fensterprofil 2.jpg") == [
        "Zeichenpapier/Canson One (100 g)"
    ]


def test_get_filesize_bytes() -> int:
    assert get_filesize_bytes("tests/2024-11-20 Fensterprofil 2.jpg") == 224909
