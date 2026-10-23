"""The page layout: structure operations, their rules, and the Pagina-indeling screen."""

import copy
import importlib
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sitemanager import layout

SITE_ROOT = Path(__file__).resolve().parents[2]
STRUCTURE = json.loads((SITE_ROOT / "src/content/page.json").read_text())


def ids(data: dict) -> list[str]:
    return [s["id"] for s in data["sections"]]


@pytest.fixture()
def data() -> dict:
    return copy.deepcopy(STRUCTURE)


@pytest.fixture()
def app(tmp_path, monkeypatch):
    site = tmp_path / "site"
    for part in ("src/content", "src/data", "src/assets", "src/styles"):
        shutil.copytree(SITE_ROOT / part, site / part)
    shutil.copy(SITE_ROOT / "astro.config.mjs", site / "astro.config.mjs")
    monkeypatch.setenv("SITE_ROOT", str(site))
    import sitemanager.main as main

    main = importlib.reload(main)
    return main, TestClient(main.app), site


def structure(site: Path) -> dict:
    return json.loads((site / "src/content/page.json").read_text())


# Operations ----------------------------------------------------------------


def test_the_current_structure_follows_the_rules(data):
    assert layout.check(data) == []


def test_sections_move_but_never_past_hero_or_contact(data):
    layout.move_section(data, "over-mij", -1)
    assert ids(data) == ["hero", "over-mij", "mediums", "contact"]
    with pytest.raises(layout.LayoutError):
        layout.move_section(data, "over-mij", -1)
    with pytest.raises(layout.LayoutError):
        layout.move_section(data, "mediums", +1)


def test_hero_and_contact_cannot_be_moved_or_removed(data):
    for section_id in ("hero", "contact"):
        with pytest.raises(layout.LayoutError):
            layout.move_section(data, section_id, +1)
        with pytest.raises(layout.LayoutError):
            layout.remove_section(data, section_id, None)


def test_new_sections_go_before_contact(data):
    layout.add_section(data, "nieuws")
    assert ids(data)[-2:] == ["nieuws", "contact"]
    with pytest.raises(layout.LayoutError):
        layout.add_section(data, "nieuws")


def test_removing_a_section_moves_or_unplaces_its_topics(data):
    layout.add_section(data, "nieuws")
    unplaced = layout.remove_section(data, "mediums", "nieuws")
    assert unplaced == []
    assert layout.find(data, "nieuws")["topics"] == [
        "als-het-licht-even-uitgaat",
        "tijd-voor-max",
        "voor-ik-sluit",
    ]
    assert layout.remove_section(data, "nieuws", None) == layout.placed_topics(STRUCTURE)
    assert layout.placed_topics(data) == []
    assert layout.check(data) == []


def test_the_hero_link_target_cannot_be_removed(data):
    with pytest.raises(layout.LayoutError, match="link in het openingsbeeld"):
        layout.remove_section(data, "over-mij", None)
    layout.set_hero_link(data, "mediums")
    layout.remove_section(data, "over-mij", None)
    assert layout.check(data) == []


def test_topics_move_within_and_between_sections(data):
    layout.move_topic(data, "voor-ik-sluit", -1)
    assert layout.find(data, "mediums")["topics"][1:] == ["voor-ik-sluit", "tijd-voor-max"]
    with pytest.raises(layout.LayoutError):
        layout.move_topic(data, "als-het-licht-even-uitgaat", -1)
    layout.place_topic(data, "tijd-voor-max", "over-mij")
    assert layout.find(data, "over-mij")["topics"] == ["tijd-voor-max"]
    assert "tijd-voor-max" not in layout.find(data, "mediums")["topics"]
    with pytest.raises(layout.LayoutError):
        layout.place_topic(data, "tijd-voor-max", "contact")
    assert layout.check(data) == []


def test_menu_toggle(data):
    assert layout.toggle_menu(data, "mediums") is True
    assert layout.find(data, "mediums")["menu"] is True
    assert layout.toggle_menu(data, "mediums") is False
    assert "menu" not in layout.find(data, "mediums")
    with pytest.raises(layout.LayoutError):
        layout.toggle_menu(data, "hero")


def test_check_finds_broken_structures(data):
    data["sections"].reverse()
    data["sections"][1]["topics"] = ["tijd-voor-max"]
    data["sections"].append({"id": "mediums", "type": "section"})
    messages = " ".join(layout.check(data))
    for fragment in ("openingsbeeld", "contactsectie", "twee keer", "meer dan één sectie"):
        assert fragment in messages


# Screen --------------------------------------------------------------------


def test_layout_screen_shows_sections_topics_and_bands(app):
    _, client, _ = app
    page = client.get("/indeling")
    assert page.status_code == 200
    for text in ("Mediums en Disciplines", "Tijd Voor MAX", "staat vast", "band-dot--paper"):
        assert text in page.text


def test_adding_and_removing_a_section_through_the_screen(app):
    _, client, site = app
    response = client.post(
        "/indeling/sectie",
        data={"nl_title": "Nieuws", "en_title": "News"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert ids(structure(site))[-2:] == ["nieuws", "contact"]
    nl = (site / "src/content/sections/nl/nieuws.md").read_text()
    assert "title: Nieuws" in nl and "anchor: nieuws" in nl
    assert "anchor: news" in (site / "src/content/sections/en/nieuws.md").read_text()

    client.post("/indeling/sectie/nieuws/verwijderen", data={"topics_to": ""})
    assert "nieuws" not in ids(structure(site))
    assert not (site / "src/content/sections/nl/nieuws.md").exists()


def test_a_refused_change_leaves_the_structure_alone(app):
    _, client, site = app
    before = (site / "src/content/page.json").read_text()
    response = client.post("/indeling/sectie/over-mij/verwijderen", data={}, follow_redirects=False)
    assert "fout=" in response.headers["location"]
    assert (site / "src/content/page.json").read_text() == before
    assert (site / "src/content/sections/nl/over-mij.md").exists()


def test_topics_can_leave_the_page_and_be_deleted(app):
    _, client, site = app
    assert (
        "fout="
        in client.post(
            "/indeling/onderwerp/voor-ik-sluit/verwijderen", follow_redirects=False
        ).headers["location"]
    )
    client.post("/indeling/onderwerp/voor-ik-sluit/van-pagina")
    assert "voor-ik-sluit" not in layout.placed_topics(structure(site))
    assert "Niet op de pagina" in client.get("/indeling").text
    client.post("/indeling/onderwerp/voor-ik-sluit/verwijderen")
    assert not (site / "src/content/topics/nl/voor-ik-sluit.md").exists()


def test_new_topic_goes_to_the_chosen_section(app):
    main, client, site = app
    form = {
        "accent": "purple",
        "image_count": "0",
        "image_new_alt_nl": "x",
        "nl_title": "Lijnen",
        "nl_discipline": "Tekenen",
        "nl_body": "Tekst.",
        "section": "over-mij",
    }
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), "black").save(buffer, "PNG")
    files = {"image_new_file": ("lijnen.png", buffer.getvalue(), "image/png")}
    response = client.post("/werken/nieuw", data=form, files=files, follow_redirects=False)
    assert response.status_code == 303
    assert layout.find(structure(site), "over-mij")["topics"] == ["lijnen"]
