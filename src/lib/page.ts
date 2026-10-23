// The structure of the landing page: src/content/page.json, checked against
// the rules below, and resolved per language into sections, topics, bands and
// the header menu. The site manager applies the same rules before saving.

import { getEntry, type CollectionEntry } from 'astro:content';
import { z } from 'astro/zod';
import pageData from '../content/page.json';
import type { Lang } from '../i18n/ui';

export type Band = 'cream' | 'paper';

const id = z.string().regex(/^[a-z0-9-]+$/, 'Use lowercase letters, digits and hyphens');

const sectionRef = z.object({
	id,
	type: z.enum(['hero', 'section', 'contact']),
	topics: z.array(id).default([]),
	menu: z.boolean().default(false),
	band: z.enum(['cream', 'paper']).optional(),
	link: id.optional(),
});

export const pageSchema = z
	.object({ sections: z.array(sectionRef).min(2) })
	.superRefine(({ sections }, ctx) => {
		const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
		const types = sections.map((s) => s.type);
		if (types[0] !== 'hero' || types.filter((t) => t === 'hero').length !== 1)
			fail('There must be exactly one hero, and it must be the first section.');
		if (types.at(-1) !== 'contact' || types.filter((t) => t === 'contact').length !== 1)
			fail('There must be exactly one contact section, and it must be the last section.');
		const ids = sections.map((s) => s.id);
		for (const dup of new Set(ids.filter((x, i) => ids.indexOf(x) !== i))) fail(`Section id "${dup}" is used twice.`);
		const topics = sections.flatMap((s) => s.topics);
		for (const dup of new Set(topics.filter((x, i) => topics.indexOf(x) !== i)))
			fail(`Topic "${dup}" is in more than one section.`);
		for (const s of sections) {
			if (s.type !== 'section' && s.topics.length) fail(`The ${s.type} section cannot hold topics.`);
		}
		const hero = sections[0];
		if (hero?.type === 'hero' && hero.link) {
			const target = sections.find((s) => s.id === hero.link);
			if (!target || target.type === 'hero') fail(`The hero links to "${hero.link}", which is not a section.`);
		}
	});

export type SectionRef = z.infer<typeof sectionRef>;

export interface ResolvedTopic {
	entry: CollectionEntry<'topics'>;
	/** Language of the text actually shown; differs from the page when it falls back to Dutch. */
	lang: Lang;
	fallback: boolean;
	band: Band;
}

export interface ResolvedSection {
	ref: SectionRef;
	entry: CollectionEntry<'sections'>;
	lang: Lang;
	fallback: boolean;
	anchor: string;
	headingId: string;
	/** True when the section has text or an image of its own, shown in its own band. */
	hasOwnContent: boolean;
	/** Band of the section's own part (own content, or heading only). */
	band: Band;
	topics: ResolvedTopic[];
}

export interface MenuItem {
	label: string;
	anchor: string;
}

export interface ResolvedPage {
	sections: ResolvedSection[];
	menu: MenuItem[];
	/** Anchor the hero's link points to. */
	heroLink?: string;
}

const structure = pageSchema.parse(pageData);

async function pick<C extends 'sections' | 'topics'>(collection: C, entryId: string, lang: Lang) {
	const entry = await getEntry(collection, `${lang}/${entryId}`);
	if (entry) return { entry, lang };
	const fallback = lang === 'nl' ? undefined : await getEntry(collection, `nl/${entryId}`);
	if (fallback) return { entry: fallback, lang: 'nl' as Lang };
	throw new Error(`Missing src/content/${collection}/nl/${entryId}.md (listed in src/content/page.json)`);
}

/**
 * Each band takes the other colour than the band before it, starting with cream
 * after the hero. A section may force its colour ("band" in page.json); the
 * bands after it then alternate from that colour.
 */
function bandCounter() {
	let previous: Band | undefined;
	return (forced?: Band): Band => {
		const band = forced ?? (previous === 'cream' ? 'paper' : 'cream');
		previous = band;
		return band;
	};
}

export async function loadPage(lang: Lang): Promise<ResolvedPage> {
	const nextBand = bandCounter();
	const sections: ResolvedSection[] = [];
	for (const ref of structure.sections) {
		const { entry, lang: shownLang } = await pick('sections', ref.id, lang);
		if (ref.type !== 'hero' && !entry.data.anchor)
			throw new Error(`src/content/sections/${shownLang}/${ref.id}.md needs an anchor.`);
		const hasOwnContent = ref.type === 'contact' || Boolean(entry.body?.trim() || entry.data.image);
		// Without own content the heading sits in the band of the first topic.
		const ownBand = ref.type === 'hero' ? 'cream' : hasOwnContent || !ref.topics.length ? nextBand(ref.band) : undefined;
		const topics: ResolvedTopic[] = [];
		for (const [index, topicId] of ref.topics.entries()) {
			const topic = await pick('topics', topicId, lang);
			topics.push({
				...topic,
				fallback: topic.lang !== lang,
				band: nextBand(index === 0 && !ownBand ? ref.band : undefined),
			});
		}
		sections.push({
			ref,
			entry,
			lang: shownLang,
			fallback: shownLang !== lang,
			anchor: entry.data.anchor ?? ref.id,
			headingId: `${ref.id}-heading`,
			hasOwnContent,
			band: ownBand ?? topics[0]?.band ?? 'cream',
			topics,
		});
	}
	const anchors = sections.filter((s) => s.ref.type !== 'hero').map((s) => s.anchor);
	for (const dup of new Set(anchors.filter((a, i) => anchors.indexOf(a) !== i)))
		throw new Error(`Two sections share the anchor "${dup}" on the ${lang} page.`);
	const menu = sections
		.filter((s) => s.ref.menu)
		.map((s) => ({ label: s.entry.data.menuLabel ?? s.entry.data.title, anchor: s.anchor }));
	const hero = sections[0];
	const heroLink = hero.ref.link ? sections.find((s) => s.ref.id === hero.ref.link)?.anchor : undefined;
	return { sections, menu, heroLink };
}
