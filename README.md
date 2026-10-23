# Daan Cornelisse

Web site promoting the work of the artist Daan Cornelisse.

The objective and main use case are in [docs/specs/intent.md](docs/specs/intent.md).
The current plan is [docs/work/phase1-mvp/plan.md](docs/work/phase1-mvp/plan.md).

## Development

Requires Node 22.23 or newer.

| Command | What it does |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Dev server at `http://localhost:4321/daan-cornelisse-site/` |
| `npm run check` | Type and template check (`astro check`) |
| `npm run build` | Static build into `dist/` |
| `npm run preview` | Serve the build locally |

## Deployment

- **Prototype:** every push to `main` builds and deploys to GitHub Pages
  (`.github/workflows/deploy.yml`) at
  <https://erikcornelisse.github.io/daan-cornelisse-site/>.
- **Production:** build for the domain root and upload `dist/` to the web
  hosting at mijndomein.nl:

  ```bash
  SITE=https://<domain> BASE=/ npm run build
  ```

`SITE` and `BASE` default to the GitHub Pages values (see `astro.config.mjs`).
