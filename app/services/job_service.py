from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Job, JobAnalysis
from app.db.schemas import JobCreate
from app.domain.job_lifecycle import (
    JOB_STATUS_ACTIVE,
    JOB_STATUS_CLOSED,
    JOB_STATUS_UPDATED,
    UPSERT_CREATED,
    UPSERT_UNCHANGED,
    UPSERT_UPDATED,
)
from app.utils.hash import generate_job_content_hash


@dataclass
class JobUpsertResult:
    job: Job
    result: str


def _build_content_hash(job_data: JobCreate) -> str:
    return generate_job_content_hash(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description_raw=job_data.description_raw,
    )


def create_job(db: Session, job_data: JobCreate) -> Job:
    now = datetime.utcnow()
    job = Job(
        **job_data.model_dump(),
        content_hash=_build_content_hash(job_data),
        status=JOB_STATUS_ACTIVE,
        first_seen_at=now,
        last_seen_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def upsert_job(db: Session, job_data: JobCreate) -> JobUpsertResult:
    now = datetime.utcnow()
    content_hash = _build_content_hash(job_data)

    existing = db.query(Job).filter(Job.url == job_data.url).first()
    if existing is None:
        job = Job(
            **job_data.model_dump(),
            content_hash=content_hash,
            status=JOB_STATUS_ACTIVE,
            first_seen_at=now,
            last_seen_at=now,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return JobUpsertResult(job=job, result=UPSERT_CREATED)

    if existing.content_hash == content_hash:
        existing.last_seen_at = now
        if existing.status == JOB_STATUS_CLOSED:
            existing.status = JOB_STATUS_ACTIVE
        db.commit()
        db.refresh(existing)
        return JobUpsertResult(job=existing, result=UPSERT_UNCHANGED)

    existing.title = job_data.title
    existing.company = job_data.company
    existing.location = job_data.location
    existing.description_raw = job_data.description_raw
    existing.posted_at = job_data.posted_at
    existing.content_hash = content_hash
    existing.status = JOB_STATUS_UPDATED
    existing.last_seen_at = now
    existing.last_analyzed_at = None

    db.query(JobAnalysis).filter(JobAnalysis.job_id == existing.id).delete()
    db.commit()
    db.refresh(existing)
    return JobUpsertResult(job=existing, result=UPSERT_UPDATED)


def get_jobs(db: Session):
    return db.query(Job).order_by(Job.created_at.desc()).all()
