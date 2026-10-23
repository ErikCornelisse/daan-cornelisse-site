# Phase 04 — Hero and header

**Objective:** the top of the page as in the mockup, designed for the phone first.

**Tasks**
- [x] Hero image art direction: portrait crop for phones, wide crop from 768 px, via `<picture>` and `astro:assets` — _affects:_ `src/components/Hero.astro`, `src/assets/images/hero-*` — _done when:_ the figure stays visible at every width and the image is under 300 KB on phones
- [x] Title, subtitle and *Mijn verhaal* from the page content per language, with the bottom fade into cream — _affects:_ `src/components/Hero.astro`, `src/content/pages/{nl,en}/home.md` — _done when:_ text is readable over the photo at all widths
- [x] Header with name, nav (*Over mij*, *Contact*) and the language switch; no hamburger — _affects:_ `src/components/Header.astro` — _done when:_ it fits on one line at 375 px with 44 px touch targets
- [x] Anchor scrolling with `scroll-margin-top` and smooth scroll that respects `prefers-reduced-motion` — _affects:_ `src/styles/global.css` — _done when:_ *Mijn verhaal* and the nav land on the right section heading

**Acceptance:** build green; hero and header checked at 375, 768 and 1440 px in both languages.
