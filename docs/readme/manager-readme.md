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

## What it does (phases 1–3)

| Screen | Edits |
|---|---|
| Overzicht | Lists works and pages per language, starts/stops the preview, shows unpublished changes |
| Werken | Accent colour, order, 1–2 images (upload, replace, remove, alt text per language), and title, discipline, quote and text in Dutch and English side by side; "Nieuw werk" adds one |
| Pagina's | Opening image texts, About, Contact and Privacy in both languages |
| Contact & links | E-mail address, Instagram, Spotify and LinkedIn links, Web3Forms key |
| Publiceren | Lists unpublished content changes (each can be undone), checks and builds the site, commits only the content files, pulls in changes from GitHub, pushes, and follows the GitHub Pages deploy |

Edits are written straight into `src/content/`, `src/data/site.json` and
`src/assets/images/works/`. Comments and field order in the Markdown front
matter are kept, so hand edits and manager edits can be mixed. The preview
(Astro dev server) picks up every save immediately.

### Publishing

*Controleren en publiceren* runs `npm run check` and `npm run build`; only if
both pass does it commit the changed files under `src/content`, `src/data`,
`src/assets` and `src/styles` (never code), run `git pull --rebase
--autostash`, and push to `main`. The existing workflow then deploys GitHub
Pages; the screen follows that run through GitHub's public API. If the push
fails (for example without network), the commit stays and the next publish
sends it.

The Mac running the manager needs:

- push access to the GitHub repository (for example `gh auth login`, or an
  SSH key), because the manager pushes as that Mac's git user;
- optionally `PUBLISH_AUTHOR="Daan Cornelisse <…>"` in `.env` to record Daan
  as the author of the commits.

Translation, style editing and the production deploy follow in phases 4–7
of the plan.

## Structure

| Module | Role |
|---|---|
| `sitemanager/settings.py` | Settings from `manager/.env` |
| `sitemanager/content.py` | Reading and writing Markdown/JSON content, round-trip YAML |
| `sitemanager/validation.py` | Checks mirroring `src/content.config.ts`; keep the two in step |
| `sitemanager/images.py` | Image uploads: format check, orientation, scaled to max 2400 px |
| `sitemanager/site_tools.py` | Git status and the Astro preview |
| `sitemanager/publish.py` | Check, commit, pull, push, undo, and the GitHub deploy status |
| `sitemanager/main.py` | FastAPI routes; templates in `templates/`, CSS in `static/` |

## Tests

```bash
cd manager
uv run ruff check .
uv run pytest
```

The tests check that reading and writing every content file leaves it
byte-for-byte identical, run the endpoints against a temporary copy of the
content, and publish into a temporary git repository with a local remote.
