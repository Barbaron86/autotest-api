import asyncio
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest


@pytest.mark.parametrize("raw_kind", ["plain", "embedded", "invalid_action"])
def test_smoke_preserves_final_answer_and_usage_without_requiring_raw_json(raw_kind):
    from ai_review.services.agent.loop.schema import (
        AgentAction,
        AgentLoopResultSchema,
        AgentStepSchema,
        AgentTraceSchema,
    )

    from checks.ai_review.smoke_agent import summarize_result

    head = "a" * 40
    answer = "В test_agent_sample.py вызов create_file_api использует payload вместо request."
    raw = (
        answer
        if raw_kind == "plain"
        else json.dumps({"action": "FINAL", "content": answer}, ensure_ascii=False) + "\nГотово."
    )
    if raw_kind == "invalid_action":
        raw = '{"action":"TOOL_CALL"} {"action":"FINAL"}'
        answer = raw
    traces = [
        AgentTraceSchema(
            iteration=index,
            step=AgentStepSchema(action=AgentAction.TOOL_CALL, command=command),
            raw_output="tool request",
            tool_output="command: example\nexit_code: 0\nstdout: source\nstderr: ",
            prompt_tokens=10,
            completion_tokens=2,
        )
        for index, command in enumerate(
            ("git grep -n -I -F -e create_file_api", f"git show {head}:clients/files/files_client.py"), 1
        )
    ]
    traces.append(
        AgentTraceSchema(
            iteration=3,
            step=AgentStepSchema(action=AgentAction.FINAL, content=answer),
            raw_output=raw,
            prompt_tokens=20,
            completion_tokens=5,
        )
    )
    result = AgentLoopResultSchema(traces=traces, final_text=answer, stop_reason="max_requests_or_context_limit")
    report = summarize_result(result, {"head_sha": head}, live=True, report={"http_requests": 3})
    assert report["passed"] is (raw_kind != "invalid_action")
    assert report["final_text"] == answer
    assert report["input_tokens"] == 40 and report["output_tokens"] == 9
    assert report["traces"][-1]["raw_output"] == raw
    assert len(report["successful_commands"]) == 2
    assert bool(report["failure_reasons"]) is (raw_kind == "invalid_action")


def test_blocked_failed_and_duplicate_commands_do_not_count_as_successful_exploration():
    from checks.ai_review.smoke_agent import successful_commands

    command = "git grep -n -I -F -e example"
    traces = [
        SimpleNamespace(step=SimpleNamespace(command=command), tool_output="Agent command blocked by policy"),
        SimpleNamespace(
            step=SimpleNamespace(command=command), tool_output="command: example\nexit_code: 1\nstdout: \nstderr: error"
        ),
        SimpleNamespace(step=SimpleNamespace(command=command), tool_output=None),
        SimpleNamespace(
            step=SimpleNamespace(command="git show example"),
            tool_output="command: example\nexit_code: 0\nstdout: real source\nstderr: ",
        ),
    ]
    assert successful_commands(traces) == ["git show example"]


