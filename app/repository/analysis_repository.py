from sqlalchemy.orm import Session

from app.db.models import Job, JobAnalysis


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_jobs_without_analysis(self, limit: int = 20) -> list[Job]:
        return (
            self.db.query(Job)
            .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
            .filter(JobAnalysis.id.is_(None))
            .limit(limit)
            .all()
        )

    def save_analysis(self, job: Job, analyzed: dict) -> JobAnalysis:
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
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_all_analysis(self) -> list[JobAnalysis]:
        return self.db.query(JobAnalysis).order_by(JobAnalysis.created_at.desc()).all()