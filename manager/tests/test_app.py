"""Endpoint tests against a temporary copy of the site's content."""

import importlib
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SITE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def app(tmp_path, monkeypatch):
    site = tmp_path / "site"
    for part in ("src/content", "src/data", "src/assets"):
        shutil.copytree(SITE_ROOT / part, site / part)
    shutil.copy(SITE_ROOT / "astro.config.mjs", site / "astro.config.mjs")
    monkeypatch.setenv("SITE_ROOT", str(site))
    import sitemanager.main as main

    main = importlib.reload(main)
    return main, TestClient(main.app), site


def form_for_work(main, slug: str) -> dict:
    """The form fields the edit page would submit for an unchanged work."""
    view = main.work_view(
        main.content.get("works", "nl", slug), main.content.get("works", "en", slug)
    )
    data = {
        "accent": view["accent"],
        "order": str(view["order"]),
        "image_count": str(len(view["images"])),
    }
    for i, image in enumerate(view["images"]):
        data[f"image_{i}_src"] = image["src"]
        for lang in main.LANGS:
            data[f"image_{i}_alt_{lang}"] = image["alt"][lang]
    for lang, text in view["texts"].items():
        for key, value in text.items():
            data[f"{lang}_{key}"] = value
    return data


def test_overview_lists_works_and_pages(app):
    _, client, _ = app
    page = client.get("/")
    assert page.status_code == 200
    assert "Tijd Voor MAX" in page.text and "Over mij" in page.text


@pytest.mark.parametrize("slug", ["tijd-voor-max", "voor-ik-sluit", "als-het-licht-even-uitgaat"])
def test_saving_an_unchanged_work_keeps_the_files_identical(app, slug):
    main, client, site = app
    files = [site / f"src/content/works/{lang}/{slug}.md" for lang in main.LANGS]
    before = [f.read_text() for f in files]
    response = client.post(
        f"/werken/{slug}", data=form_for_work(main, slug), follow_redirects=False
    )
    assert response.status_code == 303
    assert [f.read_text() for f in files] == before


def test_missing_alt_text_is_refused_and_nothing_is_written(app):
    main, client, site = app
    file = site / "src/content/works/nl/voor-ik-sluit.md"
    before = file.read_text()
    data = form_for_work(main, "voor-ik-sluit") | {"image_0_alt_nl": ""}
    response = client.post("/werken/voor-ik-sluit", data=data)
    assert response.status_code == 422
    assert "beschrijving (alt-tekst)" in response.text
    assert file.read_text() == before


def test_new_work_without_english_creates_only_the_dutch_file(app):
    main, client, site = app
    data = form_for_work(main, "voor-ik-sluit") | {
        "nl_title": "Nieuw werk",
        "nl_body": "Tekst.",
        "en_title": "",
        "en_discipline": "",
        "en_quote": "",
        "en_body": "",
        "order": "",
    }
    response = client.post("/werken/nieuw", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert (site / "src/content/works/nl/nieuw-werk.md").exists()
    assert not (site / "src/content/works/en/nieuw-werk.md").exists()
    assert "order: 4" in (site / "src/content/works/nl/nieuw-werk.md").read_text()


def test_contact_data_is_validated(app):
    _, client, site = app
    before = (site / "src/data/site.json").read_text()
    response = client.post("/contact", data={"email": "geen-adres", "social_instagram": "http://x"})
    assert response.status_code == 422
    assert (site / "src/data/site.json").read_text() == before


def test_images_outside_the_image_folder_are_not_served(app):
    _, client, _ = app
    assert client.get("/afbeelding", params={"pad": "src/data/site.json"}).status_code == 404


def test_uploaded_image_is_scaled_down_and_linked_in_both_languages(app):
    import io

    from PIL import Image

    main, client, site = app
    buffer = io.BytesIO()
    Image.new("RGB", (4000, 3000), "orange").save(buffer, "JPEG")
    data = form_for_work(main, "voor-ik-sluit") | {
        "image_new_alt_nl": "Oranje vlak",
        "image_new_alt_en": "Orange field",
    }
    files = {"image_new_file": ("Mijn Foto.JPG", buffer.getvalue(), "image/jpeg")}
    response = client.post("/werken/voor-ik-sluit", data=data, files=files, follow_redirects=False)
    assert response.status_code == 303
    saved = site / "src/assets/images/works/mijn-foto.jpg"
    assert max(Image.open(saved).size) == 2400
    for lang, alt in (("nl", "Oranje vlak"), ("en", "Orange field")):
        text = (site / f"src/content/works/{lang}/voor-ik-sluit.md").read_text()
        assert "src: ../../../assets/images/works/mijn-foto.jpg" in text
        assert f"alt: {alt}" in text
