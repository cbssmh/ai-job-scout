from pydantic import BaseModel
from datetime import datetime


class JobCreate(BaseModel):
    source: str
    title: str
    company: str
    location: str | None = None
    url: str
    description_raw: str
    posted_at: str | None = None


class JobResponse(BaseModel):
    id: int
    source: str
    title: str
    company: str
    location: str | None = None
    url: str
    description_raw: str
    posted_at: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobAnalysisResponse(BaseModel):
    id: int
    job_id: int
    role: str | None = None
    tech_stack: str | None = None
    experience_level: str | None = None
    language_requirement: str | None = None
    visa_sponsorship: str | None = None
    summary: str | None = None

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    job_id: int
    title: str
    company: str
    role: str | None = None
    tech_stack: str | None = None
    skill_score: int
    language_bonus: int
    visa_bonus: int
    location_bonus: int
    match_score: int
    visa_sponsorship: str | None = None
    reason: str

    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    skills: list[str]
    preferred_countries: list[str] = []
    visa_needed: bool = False