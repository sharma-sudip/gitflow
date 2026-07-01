#!/usr/bin/env python3
"""Interactive git workflow: branch → stage → commit → push."""

import subprocess
import sys
import pydevd_pycharm
# uncomment for debugging
# pydevd_pycharm.settrace(
#     "localhost",
#     port=8062,
#     stdout_to_server=True,
#     stderr_to_server=True,
#     suspend=False,
# )
try:
    import questionary
except ImportError:
    print("Missing dependency: run  pip install questionary")
    sys.exit(1)

BRANCH_TYPES = ["feature", "bugfix", "fix", "hotfix", "chore", "docs", "refactor"]


def run(cmd: list[str], check=True, capture=False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, check=check, capture_output=capture, text=True, encoding="utf-8-sig"
    )


def git(*args, capture=False, check=True):
    return run(["git", *args], capture=capture, check=check)


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", capture=True).stdout.strip()


def default_branch() -> str:
    """Try to detect the default branch (main/master)."""
    for candidate in ("main", "master"):
        result = git("show-ref", "--verify", f"refs/remotes/origin/{candidate}",
                     capture=True, check=False)
        if result.returncode == 0:
            return candidate
    return "main"


def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# ── Branch creation ────────────────────────────────────────────────────────────

def create_branch():
    branch_type = questionary.select(
        "Branch type:",
        choices=BRANCH_TYPES,
    ).ask()
    if branch_type is None:
        sys.exit(0)

    if branch_type == "bugfix":
        ticket = questionary.text("Ticket / issue number (leave blank to skip):").ask()
        if ticket is None:
            sys.exit(0)
        ticket = ticket.strip()
    else:
        ticket = ""

    name = questionary.text("Branch name / short description:").ask()
    if not name:
        print("Aborted — no name given.")
        sys.exit(1)

    slug = slugify(name)
    if ticket:
        branch_name = f"{branch_type}/{ticket}-{slug}"
    else:
        branch_name = f"{branch_type}/{slug}"

    base = default_branch()
    print(f"\nFetching latest {base}…")
    git("fetch", "origin", base)
    git("checkout", base)
    git("pull", "origin", base)

    git("checkout", "-b", branch_name)
    print(f"Created branch: {branch_name}\n")
    return branch_name


# ── Stage files ────────────────────────────────────────────────────────────────

def stage_files():
    import re
    _ansi = re.compile(r"\x1b\[[0-9;]*m")

    result = git("-c", "color.status=false", "status", "--short", "--porcelain", capture=True)
    raw_lines = result.stdout.strip().splitlines()
    lines = [_ansi.sub("", l) for l in raw_lines]
    if not lines:
        print("Nothing to stage — working tree is clean.")
        return False

    # Use 1-based integer values so no value is falsy (questionary treats 0 as
    # "no value set" and falls back to the title string on some Windows builds).
    paths = []
    choices = []
    for line in lines:
        status = line[:2]
        path = line[2:].strip()
        paths.append(path)
        choices.append(questionary.Choice(title=f"{status}  {path}", value=len(paths)))

    selected_indices = questionary.checkbox(
        "Select files to stage (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()

    if selected_indices is None:
        sys.exit(0)
    if not selected_indices:
        print("No files selected — nothing staged.")
        return False

    selected = [paths[i - 1] for i in selected_indices]
    git("add", "--", *selected)
    print(f"Staged {len(selected)} file(s).\n")
    return True


# ── Commit ─────────────────────────────────────────────────────────────────────

def make_commit():
    # Show a short diff summary so the user has context
    result = git("diff", "--cached", "--stat", capture=True)
    if result.stdout.strip():
        print(result.stdout)

    message = questionary.text("Commit message:").ask()
    if not message:
        print("Aborted — empty commit message.")
        sys.exit(1)

    git("commit", "-m", message)
    print()


# ── Push ───────────────────────────────────────────────────────────────────────

def push_branch(branch: str):
    confirmed = questionary.confirm(
        f"Push  {branch}  to origin?", default=True
    ).ask()
    if confirmed:
        git("push", "--set-upstream", "origin", branch)
        print(f"\nPushed {branch} to origin.")
    else:
        print("Push skipped.")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    try:
        # Check we're in a git repo
        git("rev-parse", "--git-dir", capture=True)
    except subprocess.CalledProcessError:
        print("Not inside a git repository.")
        sys.exit(1)

    mode = questionary.select(
        "What do you want to do?",
        choices=[
            questionary.Choice("New branch + stage + commit + push", value="full"),
            questionary.Choice("Stage + commit + push on current branch", value="quick"),
        ],
    ).ask()
    if mode is None:
        sys.exit(0)

    print()

    if mode == "full":
        branch = create_branch()
    else:
        branch = current_branch()
        print(f"Current branch: {branch}\n")

    staged = stage_files()
    if not staged:
        sys.exit(0)

    make_commit()
    push_branch(branch)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
