// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// The prototype is served from a GitHub Pages sub-path; production runs at the
// root of Daan's own domain. Override both with SITE and BASE at build time,
// e.g. SITE=https://example.nl BASE=/ npm run build
const site = process.env.SITE ?? 'https://erikcornelisse.github.io';
const base = process.env.BASE ?? '/daan-cornelisse-site';

// https://astro.build/config
export default defineConfig({
	site,
	base,
	trailingSlash: 'always',
	// The CSS is small (about 7 KB); inlining it saves a render-blocking request.
	build: { inlineStylesheets: 'always' },
	// Both languages live under a prefix (/nl/, /en/). The root page picks one
	// (src/pages/index.astro); English is the fallback.
	i18n: {
		locales: ['nl', 'en'],
		defaultLocale: 'en',
		routing: {
			prefixDefaultLocale: true,
			redirectToDefaultLocale: false,
		},
	},
	integrations: [
		sitemap({
			i18n: { defaultLocale: 'en', locales: { nl: 'nl-NL', en: 'en' } },
			// The root page only forwards to /nl/ or /en/; keep it out.
			filter: (page) => new URL(page).pathname !== `${base.replace(/\/?$/, '/')}`,
		}),
	],
});
