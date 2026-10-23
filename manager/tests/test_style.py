"""Style settings: reading and writing tokens and fonts, and the contrast rules."""

import importlib
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sitemanager import style

SITE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def site(tmp_path):
    site = tmp_path / "site"
    for part in ("src/content", "src/data", "src/assets", "src/styles"):
        shutil.copytree(SITE_ROOT / part, site / part)
    shutil.copy(SITE_ROOT / "astro.config.mjs", site / "astro.config.mjs")
    (site / "node_modules").symlink_to(SITE_ROOT / "node_modules")  # for the font samples
    return site


@pytest.fixture()
def client(site, monkeypatch):
    monkeypatch.setenv("SITE_ROOT", str(site))
    import sitemanager.main as main

    return TestClient(importlib.reload(main).app)


def form_values(values: dict[str, str]) -> dict[str, str]:
    """What the style form submits: colours, scale numbers and font keys."""
    form = dict(values)
    for scale in style.SCALES:
        form[scale.token] = str(style.scale_number(values[scale.token]))
    return form


def test_current_site_matches_the_defaults():
    assert style.StyleFiles(SITE_ROOT).read() == style.DEFAULTS


def test_contrast_matches_known_values():
    assert round(style.contrast("#111111", "#ffdda3"), 1) == 14.5
    assert round(style.contrast("#ffffff", "#000000"), 1) == 21.0


def test_writing_changes_only_the_edited_lines(site):
    files = style.StyleFiles(site)
    before = files.tokens_path.read_text().splitlines()
    files.write(style.DEFAULTS | {"color-cream": "#ffe6b8", "scale-text": "1.1"})
    after = files.tokens_path.read_text().splitlines()
    changed = [(a, b) for a, b in zip(before, after) if a != b]
    assert changed == [
        ("\t--color-cream: #ffdda3;", "\t--color-cream: #ffe6b8;"),
        ("\t--scale-text: 1;", "\t--scale-text: 1.1;"),
    ]


def test_fonts_module_matches_the_current_file():
    current = (SITE_ROOT / "src/styles/fonts.ts").read_text()
    heading, body = style.HEADING_FONTS[0], style.BODY_FONTS[0]
    assert style.fonts_module(heading, body) == current


def test_choosing_fonts_updates_tokens_and_imports(site):
    files = style.StyleFiles(site)
    files.write(style.DEFAULTS | {"font-heading": "marcellus", "font-body": "eb-garamond"})
    assert files.read()["font-heading"] == "marcellus"
    assert files.read()["font-body"] == "eb-garamond"
    module = files.fonts_path.read_text()
    assert "@fontsource/marcellus/latin-400.css" in module
    assert "@fontsource/eb-garamond/latin-700.css" in module
    assert "belleza" not in module
    for font in ("marcellus", "eb-garamond"):
        assert (SITE_ROOT / "node_modules/@fontsource" / font / "latin-400.css").exists()


def test_parse_form_rejects_bad_values():
    form = form_values(style.DEFAULTS) | {"color-ink": "red", "scale-text": "3"}
    _, errors = style.parse_form(form, style.DEFAULTS)
    assert len(errors) == 2


def test_unreadable_colours_are_refused(client, site):
    tokens = site / "src/styles/tokens.css"
    before = tokens.read_text()
    form = form_values(style.DEFAULTS) | {"color-accent-orange": "#f0c890"}
    response = client.post("/stijl", data=form)
    assert response.status_code == 422
    assert "Voor ik sluit" in response.text and "minimaal 3:1" in response.text
    assert tokens.read_text() == before


def test_saving_and_restoring_the_original_style(client, site):
    form = form_values(style.DEFAULTS) | {"color-dark": "#202020", "container": "72"}
    assert client.post("/stijl", data=form, follow_redirects=False).status_code == 303
    files = style.StyleFiles(site)
    assert files.read()["color-dark"] == "#202020"
    assert files.read()["container"] == "72rem"

    assert client.post("/stijl/standaard", follow_redirects=False).status_code == 303
    assert files.read() == style.DEFAULTS
    assert files.tokens_path.read_text() == (SITE_ROOT / "src/styles/tokens.css").read_text()


def test_style_page_and_font_samples(client):
    page = client.get("/stijl")
    assert page.status_code == 200
    assert "Tekst op crème" in page.text and "Tenor Sans" in page.text
    assert client.get("/lettertype/marcellus.woff2").status_code == 200
    assert client.get("/lettertype/onbekend.woff2").status_code == 404
