# Phase 1 proposal — static site from mockup v1

Source: [mockup v1.png](../design/mockup%20v1.png) (2732 × 6292 px, desktop only).

## 1. What the mockup shows

One long landing page made of full-width bands. Two background colours take
turns: warm cream and a textured khaki "paper".

| # | Section | Content | Background |
|---|---|---|---|
| 1 | Hero | Full-bleed photo (figure walking down a path toward the light). Title *Een kijkje in mijn hoofd*, subtitle *Hoe kunst het onzichtbare zichtbaar maakt*, link *Mijn verhaal*. Nav top right: *Over mij – Contact*. The bottom edge fades into cream. | photo |
| 2 | Mediums en Disciplines | Centred section heading for the three work blocks below. | cream |
| 2a | *Als het licht even uitgaat* (purple title) | Two text columns plus an illustration (vase, mask, anemones). Book illustrations for Marije van der Kooij's biography. | cream |
| 2b | *Tijd Voor MAX* (white title) | One text column, a TV still (EpilepsieNL / MAX), a quote, and a photo of a piano with light panels. Music. | paper |
| 2c | *Voor ik sluit* (orange title) | Two text columns plus a square digital artwork. | cream |
| 3 | Over mij | Portrait on the left, three paragraphs on the right. | paper |
| 4 | Contact | One paragraph plus a hand-drawn brush button *Contact me* (annotated "Knop"). | cream |

**Pattern:** sections 2a–2c are the same block: title in an accent colour,
1–2 text columns, 1–2 images, optional quote. That is the main reusable
component, and later it becomes the portfolio entry.

**Style tokens (estimated from the image, to be refined):**

- Cream `#FDDB9F`, paper khaki `#B8A27B` with a grain texture, text `#111`
- Accents per work: purple `#6F6293`, white, orange `#D9843F`
- Headings: humanist sans (Optima-like). Body text: classic serif (Times-like).

**Gaps and issues:**

- All body text is placeholder. Daan supplies the final texts and images;
  phase 1 runs on placeholders until then.
- The mockup is desktop only. The site is mobile first (see §2), so the
  mobile layout must be designed here, not derived afterwards.
- Contrast: the white title and quote on khaki are likely to fail WCAG AA.
- The button text follows the page language (*Neem contact op* / *Contact me*).
- Image rights: the MAX/EpilepsieNL TV still needs permission or a replacement.
- The mockup PNG is 10 MB. Real photos need responsive, compressed versions.

## 2. Decisions (2026-10-23)

| # | Topic | Decision | Consequence |
|---|---|---|---|
| 1 | Language | Dutch and English. Visitors in the Netherlands get Dutch, others English. A switch on every page goes to the other language. | URLs `/nl/…` and `/en/…` from the start. See §4 for how "in the Netherlands" is detected. |
| 2 | Hosting | Prototype in a new GitHub repository on account `ErikCornelisse`. Production on Daan's existing domain at mijndomein.nl. | Prototype on GitHub Pages; production is the same `dist/` folder uploaded to mijndomein. The build must work under a sub-path and at a domain root. |
| 3 | Contact | E-mail address, Instagram, YouTube and LinkedIn links, plus a contact form. | Form through a host-independent form service (§5). |
| 4 | *Mijn verhaal* | Scrolls down to *Over mij*. | Anchor link with smooth scroll (off for reduced motion). |
| 5 | Fonts | Free Optima look-alike now, possibly a licensed font later. | Fonts are self-hosted and set in one token, so a swap touches one file. |
| 6 | Content | Daan provides final texts and images. | Content lives in Markdown per language, easy to hand over or edit. |
| 7 | Layout | **Mobile first, and it must look great on a laptop.** | CSS is written for the phone first, wider layouts added with `min-width` queries; every step is checked at phone and laptop width. |

## 3. Approach

**Astro, static output, plain CSS, content in Markdown.**

| Option | Phase 1 | Later phases | Verdict |
|---|---|---|---|
| Plain HTML + CSS | Fastest start, no tooling | Two languages by hand; no content model; a rewrite by phase 3 | Not a fit with i18n |
| Eleventy | Simple, static | Collections work; images and i18n weaker | Viable alternative |
| **Astro** | Same speed with hot reload; zero JS by default | Built-in i18n routing, content collections for portfolio/blog/events, image optimisation, CMS-friendly | **Recommended** |

The output is plain HTML and CSS in `dist/`, which runs on GitHub Pages and on
ordinary mijndomein web hosting without anything server-side.

**Mobile first in practice:**

- Base CSS is the single-column phone layout (375 px). Two- and three-column
  work blocks, the side-by-side *Over mij* and the wide hero appear from
  about 768 px and 1024 px.
- Fluid type and spacing with `clamp()`, so there are few breakpoints.
- Hero uses art direction: a portrait crop of the photo on phones, the wide
  crop on laptops (`<picture>`).
- Navigation stays small (*Over mij*, *Contact*, language switch), so no
  hamburger menu is needed.
- Touch targets ≥ 44 px; check at 375, 768 and 1440 px in every step.

## 4. Language selection

A static site cannot see the visitor's location on the server, and
mijndomein shared hosting offers no geo-IP. The practical proxy is the
browser's language:

1. `/` is a tiny page with an inline script: a stored manual choice wins;
   otherwise a browser language starting with `nl` goes to `/nl/`, anything
   else to `/en/`. Without JavaScript it shows two plain links.
