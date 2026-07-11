from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import Job, JobAnalysis
from app.domain.job_lifecycle import JOB_STATUS_ACTIVE, JOB_STATUS_UPDATED


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_jobs_without_analysis(self, limit: int = 20) -> list[Job]:
        return (
            self.db.query(Job)
            .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
            .filter(
                Job.status.in_([JOB_STATUS_ACTIVE, JOB_STATUS_UPDATED]),
                or_(
                    JobAnalysis.id.is_(None),
                    Job.status == JOB_STATUS_UPDATED,
                    Job.last_analyzed_at.is_(None),
                ),
            )
            .limit(limit)
            .all()
        )

    def save_analysis(self, job: Job, analyzed: dict) -> JobAnalysis:
        existing = (
            self.db.query(JobAnalysis)
            .filter(JobAnalysis.job_id == job.id)
            .first()
        )
        if existing is not None:
            self.db.delete(existing)
            self.db.flush()

        row = JobAnalysis(
            job_id=job.id,
            role=str(analyzed.get("role", "")) if analyzed.get("role") is not None else None,
            tech_stack=str(analyzed.get("tech_stack", "")) if analyzed.get("tech_stack") is not None else None,
            experience_level=str(analyzed.get("experience_level", "")) if analyzed.get("experience_level") is not None else None,
            language_requirement=str(analyzed.get("language_requirement", "")) if analyzed.get("language_requirement") is not None else None,
            visa_sponsorship=str(analyzed.get("visa_sponsorship", "")) if analyzed.get("visa_sponsorship") is not None else None,
            summary=str(analyzed.get("summary", "")) if analyzed.get("summary") is not None else None,
        )

        self.db.add(row)
        job.last_analyzed_at = datetime.utcnow()
        if job.status == JOB_STATUS_UPDATED:
            job.status = JOB_STATUS_ACTIVE

        self.db.commit()
        self.db.refresh(row)
        self.db.refresh(job)
        return row

    def get_all_analysis(self) -> list[JobAnalysis]:
        return self.db.query(JobAnalysis).order_by(JobAnalysis.created_at.desc()).all()
