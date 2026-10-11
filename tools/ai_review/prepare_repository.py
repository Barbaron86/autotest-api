"""Save trusted policy and check out a validated same-repository PR head."""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

import yaml


def snapshot(source: Path, destination: Path) -> None:
    source = source.resolve()
    if destination.exists():
        raise ValueError("Policy destination already exists")
    config = yaml.safe_load((source / ".ai-review.yaml").read_text(encoding="utf-8"))
    names = [".ai-review.yaml", "tools/ai_review/prepare_config.py", "tools/ai_review/prepare_repository.py"]
    for key, paths in config.get("prompt", {}).items():
        if key.endswith("_files"):
            names.extend(paths)
    for name in set(names):
        original = (source / name).resolve()
        if not original.is_relative_to(source) or not original.is_file():
            raise ValueError(f"Missing trusted policy file: {name}")
        target = destination / original.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target)


def validate_pr(payload: dict[str, Any], repository: str, number: str) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid repository name")
    if not re.fullmatch(r"[1-9][0-9]*", number):
        raise ValueError("PR number must be a positive integer")
    if payload.get("number") != int(number) or payload.get("state") != "open":
        raise ValueError("Expected an open PR with the requested number")
    result: dict[str, Any] = {"repository": repository, "number": int(number)}
    for side in ("head", "base"):
        item = payload.get(side) or {}
        if (item.get("repo") or {}).get("full_name") != repository:
            raise ValueError("Only same-repository PRs are supported; forks are not permitted")
        sha = item.get("sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError(f"Invalid {side} commit SHA")
        result[f"{side}_sha"] = sha
    return result


def get_pr(repository: str, number: str, metadata: Path | None) -> dict[str, Any]:
    # Validate before constructing a URL or sending a credential.
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid repository name")
    if not re.fullmatch(r"[1-9][0-9]*", number):
        raise ValueError("PR number must be a positive integer")
    if metadata is not None:
        payload = json.loads(metadata.read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GH_TOKEN")
        if not token:
            raise ValueError("GH_TOKEN is required")
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repository}/pulls/{number}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    return validate_pr(payload, repository, number)


def git(root: Path, *args: str, authenticated: bool = False) -> str:
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    if authenticated:
        token = environment.get("GH_TOKEN")
        if not token:
            raise ValueError("GH_TOKEN is required for fetch")
        credential = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        environment.update(
            GIT_CONFIG_COUNT="1",
            GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
            GIT_CONFIG_VALUE_0=f"AUTHORIZATION: basic {credential}",
        )
    return subprocess.run(
        ["git", *args],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=120,
    ).stdout.strip()


def prepare(root: Path, identity: dict[str, Any], state: Path, *, skip_fetch: bool = False) -> None:
    if not skip_fetch:
        git(
            root,
            "fetch",
            "--no-tags",
            f"https://github.com/{identity['repository']}.git",
            identity["head_sha"],
            identity["base_sha"],
            authenticated=True,
        )
    for side in ("head_sha", "base_sha"):
        git(root, "cat-file", "-e", identity[side] + "^{commit}")
    git(root, "checkout", "--detach", identity["head_sha"])
    if git(root, "rev-parse", "HEAD") != identity["head_sha"]:
        raise ValueError("Checkout does not match the validated PR head")
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")


def check(root: Path, identity: dict[str, Any], state: Path) -> None:
    expected = json.loads(state.read_text(encoding="utf-8"))
    if identity != expected or git(root, "rev-parse", "HEAD") != expected["head_sha"]:
        raise ValueError("PR head/base changed; this review is stale. Start a fresh run.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    saved = subparsers.add_parser("snapshot")
    saved.add_argument("--source", type=Path, required=True)
    saved.add_argument("--destination", type=Path, required=True)
    for name in ("prepare", "check"):
        command = subparsers.add_parser(name)
        command.add_argument("--repository-root", type=Path, required=True)
        command.add_argument("--repository", required=True)
        command.add_argument("--number", required=True)
        command.add_argument("--state", type=Path, required=True)
        command.add_argument("--metadata", type=Path, help="Offline fixture; omit for GitHub API")
        if name == "prepare":
            command.add_argument("--skip-fetch", action="store_true", help="Offline commits already fetched")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            snapshot(args.source, args.destination)
        else:
            identity = get_pr(args.repository, args.number, args.metadata)
            if args.command == "prepare":
                prepare(args.repository_root, identity, args.state, skip_fetch=args.skip_fetch)
            else:
                check(args.repository_root, identity, args.state)
            print(f"Verified PR #{identity['number']}: head={identity['head_sha']} base={identity['base_sha']}")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Cannot prepare/check PR: {error}\n")


if __name__ == "__main__":
    main()
