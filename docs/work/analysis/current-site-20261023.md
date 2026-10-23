# Daan's current site — daniel-cornelisse.nl

Read on 2026-10-23 to find reusable content and the production hosting
details for [phase 1, step 8](../phase1-mvp/phase-08-handover.md).

## Hosting

| Item | Finding |
|---|---|
| Domain | `daniel-cornelisse.nl` (no `www` record of its own; `www` resolves to the same IP) |
| DNS | `nsn1/nsn2.mijndomein.nl` |
| Server | `server159.mijndomeinhosting.nl` (194.213.127.119), Plesk on Linux, nginx in front |
| HTTPS | Active; `http://` redirects to `https://` with a 301 |
| E-mail | No MX records on the domain; Daan uses a Gmail address |
| Site type | Hand-made static HTML, last modified 14 May 2024; no `robots.txt` or sitemap |

Consequences for step 8:

- The new `dist/` can replace the old files in the Plesk document root
  (normally `httpdocs/`), via the Plesk file manager or (S)FTP.
- Back up the old site first (download `httpdocs/`).
- Production build: `SITE=https://daniel-cornelisse.nl BASE=/ npm run build`.
- Old URLs that may be linked or indexed should redirect (301) to the new
  pages; whether `.htaccess` is honoured depends on Plesk's nginx/Apache
  setting and has to be checked, otherwise use Plesk's own redirect settings.

| Old URL | Redirect to |
|---|---|
| `/index.html` | `/` |
| `/work.html` | `/nl/` (works section; portfolio in phase 3) |
| `/blog.html` and `/NieuwsItem_*.html` | `/nl/` (blog in phase 4) |
| `/about.html` | `/nl/#over-mij` |
| `/contact.html` | `/nl/#contact` |

## Contact details and links

- E-mail: `danielcornelis.nl@gmail.com`
- Instagram: <https://www.instagram.com/daancornelisse/>
- LinkedIn: <https://www.linkedin.com/in/cornelissedaan/>
- Spotify (artist): <https://open.spotify.com/artist/7dPe6JDh0Z6esY8hMY0Mtp>
- YouTube: no channel linked; the only YouTube link is the *Accept the Gap*
  campaign video (<https://www.youtube.com/watch?v=fKMWWyBJWsU>).

## Content that can replace placeholders (phase 1)

- **About** (`about.html`): two parts, *Mijn werk* (curious, ambitious work;
  specialised in 3D design, cinematography and storytelling) and *Epilepsie*
  (conscious seizures as both fear and his greatest strength; a source of
  inspiration). Dutch only.
- **Contact** (`contact.html`): "Ben je op zoek naar grafische ontwerpen,
  creatief advies of heb je een eigen verzoek, neem dan gerust contact met me op."
- **Voor ik sluit**: made for the museum exhibition *Onzichtbaar Verlies*
  about epilepsy, shown in the Beautiful Distress House, Amsterdam
  (March–May 2024). This is the third work block in the mockup.

## Content for later phases

**Portfolio (phase 3)** — `work.html`:

| Work | Description |
|---|---|
| Grafisch portfolio | Link to graphic work |
| Onzichtbaar Verlies | *Voor ik sluit*, museum exhibition on epilepsy, Beautiful Distress House Amsterdam |
| Kleur de Stad (Mr Beam) | Projections on notable buildings in Utrecht |
| 1905 | For Monumentendag 2021 at Fort bij Aalsmeer; piano pieces (Spotify) |
| Twee voor Twaalf | 3D animation on the origin of the compact disc for the TV quiz *2 voor 12* |

**Blog / news (phase 4)** — `blog.html`:

| Date | Item |
|---|---|
| 2024-03-03 | Opening of *Onzichtbaar Verlies* (on show until 26 May 2024) |
| 2024-01-01 | Invitation to make a work for the exhibition |
| 2023-05-14 | RunExpected 2023, "Team Fibrosaurus", for LetsBeatNF! |
| 2023-03-29 | *Accept the Gap!* campaign by Stichting Emma At Work, as ambassador |
| 2020-12-20 | GIG At Home: own compositions with a string duo, for 1000+ viewers |

Images on the old site live under `images/` (for example
`FullSized_Drieluik_Epilepsie.png`, `KleurDeStad_1.jpg`,
`FortVijfhuizen2021.png`, `DanielCornelisse_Blue_Background.png`). They were
not downloaded; ask Daan for the originals, which will be better quality.
