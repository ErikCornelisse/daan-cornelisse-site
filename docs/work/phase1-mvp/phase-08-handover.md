# Phase 08 — Production hand-over

**Objective:** Daan can publish the site on his own domain at mijndomein.nl.

**Tasks**
- [ ] Production build script for the domain root (`BASE=/`, `SITE=https://<domain>`) — _affects:_ `package.json` — _done when:_ `npm run build:prod` produces a `dist/` with root-relative links
- [ ] Apache config for mijndomein: HTTPS redirect, caching headers, 404 page — _affects:_ `public/.htaccess`, `src/pages/404.astro` — _done when:_ the build includes them and they are harmless on GitHub Pages
- [ ] Upload instructions (SFTP/FTP, which folder, how to replace a release) — _affects:_ `docs/readme/deploy-readme.md` — _done when:_ someone without the repo history can publish from the instructions
- [ ] Trial upload to the domain (or a sub-folder) together with Daan — _affects:_ — _done when:_ both languages, the redirect and the form work on the domain

**Acceptance:** the site runs on Daan's domain; automating the upload is left for phase 2.
