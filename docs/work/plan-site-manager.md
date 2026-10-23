# Plan: Site manager (site phase 2 — keeping the site up to date)

## Goal
A small local web application with which Daan maintains his site without
touching code: edit the works and page texts in Dutch and English, update
contact details, translate Dutch texts to English with a local language
model, change colours, fonts and sizes, preview the result, and publish to
GitHub Pages and (later) to `daniel-cornelisse.nl` at mijndomein.

It runs on this MacBook Pro now and on the Mac mini at home later; Daan
reaches it there over Tailscale.

Done when Daan can, from a browser on the Tailscale network, change a work,
let the English text be drafted, adjust a colour, preview it, and publish it
live, without help.

Background: the options and choice are in the advice of 2026-10-23
(option B, "custom site manager"), building on
[phase 1 proposal](analysis/phase1-static-site-20261023.md) §8.

## Current vs. desired
- **Now:** content in Markdown/JSON (`src/content/`, `src/data/site.json`),
  rules in `src/content.config.ts`, style tokens in `src/styles/tokens.css`,
  GitHub Pages deploy on push. Every change needs a code editor and git.
- **Desired:** `manager/` — a Python web app that reads and writes the same
  files, runs the Astro preview, commits and pushes, and triggers the
  production deploy. The site itself keeps building exactly as now.

## Design decisions
| # | Decision | Reason |
|---|---|---|
| D1 | The manager lives in `manager/` in this repository | One checkout on the Mac mini; manager and content rules change in the same commit |
| D2 | Python 3.12+, uv, FastAPI, Jinja2 templates, plain HTML forms and a little vanilla JS; no frontend build | Preferred language; nothing to compile; easy to run as a service |
| D3 | The Markdown/JSON files stay the single source of content; YAML is read and written round-trip (ruamel.yaml) so comments and field order survive | Hand edits and manager edits can be mixed; diffs stay small |
| D4 | Validation in the manager mirrors `src/content.config.ts`; `astro check` and a build run before publishing | Errors show in the form, and nothing broken reaches the live site |
| D5 | Preview = `astro dev`, started and stopped by the manager | Same rendering as the live site, instant updates |
| D6 | Publish = `git pull --rebase`, commit of the changed content files, `git push` to `main` (GitHub Pages deploys itself) | Reuses the existing pipeline; full history and undo through git |
| D7 | Translation through a provider interface; first provider Ollama (`OLLAMA_URL`, `OLLAMA_MODEL`, default `qwen3.6:35b-mlx`). English files get `translation: {status, source}` front matter: `draft` until Daan marks them reviewed, and a hash of the Dutch source to detect outdated translations | Local, free, private; a provider can be swapped later; drafts are never silently treated as final |
| D8 | Style editing limited to whitelisted tokens in `src/styles/tokens.css` (colours, fonts, type and spacing scale), with a live WCAG contrast check; fonts from a vetted list of self-hosted Fontsource packages. Image sizes come later | Prevents one edit from breaking the mobile layout; keeps the accessibility level of phase 1 |
| D9 | No login: access is controlled by who can reach the Mac (LAN, Tailscale). The server binds to a configurable host and port (`MANAGER_HOST`, `MANAGER_PORT`, default `127.0.0.1:8765` on the MacBook) | Owner's decision; keeps the app simple |
| D10 | Production deploy runs in a GitHub workflow (`workflow_dispatch`) that builds for `https://daniel-cornelisse.nl` and uploads over SFTP with repository secrets; the manager triggers it and shows its status through `gh` | Credentials stay in GitHub; deploys always come from what is in GitHub |
| D11 | Runs as a launchd LaunchAgent on the Mac mini | Starts on login, restarts on failure |

## Phases
| # | Phase | Delivers | Depends on | Status |
|---|-------|----------|------------|--------|
| 1 | Skeleton | `manager/` Python project, FastAPI app with layout and an overview of works, pages and git status | — | done |
| 2 | Content editing and preview | Edit works (nl/en side by side), page texts and contact data; image upload; validation; start/stop the Astro preview | 1 | done |
| 3 | Publish to GitHub Pages | Change list, check + build, commit and push, deploy status | 2 | todo |
| 4 | Translation | "Translate to English" per work/page via Ollama; draft/reviewed status; outdated-translation warnings | 2 | todo |
| 5 | Style | Colours with contrast check, fonts, type and spacing sizes; preview | 2 | todo |
| 6 | Service on the Mac mini | launchd agent, install and update instructions, Tailscale access notes | 3 | todo |
| 7 | Production deploy | SFTP deploy workflow to mijndomein, triggered and followed from the manager | 3, site phase 1 step 8 | todo |
| 8 | Image sizes | Size settings for work and portrait images | 5 | todo |

Status: `todo` → `in-progress` → `done`. This table is the source of truth
for progress.

## Phase 1 — Skeleton

**Objective:** a running manager that shows what the site contains.

- [x] `manager/` Python project with uv, Ruff, pytest (26 tests) — _done when:_ `uv run ruff check .` and `uv run pytest` pass
- [x] Settings from `.env` (`SITE_ROOT`, host, port) — _done when:_ `.env.example` documents them
- [x] Content repository module: list and read works, pages and site data per language — _done when:_ unit tests read the real content
- [x] FastAPI app with a Dutch layout and an overview page (works, pages, translation pairs, git status) — _done when:_ `uv run sitemanager` serves the overview

## Phase 2 — Content editing and preview

- [x] Edit a work: Dutch and English side by side; title, discipline, accent, order, images with alt text, quote, body — _done when:_ saving writes the Markdown with comments preserved
- [x] Edit page texts (home, about, contact, privacy) and contact data (`site.json`)
- [x] Image upload for works (resized to at most 2400 px, saved in `src/assets/images/works/`)
- [x] Validation mirroring `content.config.ts`, with messages in the form
- [x] Start/stop the Astro dev server and link to the preview of the edited language

## Phases 3–8
Detailed when the previous phase is done.

## Open questions
1. Commit author for changes made in the manager: a fixed "Daan Cornelisse
   (site manager)", or the git identity of the Mac?
2. Translation quality and speed of `qwen3.6:35b-mlx` on the Mac mini: to be
   measured in phase 4; which model is installed there?
3. SFTP host, user and target folder at mijndomein (phase 7).
