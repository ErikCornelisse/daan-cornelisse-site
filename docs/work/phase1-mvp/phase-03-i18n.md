# Phase 03 — i18n skeleton

**Objective:** the page exists at `/nl/` and `/en/`, visitors land in the right language, and can switch.

**Tasks**
- [x] Configure Astro i18n: locales `nl` and `en`, both prefixed — _affects:_ `astro.config.mjs` — _done when:_ `/nl/` and `/en/` build
- [x] Move the page to `src/pages/[lang]/index.astro` with `getStaticPaths` — _affects:_ `src/pages/` — _done when:_ both URLs render the bands with `<html lang>` set correctly
- [x] Interface strings per language — _affects:_ `src/i18n/ui.ts` — _done when:_ no visible interface text is hard-coded in components
- [x] Root language chooser: inline script (stored choice, then time zone Europe/Amsterdam or a language with region NL → `/nl/`, then the first `nl`/`en` browser language, else `/en/`), plain links as no-JS fallback — _affects:_ `src/pages/index.astro` — _done when:_ a Dutch browser lands on `/nl/`, an English one on `/en/`
- [x] `LanguageSwitch` component that links to the same page in the other language and stores the choice (try/catch around storage) — _affects:_ `src/components/LanguageSwitch.astro` — _done when:_ switching sticks across visits to `/`
- [x] `hreflang` alternates and `x-default` in the layout head — _affects:_ `src/layouts/BaseLayout.astro` — _done when:_ both pages list each other

**Acceptance:** build green; the redirect and switch work on the deployed Pages URL (base path included), also with storage blocked.
