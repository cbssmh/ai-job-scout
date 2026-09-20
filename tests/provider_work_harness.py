from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes_jobs import router as jobs_router
from app.api.routes_recommend import router as analysis_router
from app.db.database import Base, get_db
from app.db.models import Job, JobAnalysis
from app.db.schemas import JobCreate
from app.services.job_service import create_job


MAX_ANALYSIS_LIMIT = 20
MAX_JOB_DESCRIPTION_CHARS = 32_000


def valid_analysis(summary: str = "fake provider result") -> dict[str, str]:
    return {
        "role": "Backend Engineer",
        "tech_stack": "Python, FastAPI",
        "experience_level": "3+ years",
        "language_requirement": "English required",
        "visa_sponsorship": "unknown",
        "summary": summary,
    }


class CountingAnalyzer:
    """Deterministic non-network replacement for the provider boundary."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self._lock = Lock()

    def __call__(self, text: str, title: str = "") -> dict[str, str]:
        with self._lock:
            self.calls.append((text, title))
        return valid_analysis()


@dataclass
class ProviderWorkHarness:
    app: FastAPI
    client: TestClient
    session_factory: sessionmaker[Session]

    def seed_jobs(
        self,
        count: int,
        *,
        description: str = "Python FastAPI backend role",
        url_prefix: str = "https://example.invalid/provider-boundary",
    ) -> list[int]:
        db = self.session_factory()
        try:
            ids = []
            for index in range(count):
                job = create_job(
                    db,
                    JobCreate(
                        source="phase-2a-test",
                        title=f"Boundary Job {index}",
                        company="Example Corp",
                        location="Remote",
                        url=f"{url_prefix}/{index}",
                        description_raw=description,
                    ),
                )
                ids.append(job.id)
            return ids
        finally:
            db.close()

    def persisted_state(self) -> dict[str, object]:
        db = self.session_factory()
        try:
            jobs = db.query(Job).order_by(Job.id).all()
            return {
                "job_count": len(jobs),
                "analysis_count": db.query(JobAnalysis).count(),
                "statuses": [job.status for job in jobs],
                "last_analyzed": [job.last_analyzed_at is not None for job in jobs],
                "summaries": [
                    row.summary
                    for row in db.query(JobAnalysis).order_by(JobAnalysis.job_id).all()
                ],
            }
        finally:
            db.close()


def build_provider_work_harness(database_path: Path) -> ProviderWorkHarness:
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False, "timeout": 5},
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app = FastAPI()
    app.include_router(jobs_router)
    app.include_router(analysis_router)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, raise_server_exceptions=False)
    return ProviderWorkHarness(
        app=app,
        client=client,
        session_factory=testing_session,
    )
