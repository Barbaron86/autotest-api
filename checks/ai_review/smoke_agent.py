"""Offline by default; --live permits one bounded model run, without GitHub writes."""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.ai_review.prepare_config import build_access, prepare_config  # noqa: E402
from tools.ai_review.prepare_repository import snapshot  # noqa: E402

MAX_REQUESTS = 5
MAX_OUTPUT_TOKENS = 3000
MAX_PROMPT_BYTES = 40000
CASE_FILE = "tests/files/test_agent_sample.py"
REFERENCE_FILE = "clients/files/files_client.py"


class BudgetExceeded(RuntimeError):
    pass


class BudgetTransport(httpx.AsyncBaseTransport):
    """Check before sending; no retries, redirects, other hosts or unbounded output."""

    def __init__(self, inner: httpx.AsyncBaseTransport) -> None:
        self.inner = inner
        self.requests = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if request.method != "POST" or str(request.url) != "https://api.openai.com/v1/responses":
            raise BudgetExceeded("Only the configured Responses endpoint is permitted")
        data = json.loads(request.content)
        limit = data.get("max_output_tokens")
        if not isinstance(limit, int) or not 1 <= limit <= MAX_OUTPUT_TOKENS:
            raise BudgetExceeded("Output token limit is missing or too large")
        prompt = "".join(message["content"] for message in data["input"]) + data.get("instructions", "")
        if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
            raise BudgetExceeded("Full prompt exceeds the UTF-8 byte budget")
        if self.requests >= MAX_REQUESTS:
            raise BudgetExceeded("Five requests already sent; refusing another")
        self.requests += 1
        return await self.inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self.inner.aclose()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True, timeout=30
    ).stdout


def prepare_case(policy_root: Path, source: Path, work: Path, pr_state: Path | None = None) -> dict[str, Any]:
    manifest = work / "fixture.json"
    if manifest.exists():
        fixture: dict[str, Any] = json.loads(manifest.read_text(encoding="utf-8"))
        return fixture
    if work.exists():
        raise ValueError("Use a new, empty work directory")
    saved = work / "policy"
    snapshot(policy_root, saved)
    config_path = saved / ".ai-review.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    # Keep the answer and test implementation outside the inspected Git snapshot.
    config.setdefault("repository_profile", {}).setdefault("exclude_paths", []).extend(
        ["checks/ai_review/*", "tools/ai_review/*", ".github/ai-review/*", "docs/*"]
    )
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    access = build_access(source, config["repository_profile"])
    if REFERENCE_FILE not in access["files"]:
        raise ValueError("This smoke fixture needs the FilesClient project; adapt it for another project")
    identity: dict[str, Any] = {}
    if pr_state:
        identity = json.loads(pr_state.read_text(encoding="utf-8"))
        if identity["head_sha"] != access["head_sha"] or not re.fullmatch(r"[0-9a-f]{40}", identity["base_sha"]):
            raise ValueError("PR checkout differs from the validated state")
        root = source
        base = identity["base_sha"]
        changed = git(root, "diff", "--name-only", base, access["head_sha"], "--").splitlines()
        if changed != [CASE_FILE] or CASE_FILE not in access["files"]:
            raise ValueError("Controlled PR must change only the small smoke test file")
    else:
        root = work / "repository"
        root.mkdir()
        for name in access["files"]:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(git(source, "show", f"{access['head_sha']}:{name}"), encoding="utf-8")
        git(root, "init", "-q", "-b", "feat/agent-smoke")
        git(root, "config", "user.name", "AI Review Smoke")
        git(root, "config", "user.email", "ai-review-smoke@example.invalid")
        case = root / CASE_FILE
        case.parent.mkdir(parents=True, exist_ok=True)
        case.write_text(
            "from clients.files.files_client import FilesClient\n"
            "from clients.files.files_schema import CreateFileRequestSchema\n\n\n"
            "def test_create_file(files_client: FilesClient) -> None:\n"
            "    request = CreateFileRequestSchema()\n"
            "    response = files_client.create_file_api(request=request)\n"
            "    assert response.status_code == 200\n",
            encoding="utf-8",
        )
        git(root, "add", ".")
        git(root, "commit", "-qm", "test: подготовить исходники и базовый тест")
        base = git(root, "rev-parse", "HEAD").strip()
        case.write_text(
            case.read_text(encoding="utf-8").replace("(request=request)", "(payload=request)"), encoding="utf-8"
        )
        git(root, "add", CASE_FILE)
        git(root, "commit", "-qm", "test: изменить вызов создания файла")
    runtime = prepare_config(saved, root, work / "runtime/review.yaml", agent_enabled=True, dry_run=True)
    runtime_config = yaml.safe_load(runtime.read_text(encoding="utf-8"))
    runtime_config["agent"]["max_iterations"] = 4
    runtime_config["llm"]["meta"]["reasoning"] = {"effort": "low"}
    runtime.write_text(yaml.safe_dump(runtime_config), encoding="utf-8")
    fixture = {
        "source_sha": access["head_sha"],
        "base_sha": base,
        "head_sha": git(root, "rev-parse", "HEAD").strip(),
        "repository": str(root),
        "runtime": str(runtime),
        "number": identity.get("number"),
        "expected": {
            "file": CASE_FILE,
            "reference": REFERENCE_FILE,
            "wrong_argument": "payload",
            "correct_argument": "request",
        },
    }
    manifest.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    return fixture


