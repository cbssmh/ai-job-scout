from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock

import pytest
from fastapi.testclient import TestClient

from app.services import recommend_service
from tests.provider_work_harness import (
    MAX_ANALYSIS_LIMIT,
    MAX_JOB_DESCRIPTION_CHARS,
    CountingAnalyzer,
    ProviderWorkHarness,
    build_provider_work_harness,
    valid_analysis,
)


@pytest.fixture
def harness(tmp_path):
    result = build_provider_work_harness(tmp_path / "provider-work.db")
    try:
        yield result
    finally:
        result.client.close()


def test_negative_limit_is_rejected_before_repository_or_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(3)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post("/analysis/run", params={"limit": -1})

    assert response.status_code == 422
    assert len(provider.calls) == 0
    assert harness.persisted_state()["analysis_count"] == 0


def test_zero_limit_is_rejected_before_repository_or_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(3)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post("/analysis/run", params={"limit": 0})

    assert response.status_code == 422
    assert len(provider.calls) == 0
    assert harness.persisted_state()["analysis_count"] == 0


def test_maximum_limit_causes_one_call_per_selected_job(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(MAX_ANALYSIS_LIMIT)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post(
        "/analysis/run",
        params={"limit": MAX_ANALYSIS_LIMIT},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert len(body["completed"]) == MAX_ANALYSIS_LIMIT
    assert all(
        row["analysis_outcome"] == "provider_success"
        for row in body["completed"]
    )
    assert body["degraded"] == []
    assert body["failed"] == []
    assert body["remaining_count"] == 0
    assert len(provider.calls) == MAX_ANALYSIS_LIMIT
    assert harness.persisted_state()["analysis_count"] == MAX_ANALYSIS_LIMIT


def test_above_maximum_is_rejected_before_repository_or_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    requested = MAX_ANALYSIS_LIMIT + 1
    harness.seed_jobs(requested)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post("/analysis/run", params={"limit": requested})

    assert response.status_code == 422
    assert len(provider.calls) == 0
    assert harness.persisted_state()["analysis_count"] == 0


def test_extremely_large_limit_returns_client_error_before_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(1)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post(
        "/analysis/run",
        params={"limit": 10**40},
    )

    assert response.status_code == 422
    assert len(provider.calls) == 0
    state = harness.persisted_state()
    assert state["analysis_count"] == 0
    assert state["last_analyzed"] == [False]


def test_non_integer_limit_is_rejected_by_input_validation(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(1)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post("/analysis/run", params={"limit": "many"})

    assert response.status_code == 422
    assert len(provider.calls) == 0
    assert harness.persisted_state()["analysis_count"] == 0


def test_oversized_job_text_is_rejected_before_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    oversized_description = "P" * (MAX_JOB_DESCRIPTION_CHARS + 1)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    create_response = harness.client.post(
        "/jobs/",
        json={
            "source": "phase-2a-test",
            "title": "Oversized Input Job",
            "company": "Example Corp",
            "location": "Remote",
            "url": "https://example.invalid/provider-boundary/oversized",
            "description_raw": oversized_description,
            "posted_at": None,
        },
    )
    assert create_response.status_code == 422
    assert len(provider.calls) == 0
    assert harness.persisted_state()["job_count"] == 0


def test_maximum_job_text_is_accepted_and_reaches_provider_boundary_unchanged(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    maximum_description = "P" * MAX_JOB_DESCRIPTION_CHARS
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    create_response = harness.client.post(
        "/jobs/",
        json={
            "source": "phase-2a-test",
            "title": "Maximum Input Job",
            "company": "Example Corp",
            "location": "Remote",
            "url": "https://example.invalid/provider-boundary/maximum",
            "description_raw": maximum_description,
            "posted_at": None,
        },
    )
    analysis_response = harness.client.post("/analysis/run", params={"limit": 1})

    assert create_response.status_code == 200
    assert analysis_response.status_code == 200
    assert analysis_response.json()["status"] == "completed"
    assert len(provider.calls) == 1
    assert provider.calls[0][0] == maximum_description
    assert harness.persisted_state()["analysis_count"] == 1


def test_job_request_body_over_64_kib_is_rejected(
    harness: ProviderWorkHarness,
):
    import json

    payload = {
        "source": "phase-2a-test",
        "title": "Multibyte Input Job",
        "company": "Example Corp",
        "location": "Remote",
        "url": "https://example.invalid/provider-boundary/body-size",
        "description_raw": "가" * MAX_JOB_DESCRIPTION_CHARS,
        "posted_at": None,
    }
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    assert len(encoded) > 64 * 1024

    response = harness.client.post(
        "/jobs/",
        content=encoded,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert harness.persisted_state()["job_count"] == 0


@pytest.mark.parametrize(
    ("field", "maximum", "value"),
    [
        ("source", 64, "S"),
        ("title", 256, "T"),
        ("company", 256, "C"),
        ("location", 256, "L"),
        ("url", 2048, "U"),
        ("posted_at", 64, "P"),
    ],
)
def test_structured_job_field_above_maximum_is_rejected(
    harness: ProviderWorkHarness,
    field: str,
    maximum: int,
    value: str,
):
    payload = {
        "source": "phase-2a-test",
        "title": "Boundary Job",
        "company": "Example Corp",
        "location": "Remote",
        "url": "https://example.invalid/provider-boundary/field-size",
        "description_raw": "Python role",
        "posted_at": None,
    }
    payload[field] = value * (maximum + 1)

    response = harness.client.post("/jobs/", json=payload)

    assert response.status_code == 422
    assert harness.persisted_state()["job_count"] == 0


def test_repeated_analysis_after_success_does_not_repeat_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(1)
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    first = harness.client.post("/analysis/run", params={"limit": 1})
    second = harness.client.post("/analysis/run", params={"limit": 1})

    assert first.status_code == 200
    assert len(first.json()["completed"]) == 1
    assert second.status_code == 200
    assert second.json()["selected_count"] == 0
    assert second.json()["completed"] == []
    assert len(provider.calls) == 1
    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True]


class ConcurrentBoundaryAnalyzer:
    def __init__(self) -> None:
        self.calls = 0
        self._lock = Lock()
        self.first_request_entered = Event()
        self.release = Event()

    def __call__(self, text: str, title: str = "") -> dict[str, str]:
        with self._lock:
            self.calls += 1
            self.first_request_entered.set()

        if not self.release.wait(timeout=5):
            raise TimeoutError("test did not release fake provider")
        return valid_analysis()


def test_competing_request_is_rejected_before_duplicate_provider_work(
    harness: ProviderWorkHarness,
    monkeypatch,
):
    harness.seed_jobs(1)
    provider = ConcurrentBoundaryAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    def invoke_analysis():
        with TestClient(harness.app, raise_server_exceptions=False) as client:
            return client.post("/analysis/run", params={"limit": 1})

    with ThreadPoolExecutor(max_workers=1) as executor:
        first_future = executor.submit(invoke_analysis)
        assert provider.first_request_entered.wait(timeout=3)
        assert provider.calls == 1
        assert not first_future.done()

        second = invoke_analysis()
        assert second.status_code == 409
        assert provider.calls == 1

        provider.release.set()
        first = first_future.result(timeout=5)

    assert first.status_code == 200
    assert first.json()["status"] == "completed"
    assert provider.calls == 1
    assert harness.persisted_state()["analysis_count"] == 1
