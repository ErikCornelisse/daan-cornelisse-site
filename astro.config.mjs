// @ts-check
import { defineConfig } from 'astro/config';

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
});
