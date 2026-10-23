import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// The landing page is built from src/content/page.json (structure, rules in
// src/lib/page.ts) plus the two collections below. Entry ids are
// '<lang>/<id>', e.g. 'nl/over-mij'; the same id in both languages.

// Section texts: the hero, the sections in between and contact.
const sections = defineCollection({
	loader: glob({ pattern: '**/*.md', base: './src/content/sections' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			// Anchor in the page URL (#over-mij); every section except the hero has one.
			anchor: z
				.string()
				.regex(/^[a-z0-9-]+$/, 'Use lowercase letters, digits and hyphens')
				.optional(),
			// Label in the header menu when the section is in the menu; defaults to the title.
			menuLabel: z.string().optional(),
			// Hero only
			subtitle: z.string().optional(),
			cta: z.string().optional(),
			portrait: image().optional(),
			// The section's own image (the hero's photo, or an image beside the text)
			image: z
				.object({
					src: image(),
					alt: z.string().min(1, 'Every image needs an alt text'),
				})
				.optional(),
		}),
});

// Topics: the blocks inside a section (today the works). Which section they
// are in, and in what order, is set in page.json.
const topics = defineCollection({
	loader: glob({ pattern: '**/*.md', base: './src/content/topics' }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			discipline: z.string(),
			accent: z.enum(['purple', 'orange', 'brown']),
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

// Pages of their own, outside the landing page (the privacy statement).
const pages = defineCollection({
	loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
	schema: z.object({
		title: z.string(),
	}),
});

export const collections = { sections, topics, pages };
