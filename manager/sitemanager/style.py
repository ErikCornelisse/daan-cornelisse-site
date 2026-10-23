"""Style settings: the whitelisted values in src/styles/tokens.css and the fonts
in src/styles/fonts.ts, with WCAG contrast checks.

Only the listed tokens are edited, value by value, so the comments and every
other line of tokens.css stay as they are.
"""

import re
from dataclasses import dataclass
from pathlib import Path

# (token, label) — colours the site uses for backgrounds and text.
COLORS = [
    ("color-cream", "Achtergrond licht (crème)"),
    ("color-paper", "Achtergrond papier (khaki)"),
    ("color-dark", "Achtergrond donker (achter de foto, voettekst)"),
    ("color-ink", "Tekst"),
    ("color-on-photo", "Tekst op de foto en in de voettekst"),
    ("color-accent-purple", "Accent paars"),
    ("color-accent-orange", "Accent oranje"),
    ("color-accent-brown", "Accent bruin"),
    ("color-brush", "Contactknop"),
    ("color-brush-text", "Tekst op de contactknop"),
]


@dataclass(frozen=True)
class Scale:
    token: str
    label: str
    minimum: float
    maximum: float
    step: float
    unit: str = ""  # "" = factor shown as a percentage; "rem" = width


SCALES = [
    Scale("scale-text", "Tekstgrootte", 0.85, 1.25, 0.05),
    Scale("scale-heading", "Grootte van de koppen", 0.8, 1.3, 0.05),
    Scale("scale-space", "Ruimte tussen onderdelen", 0.75, 1.3, 0.05),
    Scale("container", "Breedte van de inhoud op grote schermen", 56, 80, 2, "rem"),
]


@dataclass(frozen=True)
class Font:
    key: str  # Fontsource package name
    family: str
    label: str


HEADING_FONTS = [
    Font("belleza", "Belleza", "Belleza (lijkt op Optima)"),
    Font("tenor-sans", "Tenor Sans", "Tenor Sans"),
    Font("marcellus", "Marcellus", "Marcellus (klassieke kapitalen)"),
]
BODY_FONTS = [
    Font("source-serif-4", "Source Serif 4", "Source Serif 4 (goed leesbaar op schermen)"),
    Font("libre-caslon-text", "Libre Caslon Text", "Libre Caslon Text"),
    Font("crimson-pro", "Crimson Pro", "Crimson Pro"),
    Font("eb-garamond", "EB Garamond", "EB Garamond"),
]
FALLBACK = {
    "heading": "Optima, Candara, 'Segoe UI', sans-serif",
    "body": "'Times New Roman', Times, serif",
}

# The values of phase 1, for "Standaard herstellen".
DEFAULTS = {
    "color-cream": "#ffdda3",
    "color-paper": "#b9a47a",
    "color-dark": "#1a1a14",
    "color-ink": "#111111",
    "color-on-photo": "#ffdda3",
    "color-accent-purple": "#6e5f85",
    "color-accent-orange": "#b56424",
    "color-accent-brown": "#5b2f1a",
    "color-brush": "#000000",
    "color-brush-text": "#d68641",
    "scale-text": "1",
    "scale-heading": "1",
    "scale-space": "1",
    "container": "68rem",
    "font-heading": "belleza",
    "font-body": "source-serif-4",
}

# Text that must stay readable, as (text colour, background, minimum ratio, description).
# 4.5:1 for normal text, 3:1 for large text (headings, the button label).
FIXED_PAIRS = [
    ("color-ink", "color-cream", 4.5, "Tekst op crème"),
    ("color-ink", "color-paper", 4.5, "Tekst op papier"),
    ("color-on-photo", "color-dark", 4.5, "Tekst in de voettekst"),
    ("color-brush-text", "color-brush", 3.0, "Tekst op de contactknop"),
]
ACCENT_MINIMUM = 3.0

HEX = re.compile(r"^#[0-9a-f]{6}$")


def token_pattern(name: str) -> re.Pattern:
    return re.compile(rf"^(\s*--{re.escape(name)}:\s*)([^;]+)(;)", re.MULTILINE)


# Contrast ------------------------------------------------------------------


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass
class ContrastCheck:
    label: str
    foreground: str
    background: str
    minimum: float

    @property
    def ratio(self) -> float:
        return contrast(self.foreground, self.background)

    @property
    def ok(self) -> bool:
        return self.ratio >= self.minimum


def contrast_checks(
    colors: dict[str, str], works: list[tuple[str, str, str]]
) -> list[ContrastCheck]:
    """Checks for the fixed pairs and for each work title on the band it sits on.

    `works` holds (title, accent, band) with accent 'purple'|'orange'|'brown' and band
    'cream'|'paper'.
    """
    checks = [
        ContrastCheck(label, colors[fg], colors[bg], minimum)
        for fg, bg, minimum, label in FIXED_PAIRS
    ]
    for title, accent, band in works:
        checks.append(
            ContrastCheck(
                f"Titel “{title}” op {'crème' if band == 'cream' else 'papier'}",
                colors[f"color-accent-{accent}"],
                colors[f"color-{band}"],
                ACCENT_MINIMUM,
            )
        )
    return checks


