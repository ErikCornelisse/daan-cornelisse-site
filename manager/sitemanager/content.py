"""Read and write the site's content files.

Sections, topics and pages are Markdown files with YAML front matter under
src/content/<collection>/<lang>/<slug>.md; the structure of the landing page
is src/content/page.json; contact data is src/data/site.json.
Front matter is handled round-trip, so comments and field order written by
hand survive an edit made in the manager.
"""

import io
import json
import os
from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

LANGS = ("nl", "en")
COLLECTIONS = ("sections", "topics", "pages")
# Pages of their own, outside the landing page.
PAGE_NAMES = ("privacy",)


def _yaml() -> YAML:
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 4096  # never wrap long lines such as alt texts
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


@dataclass
class Entry:
    collection: str
    lang: str
    slug: str
    path: Path
    data: CommentedMap
    body: str

    @property
    def id(self) -> str:
        return f"{self.lang}/{self.slug}"


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("File does not start with front matter")
    end = text.index("\n---\n", 3)
    return text[4 : end + 1], text[end + 5 :]


def parse(path: Path, collection: str, lang: str) -> Entry:
    head, body = split_front_matter(path.read_text(encoding="utf-8"))
    data = _yaml().load(head) or CommentedMap()
    return Entry(collection, lang, path.stem, path, data, body)


def render(entry: Entry) -> str:
    buffer = io.StringIO()
    _yaml().dump(entry.data, buffer)
    body = entry.body.strip("\n")
    return f"---\n{buffer.getvalue()}---\n" + (f"{body}\n" if body else "")


class SiteContent:
    def __init__(self, site_root: Path):
        self.root = site_root
        self.content_dir = site_root / "src" / "content"
        self.site_json = site_root / "src" / "data" / "site.json"
        self.page_json = self.content_dir / "page.json"
        self.images_dir = site_root / "src" / "assets" / "images"

    def path_for(self, collection: str, lang: str, slug: str) -> Path:
        if collection not in COLLECTIONS or lang not in LANGS:
            raise ValueError(f"Unknown collection or language: {collection}/{lang}")
        if not slug or "/" in slug or slug.startswith("."):
            raise ValueError(f"Invalid name: {slug!r}")
        return self.content_dir / collection / lang / f"{slug}.md"

    def slugs(self, collection: str) -> list[str]:
        found = {
            p.stem for lang in LANGS for p in (self.content_dir / collection / lang).glob("*.md")
        }
        return sorted(found)

    def get(self, collection: str, lang: str, slug: str) -> Entry | None:
        path = self.path_for(collection, lang, slug)
        return parse(path, collection, lang) if path.exists() else None

    def save(self, entry: Entry) -> None:
        entry.path.parent.mkdir(parents=True, exist_ok=True)
        entry.path.write_text(render(entry), encoding="utf-8")

    # Structure of the landing page -------------------------------------

    def read_structure(self) -> dict:
        return json.loads(self.page_json.read_text(encoding="utf-8"))

    def write_structure(self, data: dict) -> None:
        text = json.dumps(data, indent="\t", ensure_ascii=False)
        self.page_json.write_text(text + "\n", encoding="utf-8")

    def sections(self) -> list[dict]:
        return self.read_structure()["sections"]

    def topic_ids(self) -> list[str]:
        """Topics in page order, then any topic file not (yet) placed in a section."""
        placed = [t for s in self.sections() for t in s.get("topics", [])]
        return placed + [slug for slug in self.slugs("topics") if slug not in placed]

    def topics(self) -> list[dict[str, Entry | None]]:
        """Each topic as {'nl': Entry|None, 'en': Entry|None}, in page order."""
        return [{lang: self.get("topics", lang, t) for lang in LANGS} for t in self.topic_ids()]

    def place_topic(self, topic_id: str) -> None:
        """Add a new topic at the end of the first section that holds topics."""
        data = self.read_structure()
        sections = [s for s in data["sections"] if s["type"] == "section"]
        target = next((s for s in sections if s.get("topics")), sections[0] if sections else None)
        if target is None:
            raise ValueError("Er is geen sectie om het onderwerp in te plaatsen.")
        target.setdefault("topics", []).append(topic_id)
        self.write_structure(data)

    def bands(self) -> dict[str, str]:
        """Band colour per section ('section:<id>') and per topic ('topic:<id>'), as on the site.

        Mirrors loadPage() in src/lib/page.ts: bands alternate from the first band after
        the hero; a section without own text puts its heading in its first topic's band.
        """
        result, index = {}, 0

        def next_band(forced: str | None = None) -> str:
            nonlocal index
            band = forced or ("paper" if index % 2 else "cream")
            index += 1
            return band

        for section in self.sections():
            if section["type"] == "hero":
                continue
            topics = section.get("topics", [])
            entry = self.get("sections", "nl", section["id"])
            own = section["type"] == "contact" or bool(
                entry and (entry.body.strip() or entry.data.get("image"))
            )
            if own or not topics:
                result[f"section:{section['id']}"] = next_band(section.get("band"))
            for i, topic in enumerate(topics):
                forced = section.get("band") if i == 0 and not (own or not topics) else None
                result[f"topic:{topic}"] = next_band(forced)
            if not (own or not topics):
                result[f"section:{section['id']}"] = result[f"topic:{topics[0]}"]
        return result

    def read_site_data(self) -> dict:
        return json.loads(self.site_json.read_text(encoding="utf-8"))

    def write_site_data(self, data: dict) -> None:
        text = json.dumps(data, indent="\t", ensure_ascii=False)
        self.site_json.write_text(text + "\n", encoding="utf-8")

    def resolve_image(self, entry_path: Path, src: str) -> Path:
        return (entry_path.parent / src).resolve()

    def relative_image_src(self, entry_path: Path, image: Path) -> str:
        """Image path as written in front matter, relative to the entry file."""
        return os.path.relpath(image, entry_path.parent)
