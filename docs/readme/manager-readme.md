# Site manager

A local web app for maintaining the site's content without editing files.
Plan and design decisions: [plan-site-manager.md](../work/plan-site-manager.md).

## Start

```bash
cd manager
cp .env.example .env    # once; adjust if needed
uv run sitemanager
```

Then open <http://127.0.0.1:8765/>. On the Mac mini, set `MANAGER_HOST=0.0.0.0`
in `.env` so it can be reached over the local network and Tailscale
(`http://<mac-mini>:8765/`); the preview is then also started on all
interfaces.

Requirements: [uv](https://docs.astral.sh/uv/), Node 22.23+ with the site's
dependencies installed (`npm install` in the repository root) for the preview.

## What it does (phases 1–2)

| Screen | Edits |
|---|---|
| Overzicht | Lists works and pages per language, starts/stops the preview, shows unpublished changes |
| Werken | Accent colour, order, 1–2 images (upload, replace, remove, alt text per language), and title, discipline, quote and text in Dutch and English side by side; "Nieuw werk" adds one |
| Pagina's | Opening image texts, About, Contact and Privacy in both languages |
| Contact & links | E-mail address, Instagram, Spotify and LinkedIn links, Web3Forms key |

Edits are written straight into `src/content/`, `src/data/site.json` and
`src/assets/images/works/`. Comments and field order in the Markdown front
matter are kept, so hand edits and manager edits can be mixed. The preview
(Astro dev server) picks up every save immediately.

Publishing, translation, style editing and the production deploy follow in
phases 3–7 of the plan; until phase 3, publish with git as before.

## Structure

| Module | Role |
|---|---|
| `sitemanager/settings.py` | Settings from `manager/.env` |
| `sitemanager/content.py` | Reading and writing Markdown/JSON content, round-trip YAML |
| `sitemanager/validation.py` | Checks mirroring `src/content.config.ts`; keep the two in step |
| `sitemanager/images.py` | Image uploads: format check, orientation, scaled to max 2400 px |
| `sitemanager/site_tools.py` | Git status and the Astro preview |
| `sitemanager/main.py` | FastAPI routes; templates in `templates/`, CSS in `static/` |

## Tests

```bash
cd manager
uv run ruff check .
uv run pytest
```

The tests check that reading and writing every content file leaves it
byte-for-byte identical, and run the endpoints against a temporary copy of
the content.