# Reading and writing -------------------------------------------------------


class StyleFiles:
    def __init__(self, site_root: Path):
        self.root = site_root
        self.tokens_path = site_root / "src" / "styles" / "tokens.css"
        self.fonts_path = site_root / "src" / "styles" / "fonts.ts"

    def read(self) -> dict[str, str]:
        css = self.tokens_path.read_text(encoding="utf-8")
        values = {}
        for name in [c[0] for c in COLORS] + [s.token for s in SCALES]:
            match = token_pattern(name).search(css)
            if match:
                values[name] = match.group(2).strip()
        values["font-heading"] = self._font_key(css, "font-heading", HEADING_FONTS)
        values["font-body"] = self._font_key(css, "font-body", BODY_FONTS)
        return values

    @staticmethod
    def _font_key(css: str, token: str, fonts: list[Font]) -> str:
        """The catalogue key of the font in use, or '' when it was set by hand."""
        match = token_pattern(token).search(css)
        first = re.match(r"\s*['\"]?([^,'\"]+)", match.group(2)) if match else None
        family = first.group(1) if first else ""
        return next((f.key for f in fonts if f.family == family), "")

    def write(self, values: dict[str, str]) -> None:
        css = self.tokens_path.read_text(encoding="utf-8")
        for name in [c[0] for c in COLORS] + [s.token for s in SCALES]:
            if name in values:
                css = token_pattern(name).sub(
                    lambda m: f"{m.group(1)}{values[name]}{m.group(3)}", css
                )
        fonts = {}
        for role, catalogue in (("heading", HEADING_FONTS), ("body", BODY_FONTS)):
            key = values.get(f"font-{role}", "")
            font = next((f for f in catalogue if f.key == key), None)
            if font:
                fonts[role] = font
                stack = f"'{font.family}', {FALLBACK[role]}"
                css = token_pattern(f"font-{role}").sub(
                    lambda m: f"{m.group(1)}{stack}{m.group(3)}", css
                )
        self.tokens_path.write_text(css, encoding="utf-8")
        if len(fonts) == 2:
            self.fonts_path.write_text(
                fonts_module(fonts["heading"], fonts["body"]), encoding="utf-8"
            )


def fonts_module(heading: Font, body: Font) -> str:
    def file(font: Font) -> str:
        return f"@fontsource/{font.key}/files/{font.key}-latin-400-normal.woff2?url"

    return f"""// Fonts loaded by the site, latin subsets only. The site manager (Stijl)
// rewrites this file from its font list; by hand, change these imports and the
// --font-* values in tokens.css together.
import '@fontsource/{heading.key}/latin-400.css';
import '@fontsource/{body.key}/latin-400.css';
import '@fontsource/{body.key}/latin-400-italic.css';
import '@fontsource/{body.key}/latin-700.css';
import headingFont from '{file(heading)}';
import bodyFont from '{file(body)}';

export const preloadFonts = [headingFont, bodyFont];
"""


def parse_form(form: dict, current: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Turn submitted values into token values; return them with any errors."""
    values, errors = {}, []
    for name, label in COLORS:
        color = str(form.get(name, "")).strip().lower()
        if HEX.match(color):
            values[name] = color
        else:
            errors.append(f"{label}: gebruik een kleurcode zoals #1a1a14.")
    for scale in SCALES:
        try:
            number = float(str(form.get(scale.token, "")).replace(",", "."))
        except ValueError:
            errors.append(f"{scale.label}: geen geldig getal.")
            continue
        if not scale.minimum <= number <= scale.maximum:
            errors.append(
                f"{scale.label}: kies een waarde tussen {scale.minimum} en {scale.maximum}."
            )
            continue
        values[scale.token] = f"{number:g}{scale.unit}"
    for role, catalogue in (("heading", HEADING_FONTS), ("body", BODY_FONTS)):
        key = str(form.get(f"font-{role}", ""))
        if key and key not in {f.key for f in catalogue}:
            errors.append("Onbekend lettertype.")
        values[f"font-{role}"] = key or current.get(f"font-{role}", "")
    fonts_changed = any(
        values[f"font-{r}"] != current.get(f"font-{r}", "") for r in ("heading", "body")
    )
    if fonts_changed and not (values["font-heading"] and values["font-body"]):
        errors.append("Kies zowel een lettertype voor de koppen als voor de tekst.")
    return values, errors


def scale_number(value: str) -> float:
    return float(re.sub(r"[^0-9.]", "", value) or 0)


def font_file(site_root: Path, key: str) -> Path | None:
    """The woff2 file of a catalogue font, for showing samples in the manager."""
    if key not in {f.key for f in HEADING_FONTS + BODY_FONTS}:
        return None
    path = (
        site_root / "node_modules" / "@fontsource" / key / "files" / f"{key}-latin-400-normal.woff2"
    )
    return path if path.is_file() else None
