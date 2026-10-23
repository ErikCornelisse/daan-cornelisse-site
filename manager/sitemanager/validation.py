"""Checks that mirror src/content.config.ts, so errors show up in the form
instead of in the site build. Keep the two in step when the schema changes."""

from pathlib import Path

ACCENTS = {
    "purple": "Paars",
    "orange": "Oranje",
    "brown": "Bruin",
}

MAX_IMAGES = 2


def check_work(data: dict, entry_path: Path) -> list[str]:
    errors = []
    for field, label in (("title", "Titel"), ("discipline", "Discipline")):
        if not str(data.get(field) or "").strip():
            errors.append(f"{label} is verplicht.")
    if data.get("accent") not in ACCENTS:
        errors.append("Kies een accentkleur.")
    if not isinstance(data.get("order"), int):
        errors.append("Volgorde moet een heel getal zijn.")
    images = data.get("images") or []
    if not 1 <= len(images) <= MAX_IMAGES:
        errors.append(f"Een werk heeft 1 of {MAX_IMAGES} afbeeldingen.")
    for number, image in enumerate(images, start=1):
        if not str(image.get("alt") or "").strip():
            errors.append(f"Afbeelding {number} heeft een beschrijving (alt-tekst) nodig.")
        if not (entry_path.parent / str(image.get("src", ""))).resolve().is_file():
            errors.append(f"Afbeelding {number} is niet gevonden.")
    return errors


def check_page(data: dict) -> list[str]:
    return [] if str(data.get("title") or "").strip() else ["Titel is verplicht."]


def check_site_data(data: dict) -> list[str]:
    errors = []
    if "@" not in str(data.get("email", "")):
        errors.append("Vul een geldig e-mailadres in.")
    for name, url in (data.get("social") or {}).items():
        if url and not str(url).startswith("https://"):
            errors.append(f"De link voor {name} moet met https:// beginnen.")
    return errors
