import subprocess
from pathlib import Path


def git(root: Path, *args: str, input_text: str | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    ).stdout.strip()
