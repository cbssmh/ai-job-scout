from sqlalchemy.orm import Session
from app.db.models import Job
from app.db.schemas import JobCreate


def create_job(db: Session, job_data: JobCreate) -> Job:
    job = Job(**job_data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_jobs(db: Session):
    return db.query(Job).order_by(Job.created_at.desc()).all()