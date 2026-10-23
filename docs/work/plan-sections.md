# Plan: Modular sections and topics

## Goal
The landing page is built from an ordered list of sections, each with an
ordered list of topics, so the site manager can add, remove and re-arrange
them. The hero is always first and the contact section always last; both
are editable but cannot be removed or moved.

Design: [sections and topics proposal, revision 2](analysis/sections-topics-20261023.md),
with the proposed defaults for its open questions: a topic belongs to one
section; the structure is the same in both languages; bands alternate
automatically with an optional override per section; a missing English
text falls back to the Dutch one.

## Current vs. desired
- **Now:** the order of hero, works, about and contact is fixed in
  `src/pages/[lang]/index.astro`; headings, anchors, menu items and hero
  photos partly live in code (`ui.ts`, `Header.astro`, `Hero.astro`).
- **Desired:** `src/content/page.json` holds the structure;
  `src/content/sections/` and `src/content/topics/` hold the texts per
  language; the page, menu and bands are derived from them; the manager
  edits all of it.

## Constraints & assumptions
- Step 1 changes no visible content: the page looks and reads the same.
- The manager keeps working after every step (its tests pass).
- Mobile first and the accessibility results of phase 1 are kept.
- This comes before translation (site manager phase 4).

## Phases
| # | Phase | Delivers | Depends on | Status |
|---|-------|----------|------------|--------|
| 1 | Content-driven page | `page.json`, `sections` and `topics` collections, rules checked at build time, page/menu/bands rendered from them; manager reads the new layout | — | done |
| 2 | Page layout in the manager | Pagina-indeling: reorder, add, remove sections, menu toggle; reorder and move topics | 1 | todo |
| 3 | Section editors | Editors for section (own text, image, subheadings), hero (photo upload, focal point, link target) and contact | 2 | todo |
| 4 | Bands from the structure | Stijl contrast check reads bands from `page.json`; optional band override per section | 2 | todo |

Status: `todo` → `in-progress` → `done`. This table is the source of truth
for progress.

## Phase 1 — Content-driven page

**Objective:** the same page as today, now built from content.

- [x] Baseline build saved for comparison — _done when:_ text, images and bands of the old build can be compared with the new one
- [x] `src/content/page.json` and a schema with the rules (hero first, contact last, unique ids, each topic in one section, link target exists) — _done when:_ breaking a rule fails the build with a clear message
- [x] Works → `src/content/topics/`; home, about and contact → `src/content/sections/` (`hero`, `mediums`, `over-mij`, `contact`), with anchors, menu labels and hero photos in front matter; the `order` field leaves the topics — _done when:_ `ui.ts` no longer holds section headings, anchors or menu items
- [x] Page lib that resolves the structure per language (Dutch fallback) and computes the bands — _done when:_ unit-level output matches today's bands
- [x] Components: hero from front matter, a content section (own text and image, then topics), contact; header menu from the structure; each section a `<section>` with its topics as `<article>`s — _done when:_ the page reads and looks as before at 375, 768 and 1440 px
- [x] Manager follows the new layout (topics, sections, privacy page; topic order from `page.json`) — _done when:_ its tests pass and editing still works

**Acceptance:** `npm run check` and `npm run build` pass; text, images and
bands match the baseline; manager tests pass.

**Result (2026-10-23):** compared with the baseline build, text, heading
outline, images, bands and links are identical on all five pages; the only
difference is the new anchor of the works section (`#mediums` / `#media`).
Breaking a structure rule stops the build with a message such as "There must
be exactly one hero, and it must be the first section." Manager: 51 tests
pass. Topic order now lives only in `page.json` (the `order` field is gone);
the manager adds a new work at the end of the first section with works.

## Phases 2–4
Detailed when the previous phase is done.

## Open questions
None yet.
