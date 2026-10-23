import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Page texts per language: src/content/pages/<lang>/<page>.md, so the entry
// id is e.g. 'nl/home'. Hero fields are only used by the home page.
const pages = defineCollection({
	loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
	schema: z.object({
		title: z.string(),
		subtitle: z.string().optional(),
		cta: z.string().optional(),
		imageAlt: z.string().optional(),
	}),
});

// One file per work and language: src/content/works/<lang>/<slug>.md, with
// the same slug in both languages. Shown as blocks on the landing page now,
// and as portfolio entries in a later phase.
const works = defineCollection({
	loader: glob({ pattern: '**/*.md', base: './src/content/works' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			discipline: z.string(),
			accent: z.enum(['purple', 'orange', 'brown']),
			order: z.number().int(),
			images: z
				.array(
					z.object({
						src: image(),
						alt: z.string().min(1, 'Every image needs an alt text'),
					}),
				)
				.min(1)
				.max(2),
			quote: z.string().optional(),
		}),
});

export const collections = { pages, works };
