"""Settings from manager/.env (see .env.example)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

MANAGER_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    site_root: Path
    host: str
    port: int
    preview_port: int
    publish_author: str

    @property
    def is_local_only(self) -> bool:
        return self.host in ("127.0.0.1", "localhost", "::1")


def load_settings() -> Settings:
    load_dotenv(MANAGER_DIR / ".env")
    root = Path(os.getenv("SITE_ROOT", ".."))
    if not root.is_absolute():
        root = (MANAGER_DIR / root).resolve()
    if not (root / "astro.config.mjs").exists():
        raise RuntimeError(f"SITE_ROOT does not point to the Astro site: {root}")
    return Settings(
        site_root=root,
        host=os.getenv("MANAGER_HOST", "127.0.0.1"),
        port=int(os.getenv("MANAGER_PORT", "8765")),
        preview_port=int(os.getenv("PREVIEW_PORT", "4321")),
        publish_author=os.getenv("PUBLISH_AUTHOR", "").strip(),
    )
