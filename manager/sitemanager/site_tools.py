"""Git status and the Astro preview server, run as subprocesses in the site."""

import json
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Folders the manager edits; git status is limited to these.
CONTENT_PATHS = ("src/content", "src/data", "src/assets", "src/styles")


@dataclass
class Change:
    status: str
    path: str


def _run(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def pending_changes(site_root: Path) -> list[Change]:
    result = _run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", *CONTENT_PATHS], site_root
    )
    return [Change(line[:2].strip(), line[3:]) for line in result.stdout.splitlines() if line]


def last_commit(site_root: Path) -> str:
    return _run(["git", "log", "-1", "--format=%h %s (%cr)"], site_root).stdout.strip()


class Preview:
    """The Astro dev server, managed through `astro dev --background`."""

    def __init__(self, site_root: Path, port: int, expose: bool):
        self.site_root = site_root
        self.port = port
        self.expose = expose  # listen on all interfaces, for Tailscale access

    def _astro(self, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
        return _run(["npx", "astro", "dev", *args], self.site_root, timeout)

    @property
    def host(self) -> str:
        """Address the preview listens on. Explicit, because Astro's default ("localhost")
        may bind to IPv6 only, and then a link to 127.0.0.1 cannot connect."""
        return "0.0.0.0" if self.expose else "127.0.0.1"

    def status(self) -> bool:
        """True when the preview answers on the address its links use (much faster than
        `astro dev status`)."""
        try:
            with socket.create_connection(("127.0.0.1", self.port), timeout=0.3):
                return True
        except OSError:
            return False

    def start(self) -> str:
        # Stop a preview that may have been started otherwise (for example on another address).
        self._astro("stop")
        args = ["--background", "--port", str(self.port), "--host", self.host]
        result = self._astro(*args, timeout=120)
        return _message(result) or "Voorbeeld gestart."

    def stop(self) -> str:
        return _message(self._astro("stop")) or "Voorbeeld gestopt."


def _message(result: subprocess.CompletedProcess) -> str:
    """Astro prints JSON log lines; return the last human-readable message."""
    for line in reversed((result.stdout + result.stderr).splitlines()):
        try:
            return json.loads(line)["message"].splitlines()[0]
        except (ValueError, KeyError, TypeError):
            continue
    return ""
