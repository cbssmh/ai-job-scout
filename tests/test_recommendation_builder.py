from app.domain.recommendation_models import RecommendationContext, ScoreBreakdown
from app.recommendation.recommendation_builder import RecommendationBuilder


def test_builder_creates_recommendation_dict():
    builder = RecommendationBuilder()

    context = RecommendationContext(
        job_id=1,
        title="Backend Engineer",
        company="Example Corp",
        location="Berlin, Germany",
        role="Backend Developer",
        tech_stack="Python, FastAPI, Docker",
        language_requirement="English",
        visa_sponsorship="possible",
    )

    score = ScoreBreakdown(
        skill_score=80,
        skill_reason="Matched skills: python, fastapi",
        language_bonus=10,
        visa_bonus=10,
        location_bonus=10,
        match_score=100,
        reason_parts=[
            "Matched skills: python, fastapi",
            "language_bonus=10",
            "visa_bonus=10",
            "location_bonus=10",
        ],
    )

    result = builder.build(context, score)

    assert result["job_id"] == 1
    assert result["title"] == "Backend Engineer"
    assert result["company"] == "Example Corp"
    assert result["role"] == "Backend Developer"
    assert result["tech_stack"] == "Python, FastAPI, Docker"
    assert result["skill_score"] == 80
    assert result["language_bonus"] == 10
    assert result["visa_bonus"] == 10
    assert result["location_bonus"] == 10
    assert result["match_score"] == 100
    assert result["visa_sponsorship"] == "possible"
    assert "Matched skills" in result["reason"]