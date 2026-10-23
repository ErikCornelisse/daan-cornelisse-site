# Phase 02 — Tokens, fonts and bands

**Objective:** the visual base of the mockup (colours, type, the two section backgrounds) as a mobile-first layout.

**Tasks**
- [x] Design tokens: colours, accents, spacing scale, fluid type with `clamp()`, breakpoints (768, 1024) — _affects:_ `src/styles/tokens.css` — _done when:_ every colour and size used elsewhere comes from a token
- [ ] Font comparison page with free Optima look-alikes (e.g. Belleza, Tenor Sans) and two body serifs; owner picks one pair — _affects:_ `src/pages/fonts.astro` (temporary) — _done when:_ the pair is chosen and noted in `history.md` — _built: `/fonts/`, Belleza + Source Serif 4 in place provisionally_
- [x] Self-host the chosen fonts (Fontsource or files in `src/assets/fonts/`) — _affects:_ `package.json`, `src/styles/tokens.css` — _done when:_ no font request leaves the site, and swapping a font means changing one token
- [x] Global styles: reset, typography, links, focus outlines — _affects:_ `src/styles/global.css` — _done when:_ text on the test page matches the mockup's feel at 375 px
- [x] `BaseLayout` and `Section` component with `variant="cream" | "paper"`, paper grain as a small tiled texture — _affects:_ `src/layouts/BaseLayout.astro`, `src/components/Section.astro`, `public/textures/` — _done when:_ alternating bands render full width at all three widths
- [ ] Remove the font comparison page — _affects:_ `src/pages/fonts.astro` — _done when:_ it is gone from the build

**Acceptance:** build green; placeholder bands with headings and body text look right at 375, 768 and 1440 px.
