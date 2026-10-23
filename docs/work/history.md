# History

Append-only log of what happened to the work in this project and why.
One dated line per event, newest at the bottom: a plan started, completed
or abandoned (and archived to `docs/archive/`); a document promoted to
`docs/specs/`; a decision that changed
direction. Link to the document concerned. The state of a plan is not
recorded here — it lives in the plan's own status table.

- 2026-10-23 — Project initialised.
- 2026-10-23 — Phase 1 plan started: [phase1-mvp](phase1-mvp/plan.md), based on the [phase 1 proposal](analysis/phase1-static-site-20261023.md).
- 2026-10-23 — Fonts chosen for phase 1: Belleza (headings) and Source Serif 4 (body text), free and self-hosted; a licensed Optima may replace Belleza later ([step 2](phase1-mvp/phase-02-tokens.md)).
- 2026-10-23 — Language detection refined: besides the browser language, the device time zone (Europe/Amsterdam) and a region code NL count as "in the Netherlands", so Dutch visitors with an English browser get Dutch ([step 3](phase1-mvp/phase-03-i18n.md)).
- 2026-10-23 — Accent colours adjusted for contrast (WCAG AA), provisionally until Daan confirms: orange #D68641 → #B56424, the white *Tijd Voor MAX* title → brown #5B2F1A, the quote in ink instead of white ([step 5](phase1-mvp/phase-05-works.md)).
- 2026-10-23 — Placeholders for about, contact and *Voor ik sluit*, the e-mail address and the profile links filled from daniel-cornelisse.nl; Spotify replaces YouTube in the social links ([current site](analysis/current-site-20261023.md)).
- 2026-10-23 — Site phase 2 started as a custom local site manager (Python, FastAPI) in `manager/`; option B of the content-editing advice. Plan: [plan-site-manager.md](plan-site-manager.md). Phases 1–2 (overview, content editing, preview) done. Phase 1 step 8 (production hand-over) postponed until Daan has reviewed the site.
