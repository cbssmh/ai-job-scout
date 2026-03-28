from sqlalchemy.orm import Session

from app.db.models import Job, JobAnalysis


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_jobs_with_analysis(self) -> list[tuple[Job, JobAnalysis]]:
        return (
            self.db.query(Job, JobAnalysis)
            .join(JobAnalysis, Job.id == JobAnalysis.job_id)
            .all()
        )