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

export const collections = { pages };
