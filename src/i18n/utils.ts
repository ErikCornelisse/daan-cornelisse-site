import { getAbsoluteLocaleUrl, getRelativeLocaleUrl } from 'astro:i18n';
import { languages, ui, type Lang, type UiKey } from './ui';

export function isLang(value: unknown): value is Lang {
	return typeof value === 'string' && value in languages;
}

export function useTranslations(lang: Lang) {
	return (key: UiKey) => ui[lang][key];
}

export function otherLang(lang: Lang): Lang {
	return lang === 'nl' ? 'en' : 'nl';
}

/** The path of the current page without base and language prefix, e.g. '' or 'werk/foo/'. */
export function pathWithoutLang(url: URL): string {
	const base = import.meta.env.BASE_URL.replace(/\/?$/, '/');
	const rest = url.pathname.startsWith(base) ? url.pathname.slice(base.length) : url.pathname.replace(/^\//, '');
	const [first, ...others] = rest.split('/');
	return isLang(first) ? others.join('/') : rest;
}

export function localeUrl(lang: Lang, path = ''): string {
	return getRelativeLocaleUrl(lang, path);
}

export function absoluteLocaleUrl(lang: Lang, path = ''): string {
	return getAbsoluteLocaleUrl(lang, path);
}
