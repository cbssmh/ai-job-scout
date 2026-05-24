from app.db.schemas import RecommendationRequest
from app.domain.recommendation_models import RecommendationContext
from app.scoring.recommendation_scorer import RecommendationScorer


def test_score_applies_skill_visa_language_location_bonus():
    scorer = RecommendationScorer()

    context = RecommendationContext(
        job_id=1,
        title="Backend Engineer",
        company="Example Corp",
        location="Berlin, Germany",
        role="Backend Developer",
        tech_stack="Python, FastAPI, Docker",
        language_requirement="Business English required",
        visa_sponsorship="possible",
    )

    request = RecommendationRequest(
        skills=["Python", "FastAPI", "AWS"],
        preferred_countries=["Germany"],
        visa_needed=True,
    )

    result = scorer.score(context, request)

    assert result.skill_score >= 0
    assert result.language_bonus == 10
    assert result.visa_bonus == 10
    assert result.location_bonus == 10
    assert result.match_score <= 100
    assert "language_bonus=10" in result.reason_parts
    assert "visa_bonus=10" in result.reason_parts
    assert "location_bonus=10" in result.reason_parts


def test_score_returns_zero_location_bonus_when_country_not_preferred():
    scorer = RecommendationScorer()

    context = RecommendationContext(
        job_id=2,
        title="Data Engineer",
        company="Another Corp",
        location="Tokyo, Japan",
        role="Data Engineer",
        tech_stack="Python, SQL, Airflow",
        language_requirement="English preferred",
        visa_sponsorship="possible",
    )

    request = RecommendationRequest(
        skills=["Python", "SQL"],
        preferred_countries=["Germany"],
        visa_needed=True,
    )

    result = scorer.score(context, request)

    assert result.location_bonus == 0
    assert result.language_bonus == 10
    assert result.visa_bonus == 10


def test_score_returns_zero_visa_bonus_when_user_does_not_need_visa():
    scorer = RecommendationScorer()

    context = RecommendationContext(
        job_id=3,
        title="Platform Engineer",
        company="Infra Corp",
        location="Seoul, Korea",
        role="Platform Engineer",
        tech_stack="Python, Docker, Kubernetes",
        language_requirement="English required",
        visa_sponsorship="possible",
    )

    request = RecommendationRequest(
        skills=["Python", "Docker"],
        preferred_countries=["Korea"],
        visa_needed=False,
    )

    result = scorer.score(context, request)

    assert result.visa_bonus == 0
    assert result.language_bonus == 10
    assert result.location_bonus == 10


def test_score_caps_total_score_at_100():
    scorer = RecommendationScorer()

    context = RecommendationContext(
        job_id=4,
        title="Senior Backend Engineer",
        company="Top Corp",
        location="Berlin, Germany",
        role="Backend Engineer",
        tech_stack="Python, FastAPI, Docker, AWS",
        language_requirement="English required",
        visa_sponsorship="possible",
    )

    request = RecommendationRequest(
        skills=["Python", "FastAPI", "Docker", "AWS"],
        preferred_countries=["Germany"],
        visa_needed=True,
    )

    result = scorer.score(context, request)

    assert result.match_score == 100


def test_score_handles_missing_language_and_visa():
    scorer = RecommendationScorer()

    context = RecommendationContext(
        job_id=5,
        title="Software Engineer",
        company="Simple Corp",
        location="Paris, France",
        role="Software Engineer",
        tech_stack="Python, Flask",
        language_requirement=None,
        visa_sponsorship=None,
    )

    request = RecommendationRequest(
        skills=["Python"],
        preferred_countries=["France"],
        visa_needed=True,
    )

    result = scorer.score(context, request)

    assert result.language_bonus == 0
    assert result.visa_bonus == 0
    assert result.location_bonus == 10