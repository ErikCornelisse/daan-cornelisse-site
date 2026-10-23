"""The site manager web app: overview, editing works, pages and contact data,
style settings, the Astro preview, and publishing."""

from pathlib import Path
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ruamel.yaml.comments import CommentedMap
from starlette.datastructures import FormData, UploadFile

from . import layout, style, validation
from .content import LANGS, PAGE_NAMES, Entry, SiteContent
from .images import safe_stem, save_upload
from .publish import Publisher, default_message, latest_deploy, pages_url
from .settings import load_settings
from .site_tools import Preview, last_commit, pending_changes

HERE = Path(__file__).resolve().parent
settings = load_settings()
content = SiteContent(settings.site_root)
preview = Preview(settings.site_root, settings.preview_port, expose=not settings.is_local_only)
publisher = Publisher(settings.site_root, author=settings.publish_author)
style_files = style.StyleFiles(settings.site_root)

app = FastAPI(title="Sitebeheer Daan Cornelisse", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.globals.update(langs=LANGS, accents=validation.ACCENTS)

LANG_NAMES = {"nl": "Nederlands", "en": "English"}
templates.env.globals["lang_names"] = LANG_NAMES


# Editable texts per kind of entry, as (front matter key, label); a dotted key
# is a nested field ("image.alt"). The full section editors follow in step 3
# of the sections plan; until then these screens edit the texts only.
def page_definition(name: str) -> dict | None:
    """What the Pagina's screen edits for a section id or a standalone page."""
    if name in PAGE_NAMES:
        return {
            "collection": "pages",
            "label": "Privacyverklaring",
            "type": "page",
            "fields": [("title", "Titel")],
            "body": True,
        }
    section = next((s for s in content.sections() if s["id"] == name), None)
    if section is None:
        return None
    entry = content.get("sections", "nl", name)
    title = str(entry.data.get("title", name)) if entry else name
    if section["type"] == "hero":
        return {
            "collection": "sections",
            "label": "Openingsbeeld",
            "type": "hero",
            "body": False,
            "fields": [
                ("title", "Titel"),
                ("subtitle", "Ondertitel"),
                ("cta", "Linktekst"),
                ("image.alt", "Beschrijving van de foto"),
            ],
        }
    fields = [("title", "Kop")]
    if entry and entry.data.get("image"):
        fields.append(("image.alt", "Beschrijving van de afbeelding"))
    label = "Contact" if section["type"] == "contact" else title
    return {
        "collection": "sections",
        "label": label,
        "type": section["type"],
        "fields": fields,
        "body": True,
    }


def page_names() -> list[str]:
    return [s["id"] for s in content.sections()] + list(PAGE_NAMES)


def get_field(data: dict, key: str) -> str:
    for part in key.split("."):
        data = data.get(part) if isinstance(data, dict) else None
    return "" if data is None else str(data)


def set_field(data: dict, key: str, value: str) -> None:
    *parents, last = key.split(".")
    for part in parents:
        data = data.setdefault(part, CommentedMap())
    if value:
        data[last] = value
    elif not parents:
        data.pop(last, None)
    else:
        data[last] = value  # nested values such as an alt text stay, so validation can flag them


def redirect(url: str, message: str) -> RedirectResponse:
    return RedirectResponse(f"{url}?bericht={quote(message)}", status_code=303)


def preview_url(request: Request, lang: str = "nl", path: str = "") -> str:
    host = request.url.hostname or "localhost"
    return f"http://{host}:{settings.preview_port}/daan-cornelisse-site/{lang}/{path}"


def image_url(path: Path) -> str:
    return f"/afbeelding?pad={quote(str(path.relative_to(settings.site_root)))}"


# Overview ------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def overview(request: Request, bericht: str = ""):
    return templates.TemplateResponse(
        request,
        "overview.html",
        {
            "message": bericht,
            "works": content.topics(),
            "pages": [
                (
                    name,
                    page_definition(name)["label"],
                    {
                        lang: content.get(page_definition(name)["collection"], lang, name)
                        for lang in LANGS
                    },
                )
                for name in page_names()
            ],
            "changes": pending_changes(settings.site_root),
            "unpushed": publisher.unpushed(),
            "last_commit": last_commit(settings.site_root),
            "preview_running": preview.status(),
            "preview_url": preview_url(request),
        },
    )


@app.get("/afbeelding")
def image(pad: str):
    path = (settings.site_root / pad).resolve()
    if not path.is_relative_to(content.images_dir) or not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


# Preview -------------------------------------------------------------------


@app.post("/voorbeeld/start")
def preview_start():
    return redirect("/", preview.start())


@app.post("/voorbeeld/stop")
def preview_stop():
    return redirect("/", preview.stop())


# Works ---------------------------------------------------------------------


def work_view(nl: Entry | None, en: Entry | None) -> dict:
    """Shape a work for the form: shared fields, images with both alt texts, texts per language."""
    base = nl or en
    images = []
    for index, image in enumerate((base.data.get("images") if base else None) or []):
        src = str(image["src"])
        alt = {}
        for lang, entry in (("nl", nl), ("en", en)):
            entry_images = (entry.data.get("images") if entry else None) or []
            alt[lang] = str(entry_images[index].get("alt", "")) if index < len(entry_images) else ""
        path = content.resolve_image(base.path, src)
        images.append({"src": src, "alt": alt, "url": image_url(path) if path.is_file() else ""})
    texts = {}
    for lang, entry in (("nl", nl), ("en", en)):
        data = entry.data if entry else {}
        texts[lang] = {
            "title": data.get("title", ""),
            "discipline": data.get("discipline", ""),
            "quote": data.get("quote", ""),
            "body": entry.body.strip("\n") if entry else "",
        }
    return {
        "accent": base.data.get("accent", "purple") if base else "purple",
        "images": images,
        "texts": texts,
    }


def render_work(
    request: Request,
    slug: str | None,
    view: dict,
    errors: list[str],
    message: str = "",
    section: str = "",
):
    return templates.TemplateResponse(
        request,
        "work.html",
        {
            "slug": slug,
            "section": section,
            "work": view,
            "errors": errors,
            "message": message,
            "max_images": validation.MAX_IMAGES,
            "preview_url": preview_url(request, "nl", f"#{slug}" if slug else ""),
        },
        status_code=422 if errors else 200,
    )


@app.get("/werken/nieuw", response_class=HTMLResponse)
def new_work(request: Request, sectie: str = ""):
    return render_work(request, None, work_view(None, None), [], section=sectie)


@app.get("/werken/{slug}", response_class=HTMLResponse)
def edit_work(request: Request, slug: str, bericht: str = ""):
    nl, en = content.get("topics", "nl", slug), content.get("topics", "en", slug)
    if not nl and not en:
        raise HTTPException(404)
    return render_work(request, slug, work_view(nl, en), [], bericht)


async def images_from_form(form: FormData, entry_path: Path) -> tuple[list[dict], list[str]]:
    """Existing images (minus removed ones, with replacements) plus an optional new one."""
    images, errors = [], []
    count = int(form.get("image_count", 0))
    rows = [str(i) for i in range(count)] + ["new"]
    for row in rows:
        if form.get(f"image_{row}_remove"):
            continue
        src = str(form.get(f"image_{row}_src", ""))
        upload = form.get(f"image_{row}_file")
        if isinstance(upload, UploadFile) and upload.filename:
            try:
                saved = save_upload(
                    await upload.read(), upload.filename, content.images_dir / "works"
                )
                src = content.relative_image_src(entry_path, saved)
            except ValueError as error:
                errors.append(f"{upload.filename}: {error}")
                continue
        if not src:
            continue
        images.append(
            {
                "src": src,
                "alt": {
                    lang: str(form.get(f"image_{row}_alt_{lang}", "")).strip() for lang in LANGS
                },
            }
        )
    return images, errors


def apply_work(entry: Entry, lang: str, form: FormData, images: list[dict], accent: str) -> None:
    data = entry.data
    for key in ("title", "discipline"):
        data[key] = str(form.get(f"{lang}_{key}", "")).strip()
    data["accent"] = accent
    data["images"] = [
        CommentedMap([("src", image["src"]), ("alt", image["alt"][lang])]) for image in images
    ]
    quote_text = str(form.get(f"{lang}_quote", "")).strip()
    if quote_text:
        data["quote"] = quote_text
    else:
        data.pop("quote", None)
    entry.body = str(form.get(f"{lang}_body", "")).replace("\r\n", "\n")


def new_entry(collection: str, lang: str, slug: str) -> Entry:
    return Entry(
        collection, lang, slug, content.path_for(collection, lang, slug), CommentedMap(), ""
    )


def has_text(form: FormData, lang: str) -> bool:
    return any(str(form.get(f"{lang}_{key}", "")).strip() for key in ("title", "body"))


@app.post("/werken/nieuw", response_class=HTMLResponse)
async def create_work(request: Request):
    return await save_work(request, None)


@app.post("/werken/{slug}", response_class=HTMLResponse)
async def update_work(request: Request, slug: str):
    return await save_work(request, slug)


async def save_work(request: Request, slug: str | None):
    form = await request.form()
    creating = slug is None
    if creating:
        slug = safe_stem(str(form.get("nl_title", "")))
        if content.get("topics", "nl", slug) or content.get("topics", "en", slug):
            slug = f"{slug}-{len(content.slugs('topics')) + 1}"
    entries = {
        lang: content.get("topics", lang, slug) or new_entry("topics", lang, slug) for lang in LANGS
    }

    images, errors = await images_from_form(form, entries["nl"].path)
    accent = str(form.get("accent", ""))

    to_save = []
    for lang, entry in entries.items():
        # A language with no title and no text is left out (to be written or translated later),
        # unless the file already exists.
        if not entry.path.exists() and not has_text(form, lang):
            continue
        apply_work(entry, lang, form, images, accent)
        errors += [
            f"{LANG_NAMES[lang]}: {e}" for e in validation.check_work(entry.data, entry.path)
        ]
        to_save.append(entry)
    if not to_save:
        errors.append("Vul in minstens één taal een titel en tekst in.")

    if errors:
        view = work_view(
            entries["nl"] if entries["nl"].data else None,
            entries["en"] if entries["en"].data else None,
        )
        view["images"] = [
            {
                **image,
                "url": image_url(content.resolve_image(entries["nl"].path, image["src"]))
                if content.resolve_image(entries["nl"].path, image["src"]).is_file()
                else "",
            }
            for image in images
        ]
        return render_work(
            request, None if creating else slug, view, errors, section=str(form.get("section", ""))
        )

    for entry in to_save:
        content.save(entry)
    if creating:
        try:
            content.place_topic(slug, str(form.get("section", "")) or None)
        except layout.LayoutError as error:
            return redirect(f"/werken/{slug}", f"Opgeslagen, maar niet op de pagina gezet: {error}")
    return redirect(f"/werken/{slug}", "Opgeslagen.")


# Pages ---------------------------------------------------------------------


def render_page(request: Request, name: str, values: dict, errors: list[str], message: str = ""):
    definition = page_definition(name)
    anchor = ""
    if definition["collection"] == "sections" and definition["type"] != "hero":
        entry = content.get("sections", "nl", name)
        anchor = f"#{entry.data.get('anchor', '')}" if entry else ""
    return templates.TemplateResponse(
        request,
        "page.html",
        {
            "name": name,
            "label": definition["label"],
            "fields": definition["fields"],
            "has_body": definition["body"],
            "values": values,
            "errors": errors,
            "message": message,
            "preview_url": preview_url(request, "nl", "privacy/" if name == "privacy" else anchor),
        },
        status_code=422 if errors else 200,
    )


@app.get("/paginas/{name}", response_class=HTMLResponse)
def edit_page(request: Request, name: str, bericht: str = ""):
    definition = page_definition(name)
    if definition is None:
        raise HTTPException(404)
    values = {}
    for lang in LANGS:
        entry = content.get(definition["collection"], lang, name)
        values[lang] = (
            {key: get_field(entry.data, key) for key, _ in definition["fields"]} if entry else {}
        )
        values[lang]["body"] = entry.body.strip("\n") if entry else ""
    return render_page(request, name, values, [], bericht)


@app.post("/paginas/{name}", response_class=HTMLResponse)
async def save_page(request: Request, name: str):
    definition = page_definition(name)
    if definition is None:
        raise HTTPException(404)
    form = await request.form()
    errors, entries, values = [], [], {}
    for lang in LANGS:
        entry = content.get(definition["collection"], lang, name) or new_entry(
            definition["collection"], lang, name
        )
        values[lang] = {
            key: str(form.get(f"{lang}_{key}", "")).strip() for key, _ in definition["fields"]
        }
        values[lang]["body"] = str(form.get(f"{lang}_body", "")).replace("\r\n", "\n")
        for key, _ in definition["fields"]:
            set_field(entry.data, key, values[lang][key])
        if definition["body"]:
            entry.body = values[lang]["body"]
        errors += [f"{LANG_NAMES[lang]}: {e}" for e in validation.check_page(entry.data)]
        entries.append(entry)
    if errors:
        return render_page(request, name, values, errors)
    for entry in entries:
        content.save(entry)
    return redirect(f"/paginas/{name}", "Opgeslagen.")


# Page layout ---------------------------------------------------------------


def layout_view() -> dict:
    """Sections with their topics, labels and band colours, for the layout screen."""
    data = content.read_structure()
    bands = content.bands()

    def label(collection: str, entry_id: str) -> dict:
        nl, en = content.get(collection, "nl", entry_id), content.get(collection, "en", entry_id)
        return {
            "title": str((nl or en).data.get("title", entry_id)) if (nl or en) else entry_id,
            "missing_en": en is None,
        }

    rows = []
    for index, section in enumerate(layout.sections(data)):
        rows.append(
            {
                **section,
                **label("sections", section["id"]),
                "band": bands.get(f"section:{section['id']}"),
                "first": index == 1,
                "last": index == len(layout.sections(data)) - 2,
                "topics": [
                    {"id": t, **label("topics", t), "band": bands.get(f"topic:{t}")}
                    for t in section.get("topics", [])
                ],
            }
        )
    placed = set(layout.placed_topics(data))
    unplaced = [{"id": t, **label("topics", t)} for t in content.slugs("topics") if t not in placed]
    return {"sections": rows, "unplaced": unplaced, "link": data["sections"][0].get("link", "")}


@app.get("/indeling", response_class=HTMLResponse)
def page_layout(request: Request, bericht: str = "", fout: str = ""):
    view = layout_view()
    return templates.TemplateResponse(
        request,
        "layout.html",
        {
            **view,
            "targets": [s for s in view["sections"] if s["type"] == "section"],
            "message": bericht,
            "errors": [fout] if fout else [],
            "preview_url": preview_url(request),
        },
    )


def change_layout(change, message: str) -> RedirectResponse:
    """Apply a change to page.json if the result still follows the rules."""
    data = content.read_structure()
    try:
        result = change(data)
    except layout.LayoutError as error:
        return RedirectResponse(f"/indeling?fout={quote(str(error))}", status_code=303)
    problems = layout.check(data)
    if problems:
        return RedirectResponse(f"/indeling?fout={quote(problems[0])}", status_code=303)
    content.write_structure(data)
    return redirect("/indeling", message(result) if callable(message) else message)


@app.post("/indeling/sectie/{section_id}/{action}")
async def section_action(request: Request, section_id: str, action: str):
    form = await request.form()
    if action == "omhoog":
        return change_layout(lambda d: layout.move_section(d, section_id, -1), "Sectie verplaatst.")
    if action == "omlaag":
        return change_layout(lambda d: layout.move_section(d, section_id, +1), "Sectie verplaatst.")
    if action == "menu":
        return change_layout(
            lambda d: layout.toggle_menu(d, section_id),
            lambda on: "In het menu gezet." if on else "Uit het menu gehaald.",
        )
    if action == "verwijderen":
        target = str(form.get("topics_to", "")) or None

        def remove(data):
            return layout.remove_section(data, section_id, target)

        response = change_layout(remove, "Sectie verwijderd.")
        if "fout=" not in response.headers["location"]:
            content.delete("sections", section_id)
        return response
    raise HTTPException(404)


def unique_anchor(base: str) -> str:
    taken = set()
    for section in content.sections():
        for lang in LANGS:
            entry = content.get("sections", lang, section["id"])
            if entry and entry.data.get("anchor"):
                taken.add(str(entry.data["anchor"]))
    anchor, number = base, 2
    while anchor in taken:
        anchor, number = f"{base}-{number}", number + 1
    return anchor


@app.post("/indeling/sectie")
async def add_section(request: Request):
    form = await request.form()
    titles = {lang: str(form.get(f"{lang}_title", "")).strip() for lang in LANGS}
    if not titles["nl"]:
        return RedirectResponse(
            f"/indeling?fout={quote('Geef de nieuwe sectie een Nederlandse kop.')}", status_code=303
        )
    section_id, number = safe_stem(titles["nl"]), 2
    existing = {s["id"] for s in content.sections()} | set(content.slugs("sections"))
    while section_id in existing:
        section_id, number = f"{safe_stem(titles['nl'])}-{number}", number + 1
    response = change_layout(lambda d: layout.add_section(d, section_id), "Sectie toegevoegd.")
    if "fout=" in response.headers["location"]:
        return response
    for lang, title in titles.items():
        if title:
            entry = new_entry("sections", lang, section_id)
            entry.data["title"] = title
            entry.data["anchor"] = unique_anchor(safe_stem(title))
            content.save(entry)
    return redirect(f"/paginas/{section_id}", "Sectie toegevoegd. Vul hier de tekst in.")


@app.post("/indeling/openingsbeeld/link")
async def hero_link(request: Request):
    form = await request.form()
    target = str(form.get("target", ""))
    return change_layout(lambda d: layout.set_hero_link(d, target), "Link aangepast.")


@app.post("/indeling/onderwerp/{topic_id}/{action}")
async def topic_action(request: Request, topic_id: str, action: str):
    form = await request.form()
    if action == "omhoog":
        return change_layout(lambda d: layout.move_topic(d, topic_id, -1), "Onderwerp verplaatst.")
    if action == "omlaag":
        return change_layout(lambda d: layout.move_topic(d, topic_id, +1), "Onderwerp verplaatst.")
    if action == "naar":
        target = str(form.get("section", ""))
        return change_layout(
            lambda d: layout.place_topic(d, topic_id, target), "Onderwerp verplaatst."
        )
    if action == "van-pagina":
        return change_layout(
            lambda d: layout.unplace_topic(d, topic_id),
            "Onderwerp van de pagina gehaald. De teksten blijven bewaard.",
        )
    if action == "verwijderen":
        if topic_id in layout.placed_topics(content.read_structure()):
            return RedirectResponse(
                f"/indeling?fout={quote('Haal het onderwerp eerst van de pagina.')}",
                status_code=303,
            )
        content.delete("topics", topic_id)
        return redirect("/indeling", "Onderwerp verwijderd.")
    raise HTTPException(404)


# Contact data --------------------------------------------------------------

SOCIAL_LABELS = {"instagram": "Instagram", "spotify": "Spotify", "linkedin": "LinkedIn"}


@app.get("/contact", response_class=HTMLResponse)
def edit_contact(request: Request, bericht: str = ""):
    return templates.TemplateResponse(
        request,
        "contact.html",
        {
            "data": content.read_site_data(),
            "social_labels": SOCIAL_LABELS,
            "errors": [],
            "message": bericht,
        },
    )


@app.post("/contact", response_class=HTMLResponse)
async def save_contact(request: Request):
    form = await request.form()
    data = content.read_site_data()
    data["email"] = str(form.get("email", "")).strip()
    for key in SOCIAL_LABELS:
        data.setdefault("social", {})[key] = str(form.get(f"social_{key}", "")).strip()
    data.setdefault("contactForm", {})["accessKey"] = str(form.get("access_key", "")).strip()
    errors = validation.check_site_data(data)
    if errors:
        return templates.TemplateResponse(
            request,
            "contact.html",
            {
                "data": data,
                "social_labels": SOCIAL_LABELS,
                "errors": errors,
                "message": "",
            },
            status_code=422,
        )
    content.write_site_data(data)
    return redirect("/contact", "Opgeslagen.")


# Style ---------------------------------------------------------------------


def works_on_bands() -> list[tuple[str, str, str]]:
    """(title, accent, band) for each topic on the page, with the band it sits on."""
    bands = content.bands()
    result = []
    for topic_id, pair in zip(content.topic_ids(), content.topics()):
        entry = pair["nl"] or pair["en"]
        band = bands.get(f"topic:{topic_id}")
        if entry and band:
            result.append(
                (str(entry.data.get("title", "")), str(entry.data.get("accent", "")), band)
            )
    return [w for w in result if w[1] in validation.ACCENTS]


def render_style(request: Request, values: dict, errors: list[str], message: str = ""):
    works = works_on_bands()
    return templates.TemplateResponse(
        request,
        "style.html",
        {
            "values": values,
            "colors": style.COLORS,
            "scales": style.SCALES,
            "heading_fonts": style.HEADING_FONTS,
            "body_fonts": style.BODY_FONTS,
            "checks": style.contrast_checks(values, works) if not errors else [],
            "works": works,
            "fixed_pairs": style.FIXED_PAIRS,
            "accent_minimum": style.ACCENT_MINIMUM,
            "scale_number": style.scale_number,
            "errors": errors,
            "message": message,
            "preview_url": preview_url(request),
        },
        status_code=422 if errors else 200,
    )


@app.get("/stijl", response_class=HTMLResponse)
def edit_style(request: Request, bericht: str = ""):
    return render_style(request, style_files.read(), [], bericht)


async def save_style_values(request: Request, submitted: dict):
    current = style_files.read()
    values, errors = style.parse_form(submitted, current)
    if not errors:
        failing = [c for c in style.contrast_checks(values, works_on_bands()) if not c.ok]
        errors = [
            f"{c.label}: contrast {c.ratio:.1f}:1, minimaal {c.minimum:g}:1 nodig." for c in failing
        ]
    if errors:
        return render_style(request, current | {k: v for k, v in submitted.items()}, errors)
    style_files.write(values)
    return redirect("/stijl", "Opgeslagen. Het voorbeeld laat de nieuwe stijl direct zien.")


@app.post("/stijl", response_class=HTMLResponse)
async def save_style(request: Request):
    form = await request.form()
    return await save_style_values(request, {k: str(v) for k, v in form.items()})


@app.post("/stijl/standaard", response_class=HTMLResponse)
async def reset_style(request: Request):
    defaults = dict(style.DEFAULTS)
    for scale in style.SCALES:
        defaults[scale.token] = str(style.scale_number(defaults[scale.token]))
    return await save_style_values(request, defaults)


@app.get("/lettertype/{key}.woff2")
def font_sample(key: str):
    path = style.font_file(settings.site_root, key)
    if not path:
        raise HTTPException(404)
    return FileResponse(path, media_type="font/woff2")


# Publishing ----------------------------------------------------------------


def render_publish(request: Request, result=None, message: str = "", status_code: int = 200):
    changes = pending_changes(settings.site_root)
    repo = publisher.github_repo()
    return templates.TemplateResponse(
        request,
        "publish.html",
        {
            "changes": changes,
            "unpushed": publisher.unpushed(),
            "default_message": default_message([c.path for c in changes]) if changes else "",
            "result": result,
            "message": message,
            "errors": [],
            "repo": repo,
            "live_url": pages_url(repo) if repo else "",
            "preview_running": preview.status(),
            "preview_url": preview_url(request),
        },
        status_code=status_code,
    )


@app.get("/publiceren", response_class=HTMLResponse)
def publish_page(request: Request, bericht: str = ""):
    return render_publish(request, message=bericht)


@app.post("/publiceren", response_class=HTMLResponse)
async def publish(request: Request):
    form = await request.form()
    result = publisher.publish(str(form.get("message", "")))
    return render_publish(request, result=result, status_code=200 if result.ok else 422)


@app.post("/publiceren/terugdraaien")
async def discard(request: Request):
    form = await request.form()
    try:
        message = publisher.discard(str(form.get("path", "")))
    except ValueError as error:
        message = str(error)
    return redirect("/publiceren", message)


@app.get("/publiceren/status")
def deploy_status():
    repo = publisher.github_repo()
    return JSONResponse(latest_deploy(repo) if repo else None)


def run() -> None:
    uvicorn.run("sitemanager.main:app", host=settings.host, port=settings.port)
