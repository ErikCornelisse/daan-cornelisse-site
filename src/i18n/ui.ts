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
	'nav.label': 'Hoofdmenu',
	'nav.about': 'Over mij',
	'nav.contact': 'Contact',
	'section.works': 'Mediums en Disciplines',
	'id.about': 'over-mij',
	'id.contact': 'contact',
	'lang.switch': 'Deze pagina in het Nederlands',
	'contact.open': 'Neem contact op',
	'contact.email': 'E-mail',
	'contact.elsewhere': 'Daan online',
	'social.instagram': 'Daan op Instagram',
	'social.youtube': 'Daan op YouTube',
	'social.linkedin': 'Daan op LinkedIn',
	'form.name': 'Naam',
	'form.email': 'E-mailadres',
	'form.message': 'Bericht',
	'form.send': 'Versturen',
	'form.sending': 'Bezig met versturen…',
	'form.success': 'Dank je wel! Je bericht is verstuurd; Daan neemt zo snel mogelijk contact met je op.',
	'form.error': 'Het versturen is niet gelukt. Probeer het later nog eens of mail Daan rechtstreeks.',
	'form.notConnected': 'Dit formulier is nog niet gekoppeld en verstuurt niets. Mail Daan voorlopig rechtstreeks.',
	'form.privacy': 'Je bericht gaat via de dienst Web3Forms naar Daan en wordt alleen gebruikt om je te antwoorden.',
	'form.subject': 'Nieuw bericht via de website',
} as const;

const en: Record<keyof typeof nl, string> = {
	'site.title': 'Daan Cornelisse',
	'site.description': 'Daan Cornelisse makes illustrations, music and digital art about what you cannot see from the outside.',
	'nav.label': 'Main menu',
	'nav.about': 'About me',
	'nav.contact': 'Contact',
	'section.works': 'Media and Disciplines',
	'id.about': 'about',
	'id.contact': 'contact',
	'lang.switch': 'This page in English',
	'contact.open': 'Contact me',
	'contact.email': 'E-mail',
	'contact.elsewhere': 'Daan online',
	'social.instagram': 'Daan on Instagram',
	'social.youtube': 'Daan on YouTube',
	'social.linkedin': 'Daan on LinkedIn',
	'form.name': 'Name',
	'form.email': 'E-mail address',
	'form.message': 'Message',
	'form.send': 'Send',
	'form.sending': 'Sending…',
	'form.success': 'Thank you! Your message has been sent; Daan will get back to you as soon as possible.',
	'form.error': 'Sending failed. Please try again later or e-mail Daan directly.',
	'form.notConnected': 'This form is not connected yet and sends nothing. For now, please e-mail Daan directly.',
	'form.privacy': 'Your message reaches Daan through the Web3Forms service and is only used to reply to you.',
	'form.subject': 'New message from the website',
};

export const ui: Record<Lang, Record<keyof typeof nl, string>> = { nl, en };

export type UiKey = keyof typeof nl;
