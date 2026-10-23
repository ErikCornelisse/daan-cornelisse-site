# Phase 05 — Work blocks

**Objective:** *Mediums en Disciplines* with the three works rendered from Markdown in both languages.

**Tasks**
- [x] `works` collection schema: title, discipline, accent, order, images (src, alt), optional quote — _affects:_ `src/content.config.ts` — _done when:_ a missing alt text or unknown accent fails the build
- [x] Three works in nl and en with placeholder text, same slug per language — _affects:_ `src/content/works/{nl,en}/*.md`, `src/assets/images/works/` — _done when:_ both languages list three works in `order`
- [x] `WorkBlock` component: stacked on phones (title, text, images, quote); text in one or two columns plus media from 1024 px — _affects:_ `src/components/WorkBlock.astro` — _done when:_ the three mockup variants (two columns + image, one column + two images + quote, two columns + square image) all render from the same component
- [x] Section heading and alternating band variants per block — _affects:_ `src/pages/[lang]/index.astro` — _done when:_ the order of bands matches the mockup
- [x] Accent contrast check; adjust the white-on-khaki title and quote — _affects:_ `src/styles/tokens.css` — _done when:_ all text passes WCAG AA — _provisional: orange `#b56424`, brown `#5b2f1a` instead of white, quote in ink; to confirm with Daan_

**Acceptance:** build green; adding a fourth work is only a new Markdown file per language.
