# Proposal: modular sections and topics

Goal: the landing page becomes an ordered list of **sections**, each of
which can hold an ordered list of **topics**. In the site manager Daan can
add, remove and re-arrange sections and topics. The hero is always the
first section and the contact section always the last; both can be edited
but neither removed nor moved.

Revision 2 (2026-10-23): three section types instead of four — the
separate "topics" and "text" types are merged into one *section* type.

## 1. What is fixed today

The order and the set of sections are hard-coded in
`src/pages/[lang]/index.astro`: Hero, then one band per work, then *Over mij*,
then *Contact*. Several things that should be content live in code:

| What | Where now |
|---|---|
| Section order and which sections exist | `src/pages/[lang]/index.astro` |
| Heading *Mediums en Disciplines* | `src/i18n/ui.ts` (`section.works`) |
| Anchors `#over-mij` / `#about`, `#contact` | `src/i18n/ui.ts` (`id.*`) |
| Menu items *Over mij*, *Contact* | `src/components/Header.astro` + `ui.ts` |
| Hero photos (wide and portrait crop) | imports in `src/components/Hero.astro` |
| *Mijn verhaal* target | hard-coded to the about anchor in `index.astro` |

The works are already modular (one Markdown file per work and language),
but there is only one fixed group of them, and the group itself has no
element of its own.

## 2. Model

Two levels, with the **structure** kept apart from the **texts**:

- **Structure** — one language-neutral file says which sections exist, in
  what order, and which topics each section holds. Dutch and English
  therefore always have the same structure.
- **Texts and images** — one Markdown file per section and per topic per
  language, as the works are now.

```
src/content/
  page.json                          structure of the landing page
  sections/{nl,en}/<section-id>.md   section texts per language
  topics/{nl,en}/<topic-id>.md       topic texts per language (today's works)
```

`page.json`, matching today's page:

```json
{
  "sections": [
    { "id": "hero", "type": "hero" },
    { "id": "mediums", "type": "section",
      "topics": ["als-het-licht-even-uitgaat", "tijd-voor-max", "voor-ik-sluit"] },
    { "id": "over-mij", "type": "section", "menu": true },
    { "id": "contact", "type": "contact", "menu": true }
  ]
}
```

### Section types

| Type | Position | Fields (per language unless noted) | Today |
|---|---|---|---|
| `hero` | always first; cannot be removed or moved | title, subtitle, link text, link target (another section, language-neutral), photo (wide crop, optional portrait crop, focal point), photo description | banner |
| `section` | anywhere between hero and contact; any number | heading; optional own text; optional own image with description (left or right); 0 or more topics | *Mediums en Disciplines*, *Over mij* |
| `contact` | always last; cannot be removed or moved | heading, intro text; e-mail, links and form from `site.json` | *Contact* |

A `section` renders its parts in this order: heading, own text and image
(in today's *Over mij* layout), then its topics (each in today's work
layout). Every part is optional except the heading, so:

- *Mediums en Disciplines* = heading + three topics, no own text;
- *Over mij* = heading + own text + portrait, no topics.

**Subheadings.** The own text of a section and the text of a topic are
Markdown: a line starting with `###` is a subheading, followed by its
paragraphs. Any number of subheaded paragraphs can follow each other, and
they stay in the band of the section (or topic) they belong to — exactly as
*Mijn werk* and *Epilepsie* in *Over mij* today. Subheadings are not
movable on their own; to move a part separately, make it a topic.

A **topic** keeps today's work fields: title, discipline, accent colour,
1–2 images with descriptions, optional quote, text. In the portfolio phase
the same topic files become the portfolio entries.

Each section file also holds its **anchor** per language (`anchor:
over-mij` / `anchor: about`) and, when the section is in the menu, its
**menu label**. That replaces the `id.*` and `nav.*` strings in `ui.ts`.

### Rules

Checked both by the site build (a refinement on the `page.json` schema in
`content.config.ts`) and by the manager before saving, so a mistake can
never reach the site:

1. Exactly one `hero`, always first, and exactly one `contact`, always
   last; neither can be removed or moved.
2. Section ids are unique; a section's text file exists at least in Dutch.
3. A topic belongs to exactly one section; every listed topic exists.
4. The hero link target is an existing section.
5. A missing English text is reported in the manager; the English page then
   shows the Dutch text, marked `lang="nl"`, instead of leaving a hole.

### Bands

Bands (cream / paper) alternate automatically down the page, starting with
the first band after the hero:

- a section's heading with its own text and image is one band — however
  many subheadings and paragraphs the text has;
- each topic is one band of its own;
- a section without own text puts its heading in the band of its first
  topic, as *Mediums en Disciplines* today;
- the contact section is the last band.

A section can force its band colour (`"band": "paper"`) when Daan wants
that. The Stijl contrast check already computes the band per work; it then
reads the bands from `page.json`, so every title is checked on the band it
actually sits on after re-ordering.

## 3. Rendering

`src/pages/[lang]/index.astro` no longer lists sections; it reads
`page.json` and renders each entry with the component for its type —
`HeroSection`, `ContentSection` (with `TopicBlock`, today's `WorkBlock`)
or `ContactSection`.

Each section renders as `<section id={anchor} aria-labelledby=…>` with its
heading, and each topic as an `<article>` inside it. That also fixes the
grouping quirk: *Mediums en Disciplines* becomes a real section with its
topics inside. The header menu is built from the sections marked
`"menu": true`, in page order.

The first step of the migration must produce the same page as today; that
is checked by comparing the built HTML before and after.

## 4. Site manager

| Screen | What Daan does |
|---|---|
| **Pagina-indeling** (new) | Sees all sections in order. The hero is pinned at the top and the contact section at the bottom, both with a lock: *Bewerken* only. Sections in between: *Omhoog* / *Omlaag*, *In menu* on/off, *Verwijderen*, and *Sectie toevoegen* (with a heading). Works without dragging; drag-and-drop can be added on top. |
| **Sectie** | Heading, own text (with subheadings) and own image, Dutch and English side by side. Below: its topics with *Omhoog* / *Omlaag*, *Verplaatsen naar sectie…*, *Verwijderen* and *Onderwerp toevoegen*. |
| **Openingsbeeld** (hero) | Title, subtitle, link text, link target (a list of the sections), photo upload with a click-to-set focal point for the phone crop, optional separate portrait photo, description per language. |
| **Contact** | Heading and intro text per language; contact data and links as now. |
| **Onderwerp** | Today's work editor, unchanged apart from the name. |

Removing a section that still holds topics asks whether to remove those
topics too or move them to another section first. Everything stays
undoable until publishing (Publiceren lists every changed file), and
publishing is unchanged because all of this lives in the content folders.

## 5. Migration and phases

| # | Step | Result |
|---|---|---|
| 1 | Content model and rendering from `page.json`; move works → `topics/`, home/about/contact → `sections/`, hero photos into the hero's front matter, anchors and menu labels out of `ui.ts` | The same page as today, now driven by content |
| 2 | Manager: Pagina-indeling with reorder, add, remove and menu toggle; topic reorder and move | Structure editable |
| 3 | Manager: editors for section, hero (photo upload and focal point) and contact | All content editable |
| 4 | Stijl reads bands from `page.json`; optional band override per section | Contrast check stays correct after re-ordering |

This replaces the current Werken/Pagina's split in the manager rather
than adding to it, so it is best done before translation (phase 4 of the
site manager plan), which would otherwise be built twice.

## 6. Questions

1. May a topic appear in two sections, or does each topic belong to one
   (proposed: one)?
2. Should the section order always be the same in Dutch and English
   (proposed: yes)?
3. Band colours: automatic alternation with an optional override per
   section (proposed), or always chosen per section?
4. Missing English text: show the Dutch text (proposed) or hide that
   section or topic on the English page?