def configure(runtime: Path, *, live: bool) -> None:
    key = os.environ.get("OPENAI_API_KEY") if live else "offline-dummy"
    if not key:
        raise ValueError("OPENAI_API_KEY is required for --live")
    os.environ.update(
        AI_REVIEW_CONFIG_FILE_YAML=str(runtime),
        AI_REVIEW_CONFIG_FILE_JSON=str(runtime.parent / "absent.json"),
        AI_REVIEW_CONFIG_FILE_ENV=str(runtime.parent / "absent.env"),
        LLM__PROVIDER="OPENAI",
        LLM__HTTP_CLIENT__API_TOKEN=key,
        VCS__PROVIDER="GITHUB",
        VCS__HTTP_CLIENT__API_TOKEN="offline-unused",
        VCS__PIPELINE__OWNER="offline",
        VCS__PIPELINE__REPO="snapshot",
        VCS__PIPELINE__PULL_NUMBER="1",
    )


def build_prompts(fixture: dict[str, Any]) -> tuple[str, str]:
    from ai_review.services.diff.service import DiffService
    from ai_review.services.git.service import GitService
    from ai_review.services.prompt.schema import PromptContextSchema
    from ai_review.services.prompt.service import PromptService

    root = Path(fixture["repository"])
    rendered = DiffService().render_files(
        GitService(repo_dir=root), [CASE_FILE], fixture["base_sha"], fixture["head_sha"]
    )
    context = PromptContextSchema(review_title="File creation test update", changed_files=[CASE_FILE])
    system = PromptService.build_system_summary_request(context)
    system += (
        "\nFor this controlled smoke, no mypy results are available for the reviewed PR. "
        "Do not exclude defects only because a type checker could detect them. "
        "Other review rules still apply."
    )
    return (PromptService.build_summary_request(rendered, context), system)


class OfflineLLM:
    def __init__(self, access: dict[str, Any]) -> None:
        self.commands = [
            access["search_template"].replace("<SYMBOL>", "create_file_api"),
            f"git show {access['head_sha']}:{REFERENCE_FILE}",
        ]
        self.calls = 0

    async def chat(self, prompt: str, prompt_system: str) -> Any:
        from ai_review.services.llm.types import ChatResultSchema

        self.calls += 1
        if self.calls <= len(self.commands):
            text = json.dumps({"action": "TOOL_CALL", "command": self.commands[self.calls - 1]})
        else:
            if "def create_file_api(self, request:" not in prompt:
                raise AssertionError("Real tool output did not reach the next prompt")
            text = json.dumps(
                {
                    "action": "FINAL",
                    "content": f"В {CASE_FILE}:7 аргумент payload нужно заменить на request: "
                    f"метод create_file_api в {REFERENCE_FILE} принимает request, "
                    "иначе тест завершится с TypeError до HTTP-запроса.",
                },
                ensure_ascii=False,
            )
        return ChatResultSchema(text=text)


def successful_commands(traces: list[Any]) -> list[str]:
    return [
        str(trace.step.command)
        for trace in traces
        if trace.step and trace.step.command and trace.tool_output and "\nexit_code: 0\n" in trace.tool_output
    ]


