from unittest.mock import Mock

from app.agents import job_analyst
from app.api import routes_recommend
from app.db.database import get_db
from app.services import recommend_service
from tests.provider_work_harness import (
    CountingAnalyzer,
    build_provider_work_harness,
)


def test_disabled_analysis_fails_closed_before_provider_or_repository_work(
    tmp_path,
    monkeypatch,
):
    harness = build_provider_work_harness(
        tmp_path / "provider-disabled.db",
        provider_analysis_enabled=False,
    )
    harness.seed_jobs(1, description="Synthetic Python backend role")
    provider = CountingAnalyzer()
    client_constructor = Mock(side_effect=AssertionError("client constructed"))
    analysis_service = Mock(side_effect=AssertionError("repository work started"))
    database_dependency = Mock(side_effect=AssertionError("database dependency entered"))
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)
    monkeypatch.setattr(job_analyst, "get_llm_client_config", client_constructor)
    monkeypatch.setattr(routes_recommend, "analyze_all_jobs", analysis_service)
    harness.app.dependency_overrides[get_db] = database_dependency

    before = harness.persisted_state()
    response = harness.client.post("/analysis/run", params={"limit": 1})
    after = harness.persisted_state()

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "provider_analysis_unavailable",
            "message": "Provider-backed analysis is currently unavailable.",
        }
    }
    assert client_constructor.call_count == 0
    assert analysis_service.call_count == 0
    assert database_dependency.call_count == 0
    assert len(provider.calls) == 0
    assert before == after
    assert after["analysis_count"] == 0
    assert after["statuses"] == ["ACTIVE"]
    assert after["last_analyzed"] == [False]
    harness.client.close()


def test_disabled_analysis_leaves_read_only_routes_available(tmp_path):
    harness = build_provider_work_harness(
        tmp_path / "provider-disabled-read-only.db",
        provider_analysis_enabled=False,
    )
    harness.seed_jobs(1, description="Synthetic platform role")

    jobs_response = harness.client.get("/jobs/")
    analysis_response = harness.client.get("/analysis/")

    assert jobs_response.status_code == 200
    assert len(jobs_response.json()) == 1
    assert analysis_response.status_code == 200
    assert analysis_response.json() == []
    harness.client.close()


def test_enabled_analysis_preserves_existing_provider_work_behavior(
    tmp_path,
    monkeypatch,
):
    harness = build_provider_work_harness(
        tmp_path / "provider-enabled.db",
        provider_analysis_enabled=True,
    )
    harness.seed_jobs(1, description="Synthetic Python FastAPI backend role")
    provider = CountingAnalyzer()
    monkeypatch.setattr(recommend_service, "analyze_job_text", provider)

    response = harness.client.post("/analysis/run", params={"limit": 1})

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert len(provider.calls) == 1
    state = harness.persisted_state()
    assert state["analysis_count"] == 1
    assert state["last_analyzed"] == [True]
    harness.client.close()
