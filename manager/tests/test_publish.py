"""Publishing against a temporary git repository with a local 'GitHub' remote."""

import shutil
import subprocess
from pathlib import Path

import pytest

from sitemanager.publish import Publisher, default_message, is_content_path

SITE_ROOT = Path(__file__).resolve().parents[2]


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def configure(repo: Path) -> None:
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")


@pytest.fixture()
def repos(tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", "--initial-branch=main", str(remote))
    site = tmp_path / "site"
    site.mkdir()
    git(site, "init", "--initial-branch=main")
    configure(site)
    shutil.copytree(SITE_ROOT / "src/content", site / "src/content")
    shutil.copytree(SITE_ROOT / "src/data", site / "src/data")
    (site / "src/components").mkdir(parents=True)
    (site / "src/components/Code.astro").write_text("<p>code</p>\n")
    git(site, "add", "-A")
    git(site, "commit", "-m", "start")
    git(site, "remote", "add", "origin", str(remote))
    git(site, "push", "-u", "origin", "main")
    return site, remote


def remote_files(remote: Path, *paths: str) -> str:
    return git(remote, "show", "--stat", "--format=%s", "main", "--", *paths)


def test_publish_commits_only_content_and_pushes(repos):
    site, remote = repos
    work = site / "src/content/topics/nl/voor-ik-sluit.md"
    work.write_text(work.read_text().replace("Voor ik sluit", "Voor ik sluit (nieuw)"))
    code = site / "src/components/Code.astro"
    code.write_text("<p>half af</p>\n")

    result = Publisher(site, run_checks=False).publish("")

    assert result.ok, result.steps
    log = git(remote, "log", "-1", "--name-only", "--format=%s", "main")
    assert "Inhoud bijgewerkt via sitebeheer: topics/nl/voor-ik-sluit" in log
    assert "src/content/topics/nl/voor-ik-sluit.md" in log
    assert "Code.astro" not in log
    assert code.read_text() == "<p>half af</p>\n"  # uncommitted code is left alone


def test_publish_takes_in_changes_pushed_from_elsewhere(repos, tmp_path):
    site, remote = repos
    other = tmp_path / "other"
    git(tmp_path, "clone", str(remote), str(other))
    configure(other)
    (other / "src/components/Code.astro").write_text("<p>nieuwe code</p>\n")
    git(other, "commit", "-am", "code from elsewhere")
    git(other, "push")

    (site / "src/data/site.json").write_text('{"email": "nieuw@example.com"}\n')
    result = Publisher(site, run_checks=False).publish("Nieuw adres")

    assert result.ok, result.steps
    subjects = git(remote, "log", "--format=%s", "main").splitlines()
    assert subjects[:2] == ["Nieuw adres", "code from elsewhere"]


def test_failed_push_is_retried_on_the_next_publish(repos):
    site, remote = repos
    publisher = Publisher(site, run_checks=False)
    (site / "src/data/site.json").write_text('{"email": "a@example.com"}\n')
    git(site, "remote", "set-url", "origin", str(remote) + "-missing")

    assert not publisher.publish("").ok
    assert publisher.unpushed() == 1  # committed here, not on GitHub yet

    git(site, "remote", "set-url", "origin", str(remote))
    result = publisher.publish("")
    assert result.ok, result.steps
    assert publisher.unpushed() == 0


def test_nothing_to_publish(repos):
    site, _ = repos
    result = Publisher(site, run_checks=False).publish("")
    assert not result.ok
    assert result.steps[0].output == "Er is niets te publiceren."


def test_discard_restores_and_removes_only_content(repos):
    site, _ = repos
    publisher = Publisher(site, run_checks=False)
    page = site / "src/content/sections/nl/contact.md"
    original = page.read_text()
    page.write_text("kapot\n")
    new_image = site / "src/assets/images/works/nieuw.jpg"
    new_image.parent.mkdir(parents=True)
    new_image.write_bytes(b"x")

    publisher.discard("src/content/sections/nl/contact.md")
    publisher.discard("src/assets/images/works/nieuw.jpg")

    assert page.read_text() == original
    assert not new_image.exists()
    (site / "src/components/Code.astro").write_text("<p>gewijzigd</p>\n")
    with pytest.raises(ValueError):
        publisher.discard("src/components/Code.astro")


def test_helpers():
    assert is_content_path("src/content/topics/nl/a.md")
    assert not is_content_path("src/content/../components/x.astro")
    assert not is_content_path("astro.config.mjs")
    message = default_message([f"src/content/topics/nl/w{i}.md" for i in range(7)])
    assert message.endswith("en 2 meer")


def test_failed_check_stops_before_anything_is_committed(repos, monkeypatch):
    import sitemanager.publish as publish

    site, remote = repos
    monkeypatch.setattr(publish, "CHECK_COMMANDS", (("Site bouwen", ["false"]),))
    (site / "src/data/site.json").write_text('{"email": "b@example.com"}\n')
    before = git(remote, "rev-parse", "main")

    result = Publisher(site, run_checks=True).publish("")

    assert not result.ok
    assert [step.name for step in result.steps] == ["Site bouwen"]
    assert git(remote, "rev-parse", "main") == before
    assert git(site, "status", "--porcelain") != ""  # the change is still waiting
