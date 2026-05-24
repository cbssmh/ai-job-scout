from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommend_service import get_recommendations, get_recommendations_by_profile

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=list[RecommendationResponse])
def read_recommendations(db: Session = Depends(get_db)):
    return get_recommendations(db)


@router.post("/run", response_model=list[RecommendationResponse])
def run_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    return get_recommendations_by_profile(db, request)