def test_offline_smoke_searches_and_reads_real_project_sources(tmp_path):
    project = Path(__file__).resolve().parents[2]
    output = tmp_path / "result.json"
    result = subprocess.run(
        [
            sys.executable,
            str(project / "checks/ai_review/smoke_agent.py"),
            "--policy-root",
            str(project),
            "--source-repository",
            str(project),
            "--work-dir",
            str(tmp_path / "smoke"),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["mode"] == "offline"
    assert report["passed"] is True
    assert report["http_requests"] == 0
    assert report["searched"] is True
    assert report["read_related_file"] is True
    assert "payload" in report["final_text"] and "request" in report["final_text"]
    assert (project / "tests/files/test_files.py").read_text().find("create_file_api(payload=request)") == -1


@pytest.mark.parametrize("case", ["valid", "changed_head", "other_file"])
def test_pr_smoke_reads_actual_pr_head_without_creating_or_editing_a_diff(tmp_path, case):
    from checks.ai_review.support import git

    project = Path(__file__).resolve().parents[2]
    script = str(project / "checks/ai_review/smoke_agent.py")
    baseline_work = tmp_path / "baseline"
    first = subprocess.run(
        [
            sys.executable,
            script,
            "--prepare-only",
            "--policy-root",
            str(project),
            "--source-repository",
            str(project),
            "--work-dir",
            str(baseline_work),
            "--output",
            str(tmp_path / "baseline.json"),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert first.returncode == 0, first.stderr
    baseline = json.loads((baseline_work / "fixture.json").read_text())
    source = Path(baseline["repository"])
    if case == "other_file":
        (source / "unrelated.py").write_text("UNRELATED = True\n")
        git(source, "add", "unrelated.py")
        git(source, "commit", "-qm", "test: добавить посторонний файл")
        baseline["head_sha"] = git(source, "rev-parse", "HEAD")
    state = tmp_path / "pr-state.json"
    state.write_text(
        json.dumps(
            {
                "number": 12,
                "head_sha": "0" * 40 if case == "changed_head" else baseline["head_sha"],
                "base_sha": baseline["base_sha"],
            }
        )
    )
    before = (source / "tests/files/test_agent_sample.py").read_bytes()
    work = tmp_path / "pr-smoke"
    output = tmp_path / "result.json"
    result = subprocess.run(
        [
            sys.executable,
            script,
            "--policy-root",
            str(project),
            "--source-repository",
            str(source),
            "--work-dir",
            str(work),
            "--output",
            str(output),
            "--pr-state",
            str(state),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if case != "valid":
        assert result.returncode != 0
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["http_requests"] == 0 and report["passed"] is False
        assert (source / "tests/files/test_agent_sample.py").read_bytes() == before
        return
    assert result.returncode == 0, result.stderr
    fixture = json.loads((work / "fixture.json").read_text())
    assert fixture["repository"] == str(source.resolve())
    assert fixture["head_sha"] == baseline["head_sha"]
    assert fixture["number"] == 12
    assert (source / "tests/files/test_agent_sample.py").read_bytes() == before
    assert json.loads(output.read_text(encoding="utf-8"))["passed"] is True


def test_transport_blocks_sixth_request_before_network_and_does_not_retry_errors():
    from checks.ai_review.smoke_agent import BudgetExceeded, BudgetTransport

    attempts = []

    def respond(request):
        attempts.append(request)
        return httpx.Response(500, json={"error": "temporary"})

    async def run():
        transport = BudgetTransport(httpx.MockTransport(respond))
        async with httpx.AsyncClient(transport=transport) as client:
            body = {"input": [{"role": "user", "content": "Review"}], "max_output_tokens": 3000}
            for _ in range(5):
                response = await client.post("https://api.openai.com/v1/responses", json=body)
                assert response.status_code == 500
            with pytest.raises(BudgetExceeded):
                await client.post("https://api.openai.com/v1/responses", json=body)
        assert transport.requests == 5

    asyncio.run(run())
    assert len(attempts) == 5


@pytest.mark.parametrize("case", ["oversized", "output_limit", "other_host", "other_endpoint"])
def test_transport_rejects_unsafe_or_oversized_requests_without_sending(case):
    from checks.ai_review.smoke_agent import BudgetExceeded, BudgetTransport

    async def run():
        def unexpected(request):
            pytest.fail("Blocked request reached the network transport")

        transport = BudgetTransport(httpx.MockTransport(unexpected))
        body = {
            "input": [{"role": "user", "content": "ж" * 40000 if case == "oversized" else "Review"}],
            "max_output_tokens": 3001 if case == "output_limit" else 3000,
        }
        url = (
            "https://other.invalid/v1/responses"
            if case == "other_host"
            else (
                "https://api.openai.com/v1/chat/completions"
                if case == "other_endpoint"
                else "https://api.openai.com/v1/responses"
            )
        )
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(BudgetExceeded):
                await client.post(url, json=body)
        assert transport.requests == 0

    asyncio.run(run())
