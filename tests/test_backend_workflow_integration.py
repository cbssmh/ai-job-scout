from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Job, JobAnalysis
from app.db.schemas import JobCreate, RecommendationRequest, RecommendationResponse
from app.services import recommend_service
from app.services.job_service import create_job


def build_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return testing_session_local()


def test_backend_workflow_stores_analysis_and_builds_schema_valid_recommendation(monkeypatch):
    db = build_session()
    try:
        monkeypatch.setattr(
            recommend_service,
            "analyze_job_text",
            lambda description, title: {
                "role": "Backend Engineer",
                "tech_stack": "Python, FastAPI, Docker",
                "experience_level": "3+ years",
                "language_requirement": "English required",
                "visa_sponsorship": "possible",
                "summary": "Backend API role.",
            },
        )

        job = create_job(
            db,
            JobCreate(
                source="test",
                title="Backend Engineer",
                company="Example Corp",
                location="Berlin, Germany",
                url="https://example.com/jobs/backend-workflow",
                description_raw="Python FastAPI Docker backend API role.",
                posted_at="2026-07-01",
            ),
        )

        analysis_rows = recommend_service.analyze_all_jobs(db, limit=10)
        recommendations = recommend_service.get_recommendations_by_profile(
            db,
            RecommendationRequest(
                skills=["Python", "FastAPI", "Docker"],
                preferred_countries=["Germany"],
                visa_needed=True,
            ),
        )

        raw_job = db.query(Job).filter(Job.id == job.id).one()
        analysis = db.query(JobAnalysis).filter(JobAnalysis.job_id == job.id).one()

        assert raw_job.description_raw == "Python FastAPI Docker backend API role."
        assert len(analysis_rows) == 1
        assert analysis.job_id == raw_job.id
        assert analysis.role == "Backend Engineer"
        assert analysis.tech_stack == "Python, FastAPI, Docker"

        assert len(recommendations) == 1
        recommendation = recommendations[0]
        validated = RecommendationResponse.model_validate(recommendation)

        assert validated.job_id == raw_job.id
        assert 0 <= validated.match_score <= 100
        assert validated.skill_score == 100
        assert validated.language_bonus == 10
        assert validated.visa_bonus == 10
        assert validated.location_bonus == 10
        assert validated.reason
    finally:
        db.close()
