from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Job, JobAnalysis
from app.db.schemas import JobCreate
from app.domain.job_lifecycle import (
    JOB_STATUS_ACTIVE,
    JOB_STATUS_UPDATED,
    UPSERT_CREATED,
    UPSERT_UNCHANGED,
    UPSERT_UPDATED,
)
from app.repository.analysis_repository import AnalysisRepository
from app.services.job_service import upsert_job


def build_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TestingSessionLocal()


def build_job(description: str = "Python FastAPI backend role") -> JobCreate:
    return JobCreate(
        source="test",
        title="Backend Engineer",
        company="Example Corp",
        location="Berlin, Germany",
        url="https://example.com/jobs/backend",
        description_raw=description,
        posted_at="2026-07-01",
    )


def test_upsert_same_url_same_content_updates_last_seen_without_new_row():
    db = build_session()
    try:
        created = upsert_job(db, build_job())
        original_last_seen_at = created.job.last_seen_at

        unchanged = upsert_job(db, build_job())

        assert created.result == UPSERT_CREATED
        assert unchanged.result == UPSERT_UNCHANGED
        assert unchanged.job.id == created.job.id
        assert db.query(Job).count() == 1
        assert unchanged.job.last_seen_at >= original_last_seen_at
        assert unchanged.job.status == JOB_STATUS_ACTIVE
    finally:
        db.close()


def test_upsert_same_url_changed_content_marks_job_updated():
    db = build_session()
    try:
        created = upsert_job(db, build_job())
        updated = upsert_job(db, build_job(description="Python FastAPI Docker AWS backend role"))

        assert created.result == UPSERT_CREATED
        assert updated.result == UPSERT_UPDATED
        assert updated.job.id == created.job.id
        assert updated.job.status == JOB_STATUS_UPDATED
        assert updated.job.last_analyzed_at is None
        assert db.query(Job).count() == 1
    finally:
        db.close()


def test_updated_job_deletes_existing_analysis_for_reanalysis():
    db = build_session()
    try:
        created = upsert_job(db, build_job())
        analysis_repository = AnalysisRepository(db)
        analysis_repository.save_analysis(
            created.job,
            {
                "role": "Backend Engineer",
                "tech_stack": "Python, FastAPI",
                "experience_level": "3+ years",
                "language_requirement": "English required",
                "visa_sponsorship": "unknown",
                "summary": "Backend role.",
            },
        )
        assert db.query(JobAnalysis).filter(JobAnalysis.job_id == created.job.id).count() == 1

        upsert_job(db, build_job(description="Changed backend role with Docker"))

        assert db.query(JobAnalysis).filter(JobAnalysis.job_id == created.job.id).count() == 0
    finally:
        db.close()


def test_analysis_completion_sets_last_analyzed_at_and_restores_active_status():
    db = build_session()
    try:
        created = upsert_job(db, build_job())
        updated = upsert_job(db, build_job(description="Changed backend role with Docker"))
        assert updated.job.status == JOB_STATUS_UPDATED

        analysis_repository = AnalysisRepository(db)
        analysis_repository.save_analysis(
            updated.job,
            {
                "role": "Backend Engineer",
                "tech_stack": "Python, FastAPI, Docker",
                "experience_level": "3+ years",
                "language_requirement": "English required",
                "visa_sponsorship": "unknown",
                "summary": "Updated backend role.",
            },
        )

        db.refresh(updated.job)
        assert updated.job.last_analyzed_at is not None
        assert updated.job.status == JOB_STATUS_ACTIVE
    finally:
        db.close()
