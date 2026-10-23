# Plan: Phase 1 — minimal viable site

## Goal
A bilingual (nl/en), mobile-first static landing page for Daan Cornelisse,
built from [mockup v1](../design/mockup%20v1.png): who he is, his work, and
how to contact him. It runs as a prototype on GitHub Pages so style and
content can be refined, and builds for upload to Daan's domain at mijndomein.nl.

Done when the page is live on GitHub Pages in both languages, looks right on
a phone and a laptop, and a root-path build plus upload instructions exist
for production.

Background, decisions and options: [phase 1 proposal](../analysis/phase1-static-site-20261023.md).

## Current vs. desired
- **Now:** git repo with the docs skeleton and the mockup. No code, no remote.
- **Desired:** Astro project (static output, plain CSS, Markdown content per
  language) in a public GitHub repository with a Pages deploy on every push
  to `main`, structured so later phases (CMS, portfolio, blog, calendar,
  shop) add files rather than restructure.

## Constraints & assumptions
- Mobile first: base CSS is the phone layout; wider layouts via `min-width`.
  Every phase is checked at 375, 768 and 1440 px.
- Static output only: must run on GitHub Pages (sub-path) and plain
  mijndomein web hosting (domain root). Nothing server-side.
- Language: device in the Netherlands (time zone Europe/Amsterdam or region NL) or a Dutch browser language → Dutch, otherwise English; a manual
  switch overrides and is remembered. No geo-IP (not available on either host).
- Contact form through a third-party form service (Web3Forms or Formspree).
- No external trackers, embeds or font CDNs, so no cookie banner is needed.
- Placeholder texts and the mockup's images until Daan delivers content.
- Node 26 / npm 11 available locally; GitHub CLI logged in as `ErikCornelisse`.
- "Green" for this project: `npm run build` and `npx astro check` pass, and
  the page renders without console errors at the three widths.
- Commits go directly to `main` (one or a few per phase).

## Phases
| # | Phase | Delivers | Depends on | Status |
|---|-------|----------|------------|--------|
| 1 | [Repository and scaffold](phase-01-scaffold.md) | Astro project, GitHub repo, Pages deploy of a placeholder page | — | done (intent.md still open) |
| 2 | [Tokens, fonts and bands](phase-02-tokens.md) | Design tokens, self-hosted fonts, cream/paper bands, mobile-first base | 1 | done |
| 3 | [i18n skeleton](phase-03-i18n.md) | `/nl/` and `/en/`, root language chooser, switch, hreflang | 2 | done |
| 4 | [Hero and header](phase-04-hero.md) | Art-directed hero, header nav, *Mijn verhaal* scroll link | 3 | done |
| 5 | [Work blocks](phase-05-works.md) | `works` collection and `WorkBlock` for the three works in both languages | 4 | done |
| 6 | [About and contact](phase-06-contact.md) | *Over mij*, e-mail, social links, contact form, brush button | 5 | todo |
| 7 | [Quality pass](phase-07-quality.md) | Accessibility, performance, privacy note, meta / Open Graph | 6 | todo |
| 8 | [Production hand-over](phase-08-handover.md) | Root-path build and upload instructions for mijndomein | 7 | todo |

Status: `todo` → `in-progress` → `done`. This table is the source of truth
for progress.

## Open questions
1. ~~Repository name and visibility.~~ Resolved: `ErikCornelisse/daan-cornelisse-site`, public, Pages at <https://erikcornelisse.github.io/daan-cornelisse-site/>.
2. Form service (Web3Forms or Formspree) and the address that receives the
   messages. Needed for phase 6; the form can ship disabled until then.
3. Who writes the English texts: Daan, or Claude drafts and Daan checks.
4. Daan's e-mail address and Instagram, YouTube and LinkedIn URLs (placeholders until known).
5. Daan's mijndomein package: web hosting with SFTP/FTP access? Needed for phase 8.
6. Permission for the MAX/EpilepsieNL TV still, or a replacement image.
