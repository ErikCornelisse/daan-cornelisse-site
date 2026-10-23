// Interface strings per language. Page content (texts about the works, about
// Daan, contact) lives in src/content/; only labels and fixed headings are here.

export const languages = {
	nl: 'Nederlands',
	en: 'English',
} as const;

export type Lang = keyof typeof languages;

export const defaultLang: Lang = 'en';

// Key under which a manual language choice is remembered in the browser.
export const langStorageKey = 'dc-lang';

const nl = {
	'site.title': 'Daan Cornelisse',
	'site.description': 'Daan Cornelisse maakt illustraties, muziek en digitale kunst over wat je van buiten niet ziet.',
	'nav.about': 'Over mij',
	'nav.contact': 'Contact',
	'section.works': 'Mediums en Disciplines',
	'section.about': 'Over mij',
	'section.contact': 'Contact',
	'id.about': 'over-mij',
	'id.contact': 'contact',
	'lang.switch': 'Deze pagina in het Nederlands',
} as const;

const en: Record<keyof typeof nl, string> = {
	'site.title': 'Daan Cornelisse',
	'site.description': 'Daan Cornelisse makes illustrations, music and digital art about what you cannot see from the outside.',
	'nav.about': 'About me',
	'nav.contact': 'Contact',
	'section.works': 'Media and Disciplines',
	'section.about': 'About me',
	'section.contact': 'Contact',
	'id.about': 'about',
	'id.contact': 'contact',
	'lang.switch': 'This page in English',
};

export const ui: Record<Lang, Record<keyof typeof nl, string>> = { nl, en };

export type UiKey = keyof typeof nl;
