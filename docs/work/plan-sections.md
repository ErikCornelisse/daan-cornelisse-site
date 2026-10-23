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
| 2 | Page layout in the manager | Pagina-indeling: reorder, add, remove sections, menu toggle; reorder and move topics | 1 | done |
| 3 | Section editors | Editors for section (own text, image, subheadings), hero (photo upload, focal point, link target) and contact | 2 | done |
| 4 | Bands from the structure | Stijl contrast check reads bands from `page.json`; optional band override per section | 2 | done |

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

## Phase 2 — Page layout in the manager

- [x] Structure operations with the same rules as `src/lib/page.ts` (`manager/sitemanager/layout.py`); a change that breaks a rule is refused and `page.json` stays as it was
- [x] Pagina-indeling screen: hero and contact locked; sections up/down, in/out of the menu, add (before contact, with a Dutch and optional English heading and anchor), remove (topics move to another section or off the page)
- [x] Hero link target chosen on the same screen; the section it points to cannot be removed
- [x] Topics up/down, to another section, off the page ("Niet op de pagina", texts kept) and, once off the page, deleted; *Onderwerp toevoegen* per section
- [x] Band colour shown per section and topic
- [x] Site build also refuses two sections with the same anchor in one language

**Result (2026-10-23):** 65 manager tests pass. In the browser, adding a
section and moving *Over mij* up showed directly in the preview with the
bands still alternating; both changes were undone from the screen.

## Phase 3 — Section editors

- [x] Site: optional `focus` ("x% y%") for the hero photo, used where it is cropped (on phones only without a portrait crop); optional `image.position` (`left` / `right`) for a section's own image — _done when:_ the built site is unchanged while they are not set
- [x] Section editor: heading, anchor and menu label per language, own text with `###` subheadings, image upload / replace / remove with a description per language and its side, and the list of the section's topics
- [x] Hero editor: title, subtitle and link text per language, link target, wide photo upload with click-to-set focal point and a phone preview, optional portrait crop
- [x] Contact editor: heading, anchor, menu label and intro text per language
- [x] Checks: required texts, unique and valid anchors per language, a description for every image, a photo for the hero, a valid focal point; an English text left empty creates no English file (the site falls back to Dutch)

**Result (2026-10-23):** 72 manager tests pass; saving an unchanged hero,
section or contact leaves its files identical. In the browser, a focal
point set by clicking and the portrait moved to the right showed in the
preview and built; both test edits were undone.

## Phase 4 — Bands from the structure

- [x] Bands take the other colour than the band before them (cream first); a section's forced colour (`"band"` in `page.json`) restarts the alternation from there — site (`src/lib/page.ts`) and manager (`content.bands()`) alike — _done when:_ the built page is unchanged without overrides
- [x] Pagina-indeling: *Achtergrond: automatisch / crème / papier* per section (not the hero), shown as "achtergrond vast"
- [x] Contrast guard: a layout change (moving, adding, removing, fixing a colour) that would put a work title on a band where it is below 3:1 is refused, with a hint to fix a section's background or choose another accent colour
- [x] The Stijl contrast check uses the same bands

**Result (2026-10-23):** 78 manager tests pass. Moving *Over mij* above
*Mediums en Disciplines* is refused (the purple title would get 2.4:1 on
paper) until *Mediums en Disciplines* is fixed to cream; then the move
works, the preview and the build show the expected bands, and both changes
were undone.

All four steps of this plan are done.

## Open questions
None yet.
