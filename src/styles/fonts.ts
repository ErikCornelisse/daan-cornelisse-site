// Fonts loaded by the site, latin subsets only. The site manager (Stijl)
// rewrites this file from its font list; by hand, change these imports and the
// --font-* values in tokens.css together.
import '@fontsource/belleza/latin-400.css';
import '@fontsource/source-serif-4/latin-400.css';
import '@fontsource/source-serif-4/latin-400-italic.css';
import '@fontsource/source-serif-4/latin-700.css';
import headingFont from '@fontsource/belleza/files/belleza-latin-400-normal.woff2?url';
import bodyFont from '@fontsource/source-serif-4/files/source-serif-4-latin-400-normal.woff2?url';

export const preloadFonts = [headingFont, bodyFont];
