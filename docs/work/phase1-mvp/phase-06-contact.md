# Phase 06 — About and contact

**Objective:** *Over mij* and a complete contact section: e-mail, social links and a working form.

**Tasks**
- [ ] `About` component: portrait above text on phones, side by side from 768 px; text from `pages/{nl,en}/about.md` — _affects:_ `src/components/About.astro`, `src/content/pages/` — _done when:_ it matches the mockup on a laptop and reads well on a phone
- [ ] Site data: e-mail address, Instagram, YouTube, LinkedIn URLs, form endpoint key — _affects:_ `src/data/site.json` — _done when:_ components read these values from this file only
- [ ] `SocialLinks` with inline SVG icons and accessible labels — _affects:_ `src/components/SocialLinks.astro` — _done when:_ links open the right profiles and have visible focus
- [ ] `ContactForm`: name, e-mail, message, honeypot; posts to the chosen form service; labels and messages per language; success and error states — _affects:_ `src/components/ContactForm.astro` — _done when:_ a test message from the Pages site arrives at the receiving address
- [ ] Brush-style *Contact me* / *Neem contact op* button as SVG or CSS shape, linking to the form — _affects:_ `src/components/Contact.astro` — _done when:_ the button scales cleanly and stays legible at 375 px

**Acceptance:** build green; a form submission works on the deployed prototype in both languages.

**Risk / rollback:** if the form service is not decided yet, ship the form hidden behind a flag in `site.json` and keep the e-mail link as the contact route.
