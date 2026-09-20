from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.agents import job_analyst
from app.llm.client import LLMClientConfig
from tests.provider_work_harness import (
    ProviderWorkHarness,
    build_provider_work_harness,
)


VALID_PROVIDER_JSON = """{
  "role": "Backend Engineer",
  "tech_stack": "Python, FastAPI",
  "experience_level": "3+ years",
  "language_requirement": "English required",
  "visa_sponsorship": "unknown",
  "summary": "Valid fake provider result."
}"""


class FakeCompletions:
    def __init__(
        self,
        *,
        content: str | None = VALID_PROVIDER_JSON,
        error: Exception | None = None,
        entered: Event | None = None,
        release: Event | None = None,
    ) -> None:
        self.content = content
        self.error = error
        self.entered = entered
        self.release = release
        self.calls = 0
        self._lock = Lock()

    def create(self, **kwargs):
        with self._lock:
            self.calls += 1

        if self.entered is not None:
            self.entered.set()
        if self.release is not None and not self.release.wait(timeout=5):
            raise TimeoutError("test did not release delayed fake provider")
        if self.error is not None:
            raise self.error

        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


def fake_llm_config(completions: FakeCompletions) -> LLMClientConfig:
    return LLMClientConfig(
        provider="phase-2a-fake",
        model="deterministic-fake-model",
        client=SimpleNamespace(
            chat=SimpleNamespace(completions=completions),
        ),
    )


@pytest.fixture
def harness(tmp_path):
    result = build_provider_work_harness(tmp_path / "provider-failure.db")
    result.seed_jobs(1, description="Python FastAPI backend role")
    try:
        yield result
    finally:
        result.client.close()


def test_delayed_provider_keeps_request_open_then_persists_success(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    entered = Event()
    release = Event()
    completions = FakeCompletions(entered=entered, release=release)
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: fake_llm_config(completions),
    )

    def invoke_analysis():
        with TestClient(harness.app, raise_server_exceptions=False) as client:
            return client.post("/analysis/run", params={"limit": 1})

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(invoke_analysis)
        assert entered.wait(timeout=3)
        assert completions.calls == 1
        assert not future.done()
        assert harness.persisted_state()["analysis_count"] == 0
        release.set()
        response = future.result(timeout=5)

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True]


def test_provider_exception_is_degraded_and_remains_retryable(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    completions = FakeCompletions(error=RuntimeError("fake provider unavailable"))
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: fake_llm_config(completions),
    )

    first = harness.client.post("/analysis/run", params={"limit": 1})
    second = harness.client.post("/analysis/run", params={"limit": 1})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "degraded"
    assert first.json()["completed"] == []
    assert len(first.json()["degraded"]) == 1
    assert first.json()["degraded"][0]["analysis_outcome"] == "degraded_fallback"
    assert first.json()["remaining_count"] == 1
    assert second.json()["status"] == "degraded"
    assert completions.calls == 2
    persisted_response = harness.client.get("/analysis/")
    assert persisted_response.status_code == 200
    assert persisted_response.json()[0]["analysis_outcome"] == "degraded_fallback"
    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True]
    assert "LLM fallback reason: RuntimeError" in state["summaries"][0]


def test_malformed_json_is_degraded_and_remains_pending_for_retry(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    completions = FakeCompletions(content="not valid json")
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: fake_llm_config(completions),
    )

    response = harness.client.post("/analysis/run", params={"limit": 1})

    assert response.status_code == 200
    assert completions.calls == 1
    assert response.json()["status"] == "degraded"
    assert response.json()["remaining_count"] == 1
    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True]
    assert "LLM fallback reason: JSONDecodeError" in state["summaries"][0]


def test_structurally_incomplete_output_is_degraded_fallback(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    completions = FakeCompletions(content='{"role": "Backend Engineer"}')
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: fake_llm_config(completions),
    )

    response = harness.client.post("/analysis/run", params={"limit": 1})

    assert response.status_code == 200
    assert completions.calls == 1
    batch = response.json()
    assert batch["status"] == "degraded"
    assert batch["completed"] == []
    assert len(batch["degraded"]) == 1
    body = batch["degraded"][0]
    assert body["analysis_outcome"] == "degraded_fallback"
    assert "Rule-based fallback" in body["summary"]
    assert "LLM fallback reason: ValueError" in body["summary"]
    assert harness.persisted_state()["analysis_count"] == 1


def test_client_construction_failure_is_structured_and_remains_retryable(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    def fail_client_construction():
        raise ValueError("fake missing provider configuration")

    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        fail_client_construction,
    )

    failed = harness.client.post("/analysis/run", params={"limit": 1})

    assert failed.status_code == 200
    failed_body = failed.json()
    assert failed_body["status"] == "failed"
    assert failed_body["completed"] == []
    assert failed_body["degraded"] == []
    assert len(failed_body["failed"]) == 1
    assert failed_body["failed"][0]["error_type"] == "ValueError"
    assert failed_body["remaining_count"] == 1
    state_after_failure = harness.persisted_state()
    assert state_after_failure["analysis_count"] == 0
    assert state_after_failure["statuses"] == ["ACTIVE"]
    assert state_after_failure["last_analyzed"] == [False]

    completions = FakeCompletions()
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: fake_llm_config(completions),
    )
    retried = harness.client.post("/analysis/run", params={"limit": 1})

    assert retried.status_code == 200
    assert retried.json()["status"] == "completed"
    assert completions.calls == 1
    state_after_retry = harness.persisted_state()
    assert state_after_retry["analysis_count"] == 1
    assert state_after_retry["last_analyzed"] == [True]


def test_failure_after_success_returns_partial_progress_and_remaining_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(
        2,
        description="Python FastAPI backend role",
        url_prefix="https://example.invalid/provider-failure/extra",
    )
    completions = FakeCompletions()
    construction_calls = 0

    def first_client_then_fail():
        nonlocal construction_calls
        construction_calls += 1
        if construction_calls == 1:
            return fake_llm_config(completions)
        raise ValueError("fake configuration failure after earlier success")

    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        first_client_then_fail,
    )

    response = harness.client.post("/analysis/run", params={"limit": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "partial"
    assert body["selected_count"] == 3
    assert len(body["completed"]) == 1
    assert body["degraded"] == []
    assert len(body["failed"]) == 1
    assert body["failed"][0]["error_type"] == "ValueError"
    assert body["remaining_count"] == 2
    assert completions.calls == 1

    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True, False, False]
