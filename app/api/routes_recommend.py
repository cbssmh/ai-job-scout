from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import JobAnalysisResponse
from app.services.recommend_service import analyze_all_jobs, get_all_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=list[JobAnalysisResponse])
def run_analysis(limit: int = 20, db: Session = Depends(get_db)):
    return analyze_all_jobs(db, limit=limit)


@router.get("/", response_model=list[JobAnalysisResponse])
def read_analysis(db: Session = Depends(get_db)):
    return get_all_analysis(db)