async def run_loop(fixture: dict[str, Any], *, live: bool, report: dict[str, Any]) -> dict[str, Any]:
    from ai_review.clients.openai.v2.client import OpenAIV2HTTPClient
    from ai_review.config import settings
    from ai_review.services.agent.loop.service import AgentLoopService
    from ai_review.services.agent.tool.service import AgentToolService
    from ai_review.services.llm.openai.client import OpenAILLMClient
    from ai_review.services.policy.service import PolicyService
    from ai_review.services.prompt.service import PromptService

    class SmokeOpenAIClient(OpenAILLMClient):
        def __init__(self, client: httpx.AsyncClient) -> None:
            if not settings.llm.meta.is_v2_model:
                raise ValueError("Smoke requires the configured Responses API model")
            self.meta = settings.llm.meta
            self.http_client_v2 = OpenAIV2HTTPClient(client=client)

    access = json.loads(Path(fixture["runtime"]).with_suffix(".access.json").read_text(encoding="utf-8"))
    prompt, system = build_prompts(fixture)
    transport = BudgetTransport(httpx.AsyncHTTPTransport(retries=0))
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.openai.com/v1",
        timeout=180,
        follow_redirects=False,
        headers={"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"},
    ) as client:
        llm = SmokeOpenAIClient(client) if live else OfflineLLM(access)
        loop = AgentLoopService(
            llm=llm, prompt=PromptService(), agent_tool=AgentToolService(PolicyService(), Path(fixture["repository"]))
        )
        try:
            result = await loop.run(prompt, system)
        finally:
            report["http_requests"] = transport.requests
    commands = [trace.step.command for trace in result.traces if trace.step and trace.step.command]
    completed = successful_commands(result.traces)
    searched = any(command.startswith("git grep ") for command in completed)
    read = f"git show {fixture['head_sha']}:{REFERENCE_FILE}" in completed
    text = result.final_text
    final = json.loads(result.traces[-1].raw_output) if result.traces else {}
    found = all(word in text for word in ("payload", "request", "create_file_api", "test_agent_sample.py"))
    passed = (
        searched
        and read
        and found
        and bool(re.search(r"[А-Яа-я]", text))
        and final.get("action") == "FINAL"
        and not text.lstrip().startswith(("{", "[", "#", "```"))
    )
    report.update(
        passed=passed,
        searched=searched,
        read_related_file=read,
        final_text=text,
        commands=commands,
        successful_commands=completed,
        stop_reason=result.stop_reason,
        model_calls=len(result.traces),
        input_tokens=result.prompt_tokens if live else None,
        output_tokens=result.completion_tokens if live else None,
        # Uncached Standard estimate, not an invoice; source/date documented in rollout guide.
        estimated_usd=round((result.prompt_tokens * 2 + result.completion_tokens * 10) / 1_000_000, 6)
        if live
        else None,
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--source-repository", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pr-state", type=Path, help="Validated controlled PR state; inspect its actual checkout")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    report: dict[str, Any] = {"mode": "live" if args.live else "offline", "passed": False, "http_requests": 0}
    try:
        fixture = prepare_case(
            args.policy_root.resolve(), args.source_repository.resolve(), args.work_dir.resolve(), args.pr_state
        )
        configure(Path(fixture["runtime"]), live=args.live)
        from ai_review.services.prompt.service import PromptService

        prompt, system = build_prompts(fixture)
        first = (
            PromptService.build_agent_request([], False, prompt, system) + PromptService.build_system_agent_request()
        )
        size = len(first.encode("utf-8"))
        if size > MAX_PROMPT_BYTES:
            raise BudgetExceeded("Initial prompt exceeds the smoke budget")
        limits = {
            "max_http_requests": MAX_REQUESTS,
            "max_output_tokens_per_request": MAX_OUTPUT_TOKENS,
            "max_full_prompt_utf8_bytes": MAX_PROMPT_BYTES,
            "initial_prompt_utf8_bytes": size,
            "conservative_standard_cost_estimate_usd": 0.66,
        }
        print(json.dumps(limits, indent=2))
        if args.prepare_only:
            return
        if args.live:
            # Exclusive creation prevents accidentally repeating a paid attempt in this work directory.
            with (args.work_dir / "live-attempted").open("x", encoding="utf-8") as marker:
                marker.write("A live attempt has started; do not automatically repeat it.\n")
        report.update(
            source_sha=fixture["source_sha"], head_sha=fixture["head_sha"], number=fixture["number"], limits=limits
        )
        report = asyncio.run(run_loop(fixture, live=args.live, report=report))
    except Exception as error:
        # No retry/fallback. Do not put HTTP headers, keys or raw exception payloads in reports.
        report["error"] = type(error).__name__
        print(f"Smoke stopped: {type(error).__name__}", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
