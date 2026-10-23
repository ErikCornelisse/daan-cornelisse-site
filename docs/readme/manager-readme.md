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

## What it does (phases 1, 2, 3 and 5)

| Screen | Edits |
|---|---|
| Overzicht | Lists works and pages per language, starts/stops the preview, shows unpublished changes |
| Pagina-indeling | The structure of the landing page (`page.json`): sections up/down, add, remove, in/out of the menu, the hero's link target; topics up/down, to another section, off the page and back, delete; band colour per part. Hero and contact are locked. Changes that break the rules of `src/lib/page.ts` are refused |
| Werken | Topics (today the works): accent colour, 1–2 images (upload, replace, remove, alt text per language), and title, discipline, quote and text in Dutch and English side by side; "Nieuw werk" adds one at the end of the first section with works |
| Pagina's | Texts of every section in `page.json` (hero, sections, contact) and of the privacy page, in both languages |
| Contact & links | E-mail address, Instagram, Spotify and LinkedIn links, Web3Forms key |
| Stijl | Colours, heading and body font, text, heading and spacing size, content width; live contrast check; restore the original style |
| Publiceren | Lists unpublished content changes (each can be undone), checks and builds the site, commits only the content files, pulls in changes from GitHub, pushes, and follows the GitHub Pages deploy |

Edits are written straight into `src/content/` (`page.json` for the
structure, `sections/` and `topics/` for the texts), `src/data/site.json` and
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

### Style

*Stijl* edits only whitelisted values in `src/styles/tokens.css`, line by
line, so its comments and everything else stay untouched:

- colours (`--color-*`), checked for contrast before saving: body text
  4.5:1 on cream and paper, footer text 4.5:1 on dark, the button label 3:1,
  and every work title 3:1 on the band it actually sits on (bands alternate
  in the order of the works);
- fonts from a fixed list of free, self-hosted Fontsource fonts (headings:
  Belleza, Tenor Sans, Marcellus; text: Source Serif 4, Libre Caslon Text,
  Crimson Pro, EB Garamond). All are installed as site dependencies; only the
  chosen ones end up in the built site. Choosing one rewrites
  `src/styles/fonts.ts` together with the `--font-*` values;
- size factors `--scale-text`, `--scale-heading`, `--scale-space` (shown as
  percentages) and `--container` (content width).

Images with a background colour baked in (such as the current vase
illustration on cream) show as a block when the background colour changes;
such images should have a transparent background.

Translation and the production deploy follow in phases 4, 6 and 7 of the
plan.

## Structure

| Module | Role |
|---|---|
| `sitemanager/settings.py` | Settings from `manager/.env` |
| `sitemanager/content.py` | Reading and writing Markdown/JSON content, round-trip YAML |
| `sitemanager/validation.py` | Checks mirroring `src/content.config.ts`; keep the two in step |
| `sitemanager/images.py` | Image uploads: format check, orientation, scaled to max 2400 px |
| `sitemanager/site_tools.py` | Git status and the Astro preview |
| `sitemanager/layout.py` | Structure operations on `page.json` and the same rules as `src/lib/page.ts` |
| `sitemanager/style.py` | Style tokens, font list, contrast rules, defaults |
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
