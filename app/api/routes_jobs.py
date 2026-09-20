from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import JobResponse, JobCreate
from app.services.job_service import create_job, get_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])
MAX_JOB_REQUEST_BODY_BYTES = 64 * 1024


async def enforce_job_request_body_size(request: Request) -> None:
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_JOB_REQUEST_BODY_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="Job request body exceeds 64 KiB.",
                )
        except ValueError:
            pass

    if len(await request.body()) > MAX_JOB_REQUEST_BODY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Job request body exceeds 64 KiB.",
        )


@router.get("/", response_model=list[JobResponse])
def read_jobs(db: Session = Depends(get_db)):
    return get_jobs(db)


@router.post("/", response_model=JobResponse)
def add_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    _body_size: None = Depends(enforce_job_request_body_size),
):
    return create_job(db, job)
