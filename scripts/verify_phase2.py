import logging
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import JobAnalysis
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


def build_job(description: str) -> JobCreate:
    return JobCreate(
        source="verify",
        title="Backend Engineer",
        company="Example Corp",
        location="Berlin, Germany",
        url="https://example.com/jobs/backend",
        description_raw=description,
        posted_at="2026-07-01",
    )


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "phase2_verify.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        try:
            created = upsert_job(db, build_job("Python FastAPI backend role"))
            assert_condition(created.result == UPSERT_CREATED, "expected created result")
            assert_condition(created.job.status == JOB_STATUS_ACTIVE, "created job should be ACTIVE")

            unchanged = upsert_job(db, build_job("Python FastAPI backend role"))
            assert_condition(unchanged.result == UPSERT_UNCHANGED, "expected unchanged result")
            assert_condition(unchanged.job.id == created.job.id, "unchanged upsert should reuse existing job")

            analysis_repository = AnalysisRepository(db)
            analysis_repository.save_analysis(
                unchanged.job,
                {
                    "role": "Backend Engineer",
                    "tech_stack": "Python, FastAPI",
                    "experience_level": "3+ years",
                    "language_requirement": "English required",
                    "visa_sponsorship": "unknown",
                    "summary": "Backend role.",
                },
            )
            assert_condition(unchanged.job.last_analyzed_at is not None, "analysis should set last_analyzed_at")

            updated = upsert_job(db, build_job("Python FastAPI Docker AWS backend role"))
            assert_condition(updated.result == UPSERT_UPDATED, "expected updated result")
            assert_condition(updated.job.status == JOB_STATUS_UPDATED, "updated job should be UPDATED")
            assert_condition(updated.job.last_analyzed_at is None, "updated job should clear last_analyzed_at")
            analysis_count = db.query(JobAnalysis).filter(JobAnalysis.job_id == updated.job.id).count()
            assert_condition(analysis_count == 0, "updated job should delete existing analysis")

            analysis_repository.save_analysis(
                updated.job,
                {
                    "role": "Backend Engineer",
                    "tech_stack": "Python, FastAPI, Docker, AWS",
                    "experience_level": "3+ years",
                    "language_requirement": "English required",
                    "visa_sponsorship": "unknown",
                    "summary": "Updated backend role.",
                },
            )
            db.refresh(updated.job)
            assert_condition(updated.job.last_analyzed_at is not None, "reanalyzed job should set last_analyzed_at")
            assert_condition(updated.job.status == JOB_STATUS_ACTIVE, "reanalyzed UPDATED job should become ACTIVE")

            logger.info("Phase 2 verification passed")
        finally:
            db.close()


if __name__ == "__main__":
    main()
