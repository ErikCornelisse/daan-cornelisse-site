"""The section editors: hero, section and contact."""

import importlib
import io
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from sitemanager import section_forms

SITE_ROOT = Path(__file__).resolve().parents[2]


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


def form_for(main, section_id: str) -> dict:
    """What the editor submits for an unchanged section."""
    ref = main.section_ref(section_id)
    values = section_forms.load(main.content, ref)
    data = {"focus": values.focus, "link": values.link, "position": values.position}
    for lang, texts in values.texts.items():
        for key, value in texts.items():
            data[f"{lang}_{key}"] = value
    return data


def png(width=60, height=40) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "gray").save(buffer, "PNG")
    return buffer.getvalue()


def text(site: Path, lang: str, section_id: str) -> str:
    return (site / f"src/content/sections/{lang}/{section_id}.md").read_text()


@pytest.mark.parametrize("section_id", ["hero", "mediums", "over-mij", "contact"])
def test_saving_an_unchanged_section_keeps_the_files_identical(app, section_id):
    main, client, site = app
    before = [text(site, lang, section_id) for lang in main.LANGS]
    assert client.get(f"/paginas/{section_id}").status_code == 200
    response = client.post(
        f"/paginas/{section_id}", data=form_for(main, section_id), follow_redirects=False
    )
    assert response.status_code == 303, response.text
    assert [text(site, lang, section_id) for lang in main.LANGS] == before


def test_hero_focus_and_link(app):
    main, client, site = app
    data = form_for(main, "hero") | {"focus": "40% 30%", "link": "mediums"}
    assert client.post("/paginas/hero", data=data, follow_redirects=False).status_code == 303
    assert "focus: 40% 30%" in text(site, "nl", "hero")
    assert "focus: 40% 30%" in text(site, "en", "hero")
    structure = json.loads((site / "src/content/page.json").read_text())
    assert structure["sections"][0]["link"] == "mediums"

    response = client.post("/paginas/hero", data=data | {"focus": "150% 30%"})
    assert response.status_code == 422 and "brandpunt" in response.text.lower()


def test_hero_needs_a_photo(app):
    main, client, site = app
    before = text(site, "nl", "hero")
    response = client.post("/paginas/hero", data=form_for(main, "hero") | {"image_remove": "1"})
    # The hero form has no remove option, but a forged request must not leave it without a photo.
    assert response.status_code == 422 and "foto nodig" in response.text
    assert text(site, "nl", "hero") == before


def test_adding_an_image_to_a_section_needs_descriptions(app):
    main, client, site = app
    files = {"image_file": ("Lijnen.png", png(), "image/png")}
    response = client.post("/paginas/mediums", data=form_for(main, "mediums"), files=files)
    assert response.status_code == 422 and "alt-tekst" in response.text

    data = form_for(main, "mediums") | {"nl_alt": "Lijnen", "en_alt": "Lines", "position": "right"}
    files = {"image_file": ("Lijnen.png", png(), "image/png")}
    response = client.post("/paginas/mediums", data=data, files=files, follow_redirects=False)
    assert response.status_code == 303
    nl = text(site, "nl", "mediums")
    assert "src: ../../../assets/images/sections/lijnen" in nl
    assert "alt: Lijnen" in nl and "position: right" in nl
    assert "alt: Lines" in text(site, "en", "mediums")


def test_removing_a_section_image(app):
    main, client, site = app
    data = form_for(main, "over-mij") | {"image_remove": "1"}
    assert client.post("/paginas/over-mij", data=data, follow_redirects=False).status_code == 303
    assert "image:" not in text(site, "nl", "over-mij")
    assert "### Mijn werk" in text(site, "nl", "over-mij")


def test_anchors_must_be_unique_and_valid(app):
    main, client, site = app
    before = text(site, "nl", "over-mij")
    response = client.post(
        "/paginas/over-mij", data=form_for(main, "over-mij") | {"nl_anchor": "contact"}
    )
    assert response.status_code == 422 and "#contact" in response.text
    response = client.post(
        "/paginas/over-mij", data=form_for(main, "over-mij") | {"nl_anchor": "Over Mij"}
    )
    assert response.status_code == 422
    assert text(site, "nl", "over-mij") == before


def test_contact_section_texts(app):
    main, client, site = app
    data = form_for(main, "contact") | {"nl_body": "Mail me gerust.", "nl_menuLabel": "Mail"}
    assert client.post("/paginas/contact", data=data, follow_redirects=False).status_code == 303
    nl = text(site, "nl", "contact")
    assert "menuLabel: Mail" in nl and nl.endswith("Mail me gerust.\n")
    assert "# E-mail address, links and the form come from src/data/site.json." in nl


def test_a_new_section_without_english_gets_no_english_file(app):
    main, client, site = app
    client.post("/indeling/sectie", data={"nl_title": "Nieuws"})
    data = form_for(main, "nieuws") | {"nl_body": "Binnenkort meer."}
    assert client.post("/paginas/nieuws", data=data, follow_redirects=False).status_code == 303
    assert "Binnenkort meer." in text(site, "nl", "nieuws")
    assert not (site / "src/content/sections/en/nieuws.md").exists()
