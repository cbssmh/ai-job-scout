from sqlalchemy.orm import Session
from app.db.models import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Job]:
        return self.db.query(Job).order_by(Job.created_at.desc()).all()

    def get_by_id(self, job_id: int) -> Job | None:
        return self.db.query(Job).filter(Job.id == job_id).first()