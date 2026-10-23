"""Store uploaded images in the site, scaled down to a sensible maximum.
Astro makes the responsive sizes at build time; this only keeps the
originals in the repository reasonably small."""

import io
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIDE = 2400
FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def safe_stem(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^a-z0-9]+", "-", Path(ascii_name).stem.lower()).strip("-")
    return stem or "afbeelding"


def save_upload(data: bytes, filename: str, target_dir: Path) -> Path:
    """Save an uploaded image and return its path. Raises ValueError for non-images."""
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception as error:  # Pillow raises several types for bad input
        raise ValueError("Dit bestand is geen afbeelding die de site kan gebruiken.") from error
    if image.format not in FORMATS:
        raise ValueError("Gebruik een JPG-, PNG- of WebP-afbeelding.")

    image_format = image.format
    image = ImageOps.exif_transpose(image)  # respect the camera's orientation
    image.thumbnail((MAX_SIDE, MAX_SIDE))

    target_dir.mkdir(parents=True, exist_ok=True)
    stem, suffix = safe_stem(filename), FORMATS[image_format]
    path, counter = target_dir / f"{stem}{suffix}", 2
    while path.exists():
        path, counter = target_dir / f"{stem}-{counter}{suffix}", counter + 1

    if image_format == "JPEG":
        image.convert("RGB").save(path, "JPEG", quality=88, optimize=True)
    else:
        image.save(path, image_format)
    return path
