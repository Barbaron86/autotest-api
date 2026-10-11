"""Offline checks deliberately isolated from the API integration fixtures."""

import os
from pathlib import Path

import pytest
import yaml

from checks.ai_review.support import git

PROJECT = Path(__file__).resolve().parents[2]
for kind in ("YAML", "JSON", "ENV"):
    os.environ[f"AI_REVIEW_CONFIG_FILE_{kind}"] = str(PROJECT / "checks" / f"absent.{kind.lower()}")
os.environ.update(
    PYTHONUTF8="1",
    LLM__PROVIDER="OPENAI",
    LLM__META__MODEL="gpt-6-sol",
    LLM__HTTP_CLIENT__API_URL="https://api.openai.com/v1",
    VCS__PROVIDER="GITHUB",
    VCS__HTTP_CLIENT__API_URL="https://api.github.com",
    LLM__HTTP_CLIENT__API_TOKEN="offline-dummy",
    VCS__HTTP_CLIENT__API_TOKEN="offline-dummy",
    VCS__PIPELINE__OWNER="example",
    VCS__PIPELINE__REPO="repository",
    VCS__PIPELINE__PULL_NUMBER="1",
)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "-q", "-b", "feat/offline-check")
    git(root, "config", "user.name", "Offline Check")
    git(root, "config", "user.email", "offline@example.invalid")
    files = {
        "clients/client.py": "class CrossFolder:\n    def create(self, request):\n        return request\n",
        "tests/test_client.py": "from clients.client import CrossFolder\n",
        "new_component/helper.py": "REFERENCE = 'CrossFolder'\n",
        "credentials.yaml": "CrossFolder: DO_NOT_DISCLOSE\n",
        ".env.example": "CrossFolder=DO_NOT_DISCLOSE\n",
        "artifacts/result.py": "CrossFolder = 'DO_NOT_DISCLOSE'\n",
        "odd$(command).py": "CrossFolder = 'DO_NOT_DISCLOSE'\n",
        "README.md": "Example repository\n",
    }
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(root, "add", ".")
    blob = git(root, "hash-object", "-w", "--stdin", input_text="/etc/passwd")
    git(root, "update-index", "--add", "--cacheinfo", f"120000,{blob},clients/link.py")
    git(root, "commit", "-qm", "test: подготовить исходники фикстуры")
    return root


@pytest.fixture
def policy_root(tmp_path: Path) -> Path:
    root = tmp_path / "policy"
    (root / ".github" / "ai-review").mkdir(parents=True)
    for name in ("domain.md", "repository-exploration.md"):
        (root / ".github" / "ai-review" / name).write_text("Review carefully.\n", encoding="utf-8")
    config = {
        "llm": {
            "provider": "OPENAI",
            "meta": {"model": "gpt-6-sol"},
            "http_client": {"api_token": "MUST_NOT_BE_WRITTEN"},
        },
        "vcs": {"provider": "GITHUB", "http_client": {"api_token": "MUST_NOT_BE_WRITTEN"}},
        "agent": {"enabled": False},
        "review": {"dry_run": False},
        "prompt": {
            "summary_prompt_files": [".github/ai-review/domain.md"],
            "system_agent_prompt_files": [".github/ai-review/repository-exploration.md"],
            "include_agent_system_prompts": True,
        },
        "repository_profile": {"source_roots": ["."], "file_extensions": [".py", ".md", ".yaml"]},
    }
    (root / ".ai-review.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    return root
