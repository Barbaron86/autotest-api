import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[2]
HELPER = PROJECT / "tools" / "ai_review" / "prepare_config.py"


def prepare(policy: Path, repo: Path, output: Path, *, enabled: bool = True, dry_run: bool = True):
    result = subprocess.run(
        [sys.executable, str(HELPER), "--policy-root", str(policy), "--repository-root", str(repo),
         "--output", str(output), "--agent-mode", "on" if enabled else "off",
         "--dry-run", "true" if dry_run else "false"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(output.read_text(encoding="utf-8")), json.loads(
        output.with_suffix(".access.json").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(("enabled", "dry_run"), [(True, True), (False, False)])
def test_selected_flags_replace_yaml_values_and_tokens_stay_out(policy_root, repository, tmp_path, enabled, dry_run):
    output = tmp_path / "runtime" / "review.yaml"
    config, _ = prepare(policy_root, repository, output, enabled=enabled, dry_run=dry_run)
    assert config["agent"]["enabled"] is enabled
    assert config["review"]["dry_run"] is dry_run
    assert "repository_profile" not in config
    assert "MUST_NOT_BE_WRITTEN" not in output.read_text(encoding="utf-8")
    assert "api_token" not in config["llm"]["http_client"]
    domain = Path(config["prompt"]["summary_prompt_files"][0])
    assert domain == policy_root / ".github" / "ai-review" / "domain.md"
    assert all(Path(name).is_file() for name in config["prompt"]["system_agent_prompt_files"])


def test_search_reaches_unchanged_files_and_new_directories_without_secret_blobs(policy_root, repository, tmp_path):
    config, access = prepare(policy_root, repository, tmp_path / "review.yaml")
    allowed = lambda command: any(re.fullmatch(pattern, command) for pattern in config["agent"]["allow_commands"])
    command = access["search_template"].replace("<SYMBOL>", "CrossFolder")
    assert allowed(command)
    result = subprocess.run(shlex.split(command), cwd=repository, capture_output=True, text=True, check=True)
    assert "clients/client.py" in result.stdout
    assert "new_component/helper.py" in result.stdout
    assert "tests/test_client.py" in result.stdout
    assert "DO_NOT_DISCLOSE" not in result.stdout
    files = subprocess.run(shlex.split(access["list_command"]), cwd=repository,
                           capture_output=True, text=True, check=True).stdout.splitlines()
    assert set(files) == {"README.md", "clients/client.py", "tests/test_client.py", "new_component/helper.py"}
    read = f"git show {access['head_sha']}:clients/client.py"
    assert allowed(read)
    assert "def create(self, request)" in subprocess.run(
        shlex.split(read), cwd=repository, capture_output=True, text=True, check=True,
    ).stdout


@pytest.mark.parametrize("command", [
    "cat .env", "grep CrossFolder /proc/self/environ", "python -c print(1)", "pytest",
    "git status", "git show HEAD:clients/client.py", "git show HEAD:.env",
    "git grep --no-index CrossFolder .", "git grep --untracked CrossFolder",
    "git grep -Ocat CrossFolder", "git grep --textconv CrossFolder",
])
def test_unapproved_commands_are_blocked(policy_root, repository, tmp_path, command):
    config, access = prepare(policy_root, repository, tmp_path / "review.yaml")
    assert not any(re.fullmatch(pattern, command) for pattern in config["agent"]["allow_commands"])
    for path in ("credentials.yaml", "clients/link.py", "../.env", ".git/config", "odd$(command).py"):
        assert not any(re.fullmatch(pattern, f"git show {access['head_sha']}:{path}")
                       for pattern in config["agent"]["allow_commands"])
    valid = access["search_template"].replace("<SYMBOL>", "CrossFolder")
    assert not any(re.fullmatch(pattern, valid + " --textconv") for pattern in config["agent"]["allow_commands"])


def test_runtime_loads_in_upstream_and_preserves_protocol(policy_root, repository, tmp_path, monkeypatch):
    config, _ = prepare(policy_root, repository, tmp_path / "review.yaml")
    from ai_review.config import Settings, settings
    from ai_review.services.prompt.service import PromptService

    loaded = Settings(**config)
    monkeypatch.setattr(settings, "prompt", loaded.prompt)
    assert loaded.llm.meta.is_v2_model
    assert loaded.agent.enabled
    assert "TOOL_CALL" in PromptService.build_system_agent_request()
    prompt = PromptService.build_agent_request([], False, "Review this diff", "Return summary")
    assert "Review this diff" in prompt
    assert "Return summary" in prompt
