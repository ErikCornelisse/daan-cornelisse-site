"""Changes to the structure of the landing page (src/content/page.json).

Every function takes the structure as loaded from page.json, changes it in
place, and raises LayoutError with a message for Daan when the change is not
allowed. check() applies the same rules as src/lib/page.ts, so a structure
the manager saves always builds. Keep the two in step.
"""

import re

FIXED = ("hero", "contact")  # types that cannot be moved or removed
BANDS = ("cream", "paper")
ID = re.compile(r"^[a-z0-9-]+$")


class LayoutError(ValueError):
    pass


def sections(data: dict) -> list[dict]:
    return data["sections"]


def find(data: dict, section_id: str) -> dict:
    section = next((s for s in sections(data) if s["id"] == section_id), None)
    if section is None:
        raise LayoutError("Deze sectie bestaat niet (meer).")
    return section


def section_of(data: dict, topic_id: str) -> dict | None:
    return next((s for s in sections(data) if topic_id in s.get("topics", [])), None)


def placed_topics(data: dict) -> list[str]:
    return [t for s in sections(data) for t in s.get("topics", [])]


# Rules ---------------------------------------------------------------------


def check(data: dict) -> list[str]:
    """The rules of src/lib/page.ts, as messages for the manager."""
    errors = []
    items = sections(data)
    types = [s.get("type") for s in items]
    if not items or types[0] != "hero" or types.count("hero") != 1:
        errors.append("Het openingsbeeld moet precies één keer voorkomen, als eerste sectie.")
    if not items or types[-1] != "contact" or types.count("contact") != 1:
        errors.append("De contactsectie moet precies één keer voorkomen, als laatste sectie.")
    ids = [s.get("id", "") for s in items]
    for section_id in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"De sectie-id “{section_id}” komt twee keer voor.")
    for section_id in ids:
        if not ID.match(section_id):
            errors.append(f"Ongeldige sectie-id “{section_id}”.")
    topics = placed_topics(data)
    for topic in sorted({t for t in topics if topics.count(t) > 1}):
        errors.append(f"Onderwerp “{topic}” staat in meer dan één sectie.")
    for section in items:
        if section.get("type") in FIXED and section.get("topics"):
            errors.append("Het openingsbeeld en de contactsectie kunnen geen onderwerpen bevatten.")
    for section in items:
        if "band" in section and (section.get("type") == "hero" or section["band"] not in BANDS):
            errors.append(f"Ongeldige achtergrondkleur bij “{section.get('id')}”.")
    link = items[0].get("link") if items else None
    if link and (link not in ids or link == items[0].get("id")):
        errors.append("De link in het openingsbeeld wijst naar een sectie die niet bestaat.")
    return errors


# Sections ------------------------------------------------------------------


def _middle(data: dict, section_id: str) -> tuple[list[dict], int]:
    items = sections(data)
    section = find(data, section_id)
    if section["type"] in FIXED:
        raise LayoutError("Het openingsbeeld en de contactsectie staan vast.")
    return items, items.index(section)


def move_section(data: dict, section_id: str, step: int) -> None:
    """Move a section up (step -1) or down (step +1), never past the hero or contact."""
    items, index = _middle(data, section_id)
    target = index + step
    if target <= 0 or target >= len(items) - 1:
        raise LayoutError("Verder kan deze sectie niet.")
    items[index], items[target] = items[target], items[index]


def toggle_menu(data: dict, section_id: str) -> bool:
    section = find(data, section_id)
    if section["type"] == "hero":
        raise LayoutError("Het openingsbeeld staat niet in het menu.")
    section["menu"] = not section.get("menu", False)
    if not section["menu"]:
        section.pop("menu")
    return section.get("menu", False)


def set_band(data: dict, section_id: str, band: str) -> None:
    """Force a section's background colour ('cream' or 'paper'), or '' for automatic."""
    section = find(data, section_id)
    if section["type"] == "hero":
        raise LayoutError("Het openingsbeeld heeft geen achtergrondkleur.")
    if band and band not in BANDS:
        raise LayoutError("Kies crème, papier of automatisch.")
    if band:
        section["band"] = band
    else:
        section.pop("band", None)


def add_section(data: dict, section_id: str) -> None:
    """Add an empty section just before the contact section."""
    if not ID.match(section_id):
        raise LayoutError("Ongeldige naam voor de sectie.")
    if any(s["id"] == section_id for s in sections(data)):
        raise LayoutError("Er bestaat al een sectie met deze naam.")
    sections(data).insert(len(sections(data)) - 1, {"id": section_id, "type": "section"})


def remove_section(data: dict, section_id: str, topics_to: str | None) -> list[str]:
    """Remove a section; its topics go to `topics_to`, or off the page when None.

    Returns the topics that are no longer on the page.
    """
    items, index = _middle(data, section_id)
    if items[0].get("link") == section_id:
        raise LayoutError(
            "De link in het openingsbeeld wijst naar deze sectie. Kies eerst een ander doel."
        )
    topics = items[index].get("topics", [])
    unplaced = []
    if topics and topics_to:
        target = find(data, topics_to)
        if target["type"] != "section" or target["id"] == section_id:
            raise LayoutError("Kies een andere sectie voor de onderwerpen.")
        target.setdefault("topics", []).extend(topics)
    else:
        unplaced = list(topics)
    del items[index]
    return unplaced


def set_hero_link(data: dict, target: str) -> None:
    hero = sections(data)[0]
    if not target:
        hero.pop("link", None)
        return
    section = find(data, target)
    if section["type"] == "hero":
        raise LayoutError("Het openingsbeeld kan niet naar zichzelf linken.")
    hero["link"] = target


# Topics --------------------------------------------------------------------


def move_topic(data: dict, topic_id: str, step: int) -> None:
    section = section_of(data, topic_id)
    if section is None:
        raise LayoutError("Dit onderwerp staat niet op de pagina.")
    topics = section["topics"]
    index, target = topics.index(topic_id), topics.index(topic_id) + step
    if not 0 <= target < len(topics):
        raise LayoutError("Verder kan dit onderwerp niet binnen deze sectie.")
    topics[index], topics[target] = topics[target], topics[index]


def place_topic(data: dict, topic_id: str, section_id: str) -> None:
    """Put a topic at the end of a section (moving it there if it was elsewhere)."""
    target = find(data, section_id)
    if target["type"] != "section":
        raise LayoutError("Onderwerpen kunnen alleen in een gewone sectie staan.")
    unplace_topic(data, topic_id)
    target.setdefault("topics", []).append(topic_id)


def unplace_topic(data: dict, topic_id: str) -> None:
    """Take a topic off the page; its texts stay and it can be placed again."""
    section = section_of(data, topic_id)
    if section is not None:
        section["topics"].remove(topic_id)
        if not section["topics"]:
            section.pop("topics")
