"""The editors for the sections of the landing page: hero, section and contact.

Each section is a Markdown file per language in src/content/sections/; the
image (and for the hero the portrait crop and focal point) is shared by both
languages, the texts and image descriptions are per language. What a section
contains and where it sits is in page.json (see layout.py).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml.comments import CommentedMap

from .content import LANGS, Entry, SiteContent

ANCHOR = re.compile(r"^[a-z0-9-]+$")
FOCUS = re.compile(r"^(\d{1,3})% (\d{1,3})%$")
LANG_NAMES = {"nl": "Nederlands", "en": "English"}

# Text fields per kind, as (front matter key, label, required).
TEXT_FIELDS = {
    "hero": [
        ("title", "Titel", True),
        ("subtitle", "Ondertitel", False),
        ("cta", "Linktekst", False),
    ],
    "section": [
        ("title", "Kop", True),
        ("anchor", "Adres-anker (#…)", True),
        ("menuLabel", "Tekst in het menu", False),
    ],
    "contact": [
        ("title", "Kop", True),
        ("anchor", "Adres-anker (#…)", True),
        ("menuLabel", "Tekst in het menu", False),
    ],
}
HAS_BODY = {"hero": False, "section": True, "contact": True}
HAS_IMAGE = {"hero": True, "section": True, "contact": False}


@dataclass
class SectionForm:
    """What the editor shows, and what the form sent back."""

    kind: str
    section_id: str
    texts: dict[str, dict[str, str]]  # lang -> key -> value (incl. "body" and "alt")
    image: str = ""  # src as written in front matter, shared by both languages
    position: str = "left"
    portrait: str = ""
    focus: str = ""
    link: str = ""
    errors: list[str] = field(default_factory=list)


def load(content: SiteContent, ref: dict) -> SectionForm:
    kind, section_id = ref["type"], ref["id"]
    entries = {lang: content.get("sections", lang, section_id) for lang in LANGS}
    texts = {}
    for lang, entry in entries.items():
        data = entry.data if entry else {}
        image = data.get("image") or {}
        texts[lang] = {key: str(data.get(key, "")) for key, _, _ in TEXT_FIELDS[kind]}
        texts[lang]["alt"] = str(image.get("alt", ""))
        texts[lang]["body"] = entry.body.strip("\n") if entry else ""
    base = (entries["nl"] or entries["en"]).data if (entries["nl"] or entries["en"]) else {}
    image = base.get("image") or {}
    return SectionForm(
        kind=kind,
        section_id=section_id,
        texts=texts,
        image=str(image.get("src", "")),
        position=str(image.get("position", "left")),
        portrait=str(base.get("portrait", "")),
        focus=str(base.get("focus", "")),
        link=str(ref.get("link", "")),
    )


def from_form(content: SiteContent, ref: dict, form, uploads: dict[str, str]) -> SectionForm:
    """Read the submitted form; `uploads` maps 'image'/'portrait' to newly saved image srcs."""
    current = load(content, ref)
    kind = ref["type"]
    texts = {}
    for lang in LANGS:
        texts[lang] = {
            key: str(form.get(f"{lang}_{key}", "")).strip() for key, _, _ in TEXT_FIELDS[kind]
        }
        texts[lang]["alt"] = str(form.get(f"{lang}_alt", "")).strip()
        texts[lang]["body"] = str(form.get(f"{lang}_body", "")).replace("\r\n", "\n")
    image = "" if form.get("image_remove") else uploads.get("image", current.image)
    portrait = "" if form.get("portrait_remove") else uploads.get("portrait", current.portrait)
    return SectionForm(
        kind=kind,
        section_id=ref["id"],
        texts=texts,
        image=image,
        position="right" if form.get("position") == "right" else "left",
        portrait=portrait,
        focus=str(form.get("focus", "")).strip(),
        link=str(form.get("link", current.link)),
    )


def check(content: SiteContent, sections: list[dict], values: SectionForm) -> list[str]:
    errors = []
    present = {
        lang: _has_text(values, lang) or content.get("sections", lang, values.section_id)
        for lang in LANGS
    }
    if not present["nl"]:
        errors.append("Nederlands: de tekst is verplicht.")
    for lang in LANGS:
        if not present[lang]:
            continue
        name = LANG_NAMES[lang]
        for key, label, required in TEXT_FIELDS[values.kind]:
            if required and not values.texts[lang][key]:
                errors.append(f"{name}: {label} is verplicht.")
        anchor = values.texts[lang].get("anchor", "")
        if anchor and not ANCHOR.match(anchor):
            errors.append(f"{name}: het anker mag alleen kleine letters, cijfers en - bevatten.")
        elif anchor and anchor in _other_anchors(content, sections, values.section_id, lang):
            errors.append(f"{name}: het anker #{anchor} wordt al door een andere sectie gebruikt.")
        if values.image and not values.texts[lang]["alt"]:
            errors.append(f"{name}: de afbeelding heeft een beschrijving (alt-tekst) nodig.")
    if values.kind == "hero" and not values.image:
        errors.append("Het openingsbeeld heeft een foto nodig.")
    if values.focus:
        match = FOCUS.match(values.focus)
        if not match or int(match.group(1)) > 100 or int(match.group(2)) > 100:
            errors.append("Het brandpunt moet de vorm “50% 35%” hebben (0–100%).")
    return errors


def apply(content: SiteContent, values: SectionForm) -> list[Entry]:
    """Write the values into the entries (not yet saved); returns the entries to save."""
    entries = []
    for lang in LANGS:
        entry = content.get("sections", lang, values.section_id)
        if entry is None:
            if not _has_text(values, lang):
                continue  # no English yet: the site shows the Dutch text
            path = content.path_for("sections", lang, values.section_id)
            entry = Entry("sections", lang, values.section_id, path, CommentedMap(), "")
        data = entry.data
        for key, _, _ in TEXT_FIELDS[values.kind]:
            _set(data, key, values.texts[lang][key])
        if HAS_IMAGE[values.kind]:
            if values.image:
                image = data.get("image") if isinstance(data.get("image"), dict) else None
                if image is None:
                    image = data["image"] = CommentedMap()
                image["src"] = values.image
                image["alt"] = values.texts[lang]["alt"]
                if values.kind == "section" and values.position == "right":
                    image["position"] = "right"
                else:
                    image.pop("position", None)
            else:
                data.pop("image", None)
        if values.kind == "hero":
            _set(data, "portrait", values.portrait)
            _set(data, "focus", values.focus)
        if HAS_BODY[values.kind]:
            entry.body = values.texts[lang]["body"]
        entries.append(entry)
    return entries


def _has_text(values: SectionForm, lang: str) -> bool:
    texts = values.texts[lang]
    return any(texts.get(key) for key in ("title", "body", "subtitle", "cta"))


def _set(data: dict, key: str, value: str) -> None:
    if value:
        data[key] = value
    else:
        data.pop(key, None)


def _other_anchors(content: SiteContent, sections: list[dict], own_id: str, lang: str) -> set[str]:
    """Anchors the other sections use on the page of this language (with Dutch fallback)."""
    anchors = set()
    for section in sections:
        if section["id"] == own_id or section["type"] == "hero":
            continue
        entry = content.get("sections", lang, section["id"]) or content.get(
            "sections", "nl", section["id"]
        )
        if entry and entry.data.get("anchor"):
            anchors.add(str(entry.data["anchor"]))
    return anchors


def image_folder(content: SiteContent) -> Path:
    return content.images_dir / "sections"
