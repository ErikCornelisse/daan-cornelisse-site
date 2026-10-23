# Phase 01 — Repository and scaffold

**Objective:** an empty Astro site that builds locally and deploys to GitHub Pages on every push.

**Tasks**
- [ ] Owner fills in `docs/specs/intent.md` — _affects:_ `docs/specs/intent.md` — _done when:_ objective, use case, non-goals and success criteria are written
- [ ] Scaffold Astro with the minimal template in the project root, keeping `docs/` — _affects:_ `package.json`, `astro.config.mjs`, `tsconfig.json`, `src/pages/index.astro` — _done when:_ `npm run dev` serves a placeholder page
- [ ] Add Node ignore rules — _affects:_ `.gitignore` — _done when:_ `node_modules/`, `dist/`, `.astro/` are ignored
- [ ] Make the base path configurable: `site` and `base` from env vars, defaulting to the GitHub Pages sub-path — _affects:_ `astro.config.mjs` — _done when:_ building with `BASE=/` and with the default both produce working links
- [ ] Create the GitHub repository (after the owner confirms name and visibility) and push `main` — _affects:_ remote — _done when:_ the repo exists under `ErikCornelisse`
- [ ] GitHub Actions workflow that builds and deploys to Pages — _affects:_ `.github/workflows/deploy.yml` — _done when:_ a push to `main` updates the Pages URL
- [ ] Update `README.md` with dev, build and deploy commands — _affects:_ `README.md` — _done when:_ a fresh clone can be run from the README alone

**Acceptance:** `npm run build` and `npx astro check` pass; the placeholder page is reachable at the GitHub Pages URL.

**Risk / rollback:** creating a public repository is outward-facing; it is done only after explicit confirmation.
