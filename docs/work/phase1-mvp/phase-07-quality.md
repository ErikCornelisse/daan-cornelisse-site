# Phase 07 — Quality pass

**Objective:** the page is accessible, fast and findable on phones and laptops.

**Tasks**
- [ ] Accessibility: heading order, alt texts, keyboard path, focus states, form errors announced — _affects:_ components — _done when:_ an automated check (axe or Lighthouse) shows no violations
- [ ] Performance: responsive image sizes, lazy loading below the fold, font preload, no unused CSS — _affects:_ components, `BaseLayout.astro` — _done when:_ Lighthouse mobile scores ≥ 95 for performance, accessibility, best practices and SEO
- [ ] Privacy note per language covering the form service — _affects:_ `src/content/pages/{nl,en}/privacy.md`, `src/pages/[lang]/privacy.astro`, `Footer.astro` — _done when:_ the footer links to it
- [ ] Meta: title, description, Open Graph image, favicon, `robots.txt`, sitemap — _affects:_ `BaseLayout.astro`, `public/`, `astro.config.mjs` — _done when:_ a link preview shows the right title and image in both languages
- [ ] Cross-browser check: Safari iOS, Chrome Android, Safari and Chrome on macOS — _affects:_ — _done when:_ no layout breaks are found

**Acceptance:** build green; Lighthouse targets met on the deployed prototype.
