from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import JobResponse, JobCreate
from app.services.job_service import create_job, get_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobResponse])
def read_jobs(db: Session = Depends(get_db)):
    return get_jobs(db)


@router.post("/", response_model=JobResponse)
def add_job(job: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, job)