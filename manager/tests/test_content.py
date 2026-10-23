from pathlib import Path

import pytest

from sitemanager.content import LANGS, SiteContent, parse, render

SITE_ROOT = Path(__file__).resolve().parents[2]
CONTENT = SiteContent(SITE_ROOT)
ALL_FILES = sorted((SITE_ROOT / "src" / "content").glob("*/*/*.md"))


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: str(p.relative_to(SITE_ROOT)))
def test_round_trip_keeps_files_identical(path: Path):
    collection, lang = path.parent.parent.name, path.parent.name
    assert render(parse(path, collection, lang)) == path.read_text(encoding="utf-8")


def test_works_come_in_page_order_with_both_languages():
    works = CONTENT.works()
    orders = [pair["nl"].data["order"] for pair in works]
    assert orders == sorted(orders)
    assert all(pair[lang] is not None for pair in works for lang in LANGS)


def test_relative_image_src_matches_hand_written_paths():
    entry = CONTENT.get("works", "nl", "voor-ik-sluit")
    image = CONTENT.resolve_image(entry.path, entry.data["images"][0]["src"])
    assert image.exists()
    assert CONTENT.relative_image_src(entry.path, image) == entry.data["images"][0]["src"]


def test_rejects_unsafe_names():
    with pytest.raises(ValueError):
        CONTENT.path_for("works", "nl", "../secret")
