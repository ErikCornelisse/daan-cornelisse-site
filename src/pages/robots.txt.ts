import type { APIRoute } from 'astro';

// Points crawlers at the sitemap. The prototype is kept out of search results
// by the noindex meta tag in BaseLayout, which crawlers can only see when
// they are allowed to fetch the pages.
export const GET: APIRoute = ({ site }) => {
	const sitemap = new URL(`${import.meta.env.BASE_URL.replace(/\/?$/, '/')}sitemap-index.xml`, site);
	return new Response(`User-agent: *\nAllow: /\n\nSitemap: ${sitemap.href}\n`, {
		headers: { 'Content-Type': 'text/plain; charset=utf-8' },
	});
};
