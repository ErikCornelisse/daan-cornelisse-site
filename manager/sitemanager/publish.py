"""Publishing: check the site, commit the content changes, and push them to
GitHub, where the existing workflow deploys GitHub Pages.

Only the folders the manager edits (site_tools.CONTENT_PATHS) are ever
committed or reverted; code changes in the repository are left alone.
"""

import json
import re
import shutil
import threading
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .site_tools import CONTENT_PATHS, _run, pending_changes

CHECK_COMMANDS = (
    ("Controle van de inhoud", ["npm", "run", "check"]),
    ("Site bouwen", ["npm", "run", "build"]),
)


@dataclass
class Step:
    name: str
    ok: bool
    output: str = ""


@dataclass
class PublishResult:
    ok: bool
    steps: list[Step] = field(default_factory=list)
    commit: str = ""


def is_content_path(path: str) -> bool:
    return any(path == p or path.startswith(f"{p}/") for p in CONTENT_PATHS) and ".." not in path


def default_message(paths: list[str]) -> str:
    """'Inhoud bijgewerkt: works/nl/tijd-voor-max, data/site' and similar."""
    names = []
    for path in paths:
        name = re.sub(r"^src/(content/)?", "", path)
        name = re.sub(r"\.(md|json)$", "", name)
        if name not in names:
            names.append(name)
    shown = ", ".join(names[:5]) + (f" en {len(names) - 5} meer" if len(names) > 5 else "")
    return f"Inhoud bijgewerkt via sitebeheer: {shown}"


class Publisher:
    def __init__(self, site_root: Path, author: str = "", run_checks: bool = True):
        self.site_root = site_root
        self.author = author  # "Name <email>"; empty = the machine's git identity
        self.run_checks = run_checks
        self._lock = threading.Lock()

    def _git(self, *args: str, timeout: int = 120):
        return _run(["git", *args], self.site_root, timeout)

    def discard(self, path: str) -> str:
        """Undo the unpublished change to one content file."""
        if not is_content_path(path):
            raise ValueError("Alleen inhoud kan worden teruggedraaid.")
        if not any(change.path == path for change in pending_changes(self.site_root)):
            raise ValueError("Dit bestand heeft geen openstaande wijziging.")
        tracked = self._git("ls-files", "--error-unmatch", "--", path).returncode == 0
        if tracked:
            self._git("restore", "--source=HEAD", "--staged", "--worktree", "--", path)
        else:
            target = (self.site_root / path).resolve()
            if target.is_relative_to(self.site_root) and target.is_file():
                target.unlink()
        return f"Wijziging in {path} teruggedraaid."

    def check(self) -> list[Step]:
        steps = []
        for name, command in CHECK_COMMANDS:
            if shutil.which(command[0]) is None:
                missing = f"{command[0]} is niet gevonden op deze computer."
                return [*steps, Step(name, False, missing)]
            result = _run(command, self.site_root, timeout=600)
            steps.append(Step(name, result.returncode == 0, _tail(result.stdout + result.stderr)))
            if result.returncode != 0:
                break
        return steps

    def publish(self, message: str) -> PublishResult:
        if not self._lock.acquire(blocking=False):
            return PublishResult(False, [Step("Publiceren", False, "Er wordt al gepubliceerd.")])
        try:
            return self._publish(message.strip())
        finally:
            self._lock.release()

    def unpushed(self) -> int:
        """Commits made here that have not reached GitHub yet (for example after a failed push)."""
        count = self._git("rev-list", "--count", "@{upstream}..HEAD").stdout.strip()
        return int(count) if count.isdigit() else 0

    def _publish(self, message: str) -> PublishResult:
        changes = pending_changes(self.site_root)
        if not changes and not self.unpushed():
            return PublishResult(False, [Step("Wijzigingen", False, "Er is niets te publiceren.")])
        result = PublishResult(False)

        if self.run_checks:
            result.steps += self.check()
            if not all(step.ok for step in result.steps):
                return result

        if changes:
            # Stage exactly the changed content files (a pathspec for a folder that does not
            # exist would make `git add` fail as a whole).
            add = self._git("add", "--all", "--", *[c.path for c in changes])
            if add.returncode != 0:
                result.steps.append(Step("Vastleggen", False, _out(add)))
                return result
            commit_args = ["commit", "-m", message or default_message([c.path for c in changes])]
            if self.author:
                commit_args.append(f"--author={self.author}")
            commit = self._git(*commit_args)
            result.steps.append(Step("Vastleggen", commit.returncode == 0, _out(commit)))
            if commit.returncode != 0:
                self._git("reset", "--quiet", "--", *[c.path for c in changes])
                return result

        # Bring in anything pushed from elsewhere (for example code changes) before pushing.
        pull = self._git("pull", "--rebase", "--autostash")
        result.steps.append(Step("Bijwerken vanaf GitHub", pull.returncode == 0, _out(pull)))
        if pull.returncode != 0:
            self._git("rebase", "--abort")
            return result

        push = self._git("push")
        result.steps.append(Step("Versturen naar GitHub", push.returncode == 0, _out(push)))
        result.ok = push.returncode == 0
        result.commit = self._git("rev-parse", "--short", "HEAD").stdout.strip()
        return result

    def github_repo(self) -> str | None:
        """'owner/name' of the origin remote on GitHub, if it is one."""
        url = self._git("remote", "get-url", "origin").stdout.strip()
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(\.git)?$", url)
        return f"{match.group(1)}/{match.group(2)}" if match else None


def latest_deploy(repo: str) -> dict | None:
    """The most recent GitHub Actions run, from the public API (no login needed)."""
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            runs = json.load(response).get("workflow_runs", [])
    except (OSError, ValueError):
        return None
    if not runs:
        return None
    run = runs[0]
    return {
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "title": run.get("display_title"),
        "sha": (run.get("head_sha") or "")[:7],
        "url": run.get("html_url"),
        "updated": run.get("updated_at"),
    }


def pages_url(repo: str) -> str:
    owner, name = repo.split("/")
    return f"https://{owner.lower()}.github.io/{name}/"


def _out(result) -> str:
    return _tail(result.stdout + result.stderr)


def _tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])
