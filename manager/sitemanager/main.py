"""The site manager web app: overview, editing works, pages and contact data,
and the Astro preview."""

from pathlib import Path
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ruamel.yaml.comments import CommentedMap
from starlette.datastructures import FormData, UploadFile

from . import validation
from .content import LANGS, PAGE_NAMES, Entry, SiteContent
from .images import safe_stem, save_upload
from .settings import load_settings
from .site_tools import Preview, last_commit, pending_changes

HERE = Path(__file__).resolve().parent
settings = load_settings()
content = SiteContent(settings.site_root)
preview = Preview(settings.site_root, settings.preview_port, expose=not settings.is_local_only)

app = FastAPI(title="Sitebeheer Daan Cornelisse", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.globals.update(langs=LANGS, accents=validation.ACCENTS)

LANG_NAMES = {"nl": "Nederlands", "en": "English"}
templates.env.globals["lang_names"] = LANG_NAMES

# Which fields each page has, as (front matter key, label); body is separate.
PAGE_FIELDS = {
    "home": [
        ("title", "Titel"),
        ("subtitle", "Ondertitel"),
        ("cta", "Linktekst"),
        ("imageAlt", "Beschrijving van de foto"),
    ],
    "about": [("title", "Titel"), ("imageAlt", "Beschrijving van het portret")],
    "contact": [("title", "Titel")],
    "privacy": [("title", "Titel")],
}
PAGE_HAS_BODY = {"home": False, "about": True, "contact": True, "privacy": True}
PAGE_LABELS = {
    "home": "Openingsbeeld",
    "about": "Over mij",
    "contact": "Contact",
    "privacy": "Privacyverklaring",
}


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
            "works": content.works(),
            "pages": [
                (
                    name,
                    PAGE_LABELS[name],
                    {lang: content.get("pages", lang, name) for lang in LANGS},
                )
                for name in PAGE_NAMES
            ],
            "changes": pending_changes(settings.site_root),
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
        "order": base.data.get("order", "") if base else "",
        "images": images,
        "texts": texts,
    }


def render_work(
    request: Request, slug: str | None, view: dict, errors: list[str], message: str = ""
):
    return templates.TemplateResponse(
        request,
        "work.html",
        {
            "slug": slug,
            "work": view,
            "errors": errors,
            "message": message,
            "max_images": validation.MAX_IMAGES,
            "preview_url": preview_url(request, "nl", f"#{slug}" if slug else ""),
        },
        status_code=422 if errors else 200,
    )


@app.get("/werken/nieuw", response_class=HTMLResponse)
def new_work(request: Request):
    return render_work(request, None, work_view(None, None), [])


@app.get("/werken/{slug}", response_class=HTMLResponse)
def edit_work(request: Request, slug: str, bericht: str = ""):
    nl, en = content.get("works", "nl", slug), content.get("works", "en", slug)
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


def apply_work(
    entry: Entry, lang: str, form: FormData, images: list[dict], accent: str, order
) -> None:
    data = entry.data
    for key in ("title", "discipline"):
        data[key] = str(form.get(f"{lang}_{key}", "")).strip()
    data["accent"] = accent
    data["order"] = order
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
        if content.get("works", "nl", slug) or content.get("works", "en", slug):
            slug = f"{slug}-{len(content.slugs('works')) + 1}"
    entries = {
        lang: content.get("works", lang, slug) or new_entry("works", lang, slug) for lang in LANGS
    }

    images, errors = await images_from_form(form, entries["nl"].path)
    accent = str(form.get("accent", ""))
    try:
        order = int(str(form.get("order", "")).strip())
    except ValueError:
        order = None
    if order is None and creating:
        order = (
            max(
                (int((p["nl"] or p["en"]).data.get("order", 0)) for p in content.works()), default=0
            )
            + 1
        )

    to_save = []
    for lang, entry in entries.items():
        # A language with no title and no text is left out (to be written or translated later),
        # unless the file already exists.
        if not entry.path.exists() and not has_text(form, lang):
            continue
        apply_work(entry, lang, form, images, accent, order)
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
        return render_work(request, None if creating else slug, view, errors)

    for entry in to_save:
        content.save(entry)
    return redirect(f"/werken/{slug}", "Opgeslagen.")


# Pages ---------------------------------------------------------------------


def render_page(request: Request, name: str, values: dict, errors: list[str], message: str = ""):
    return templates.TemplateResponse(
        request,
        "page.html",
        {
            "name": name,
            "label": PAGE_LABELS[name],
            "fields": PAGE_FIELDS[name],
            "has_body": PAGE_HAS_BODY[name],
            "values": values,
            "errors": errors,
            "message": message,
            "preview_url": preview_url(request, "nl", "privacy/" if name == "privacy" else ""),
        },
        status_code=422 if errors else 200,
    )


@app.get("/paginas/{name}", response_class=HTMLResponse)
def edit_page(request: Request, name: str, bericht: str = ""):
    if name not in PAGE_NAMES:
        raise HTTPException(404)
    values = {}
    for lang in LANGS:
        entry = content.get("pages", lang, name)
        values[lang] = (
            {key: str(entry.data.get(key, "")) for key, _ in PAGE_FIELDS[name]} if entry else {}
        )
        values[lang]["body"] = entry.body.strip("\n") if entry else ""
    return render_page(request, name, values, [], bericht)


@app.post("/paginas/{name}", response_class=HTMLResponse)
async def save_page(request: Request, name: str):
    if name not in PAGE_NAMES:
        raise HTTPException(404)
    form = await request.form()
    errors, entries, values = [], [], {}
    for lang in LANGS:
        entry = content.get("pages", lang, name) or new_entry("pages", lang, name)
        values[lang] = {
            key: str(form.get(f"{lang}_{key}", "")).strip() for key, _ in PAGE_FIELDS[name]
        }
        values[lang]["body"] = str(form.get(f"{lang}_body", "")).replace("\r\n", "\n")
        for key, _ in PAGE_FIELDS[name]:
            if values[lang][key]:
                entry.data[key] = values[lang][key]
            else:
                entry.data.pop(key, None)
        if PAGE_HAS_BODY[name]:
            entry.body = values[lang]["body"]
        errors += [f"{LANG_NAMES[lang]}: {e}" for e in validation.check_page(entry.data)]
        entries.append(entry)
    if errors:
        return render_page(request, name, values, errors)
    for entry in entries:
        content.save(entry)
    return redirect(f"/paginas/{name}", "Opgeslagen.")


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


def run() -> None:
    uvicorn.run("sitemanager.main:app", host=settings.host, port=settings.port)