2. The language switch links to the same page in the other language and
   stores the choice (`localStorage`, wrapped so it fails safely).
3. Every page carries `hreflang` alternates so search engines index both.

This treats Dutch-speaking visitors in Belgium as Dutch and English-set
browsers in the Netherlands as English. True country detection would need an
edge function at the host, which neither GitHub Pages nor mijndomein shared
hosting provides. It can be revisited if production moves.

## 5. Contact form

A form needs something to receive the post. Options that work identically on
GitHub Pages and on mijndomein:

| Option | Notes |
|---|---|
| **Web3Forms** or **Formspree** (free tier) | A plain HTML form posting to the service, which mails Daan. No server code. Data passes through a third party, which goes in the privacy note. **Recommended.** |
| PHP mail script on mijndomein | No third party, but does not run on GitHub Pages, so the prototype cannot test it. |

Spam protection with a honeypot field (plus the service's own filtering). The
e-mail address is shown as a `mailto:` link; social links use inline SVG
icons, with no embedded widgets or trackers, so no cookie banner is needed.

## 6. Structure

```
src/
  pages/
    index.astro                language chooser (redirect script + fallback links)
    [lang]/index.astro         the landing page for nl and en
  layouts/BaseLayout.astro     <html lang>, meta, hreflang, fonts, header/footer
  components/
    Header.astro               name + nav + LanguageSwitch
    LanguageSwitch.astro
    Hero.astro
    Section.astro              band with variant="cream" | "paper"
    WorkBlock.astro            title + accent, columns, media, quote
    About.astro
    Contact.astro              text, mailto, social links, form, brush button
    ContactForm.astro
    SocialLinks.astro
    Footer.astro
  content/
    works/nl/*.md, works/en/*.md      one file per work, same slug in both
    pages/nl/{about,contact}.md, pages/en/…
  content.config.ts            schemas for the collections
  i18n/ui.ts                   interface strings (nav, buttons, form labels)
  data/site.json               e-mail, social URLs, form endpoint key
  styles/tokens.css            colours, fonts, spacing, breakpoints
  styles/global.css            reset, typography, section variants
  assets/images/               originals; Astro generates responsive versions
  assets/fonts/                self-hosted fonts (no Google Fonts CDN)
public/                        favicon, paper texture, robots.txt
```

Example work entry (`src/content/works/nl/als-het-licht-even-uitgaat.md`):

```markdown
---
title: Als het licht even uitgaat
discipline: Illustratie
accent: purple
order: 1
images:
  - src: ../../../assets/images/vaas-masker.png
    alt: Getekende vaas en masker met anemonen
---
Wat je van de buitenkant ziet is maar een klein gedeelte …
```

The body text flows into one or two columns via CSS `columns`, so the content
files carry no layout decisions.

## 7. Phase 1 steps

Each step leaves a working page, viewable on phone and laptop.

1. **Repository and scaffold.** New GitHub repo, Astro minimal template, Node
   ignore rules, GitHub Pages deploy workflow with the right `base` path.
   Fill in `docs/specs/intent.md` first.
2. **Tokens, fonts and section bands.** Colours, the two backgrounds with
   grain, fluid type; font comparison (free Optima look-alikes, e.g. *Belleza*
   or *Tenor Sans*, with a readable serif for body text). Mobile layout first.
3. **i18n skeleton.** `/nl/` and `/en/`, root language chooser, switch,
   `hreflang`, `ui.ts`.
4. **Hero and header.** Art-directed hero image, title block, anchor nav,
   *Mijn verhaal* scroll link.
5. **WorkBlock and works collection.** The three blocks from Markdown in both
   languages, stacked on phones, columns on laptops.
6. **About and contact.** Portrait plus text; e-mail, social links, contact
   form via the form service, brush button.
7. **Quality pass.** Contrast, alt texts, keyboard use, image sizes,
   Lighthouse (target ≥ 95 on mobile), privacy note, meta and Open Graph.
8. **Production hand-over.** A build for the domain root and written upload
   instructions for mijndomein (SFTP/FTP). Automating that upload is phase 2.

## 8. How later phases build on this

| Phase | Extension | Builds on |
|---|---|---|
| 2 Keeping it up to date | Git-based CMS (Pages CMS or Decap CMS) editing the same Markdown, a Claude-assisted workflow (including draft translations for Daan to check), and automatic upload to mijndomein on each release | Content collections, preview deploys |
| 3 Portfolio | `[lang]/werk/[slug]` pages and an overview from `works` | `WorkBlock`, `works` collection |
| 4 Blog | `posts` collection per language, list + detail pages, RSS | Layout, collections |
| 5 Calendar | `events` collection (date, place, link), upcoming/past, optional ICS feed | Collections |
| 6 Shop | External first (Shopify Buy Button, Snipcart or Stripe Payment Links) so the site stays static | Portfolio pages as product pages |

Navigation moves from anchors (phase 1) to real pages from phase 3. Keep
`site.json` and `ui.ts` as the single sources for nav and labels.

## 9. Still open (not blocking)

- Repository name and visibility (public is needed for free GitHub Pages).
- Which form service, and the address that receives the messages.
- Who writes the English texts: Daan, or Claude drafts and Daan checks.
- Daan's mijndomein package: confirm it is web hosting with SFTP/FTP access.
