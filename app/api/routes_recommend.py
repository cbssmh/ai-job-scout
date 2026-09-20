from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import AnalysisBatchResponse, JobAnalysisResponse
from app.services.recommend_service import (
    AnalysisAlreadyRunningError,
    analyze_all_jobs,
    get_all_analysis,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisBatchResponse)
def run_analysis(
    limit: Annotated[int, Query(ge=1, le=20)] = 20,
    db: Session = Depends(get_db),
):
    try:
        return analyze_all_jobs(db, limit=limit)
    except AnalysisAlreadyRunningError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[JobAnalysisResponse])
def read_analysis(db: Session = Depends(get_db)):
    return get_all_analysis(db)
