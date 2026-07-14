from types import SimpleNamespace

from app.agents import job_analyst
from app.llm.client import LLMClientConfig


REQUIRED_ANALYSIS_FIELDS = {
    "role",
    "tech_stack",
    "experience_level",
    "language_requirement",
    "visa_sponsorship",
    "summary",
}


class FakeCompletions:
    def __init__(self, *, content: str | None = None, error: Exception | None = None):
        self.content = content
        self.error = error
        self.called = False

    def create(self, **kwargs):
        self.called = True
        if self.error:
            raise self.error

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content),
                )
            ],
        )


def build_fake_client(completions: FakeCompletions):
    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=completions,
        ),
    )


def build_fake_llm_config(completions: FakeCompletions):
    return LLMClientConfig(
        provider="test",
        model="test-model",
        client=build_fake_client(completions),
    )


def test_analyze_job_text_uses_rule_based_fallback_when_llm_client_raises(monkeypatch):
    completions = FakeCompletions(error=RuntimeError("network unavailable"))
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: build_fake_llm_config(completions),
    )

    result = job_analyst.analyze_job_text(
        "We need Python, FastAPI, Docker, English, and visa sponsorship.",
        "Backend Engineer",
    )

    assert completions.called is True
    assert set(result) == REQUIRED_ANALYSIS_FIELDS
    assert result["role"] == "Backend Engineer"
    assert result["tech_stack"] == "python, fastapi, docker"
    assert result["language_requirement"] == "English required/preferred"
    assert result["visa_sponsorship"] == "possible"
    assert "Rule-based fallback" in result["summary"]
    assert "LLM fallback reason: RuntimeError" in result["summary"]


def test_analyze_job_text_uses_rule_based_fallback_when_llm_returns_invalid_json(monkeypatch):
    completions = FakeCompletions(content="not valid json")
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: build_fake_llm_config(completions),
    )

    result = job_analyst.analyze_job_text(
        "Backend API engineer using Python and SQL. English required.",
        "API Engineer",
    )

    assert completions.called is True
    assert set(result) == REQUIRED_ANALYSIS_FIELDS
    assert result["role"] == "Backend Engineer"
    assert result["tech_stack"] == "python, sql"
    assert result["language_requirement"] == "English required/preferred"
    assert "Rule-based fallback" in result["summary"]
    assert "LLM fallback reason: JSONDecodeError" in result["summary"]


def test_analyze_job_text_missing_llm_fields_uses_current_default_policy(monkeypatch):
    completions = FakeCompletions(content='{"role": "Backend Engineer"}')
    monkeypatch.setattr(
        job_analyst,
        "get_llm_client_config",
        lambda: build_fake_llm_config(completions),
    )

    result = job_analyst.analyze_job_text(
        "Python FastAPI backend role with English.",
        "Backend Engineer",
    )

    assert completions.called is True
    assert set(result) == REQUIRED_ANALYSIS_FIELDS
    assert result["role"] == "Backend Engineer"
    assert result["tech_stack"] == ""
    assert result["experience_level"] == "unknown"
    assert result["language_requirement"] == "unknown"
    assert result["visa_sponsorship"] == "unknown"
    assert result["summary"] == "No summary"
    assert "Rule-based fallback" not in result["summary"]


def test_rule_based_fallback_contract_contains_downstream_fields():
    result = job_analyst.analyze_job_text_rule_based(
        "Full stack role with React, TypeScript, Node.js, English, and relocation support.",
        "Full Stack Engineer",
    )

    assert set(result) == REQUIRED_ANALYSIS_FIELDS
    assert result["role"] == "Full Stack Engineer"
    assert result["tech_stack"] == "react, typescript, node.js"
    assert result["language_requirement"] == "English required/preferred"
    assert result["visa_sponsorship"] == "possible"
    assert result["summary"].startswith("Rule-based fallback:")
