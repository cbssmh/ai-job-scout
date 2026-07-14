from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    title: str
    company: str
    location: str | None = None
    url: str
    description_raw: str
    posted_at: str | None = None
    content_hash: str | None = None
    status: str = "ACTIVE"
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    last_analyzed_at: datetime | None = None
    created_at: datetime


class JobAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    role: str | None = None
    tech_stack: str | None = None
    experience_level: str | None = None
    language_requirement: str | None = None
    visa_sponsorship: str | None = None
    summary: str | None = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    title: str
    company: str
    role: str | None = None
    tech_stack: str | None = None
    skill_score: int
    similarity_score: int | None = None
    language_bonus: int
    visa_bonus: int
    location_bonus: int
    match_score: int
    visa_sponsorship: str | None = None
    reason: str


class RecommendationRequest(BaseModel):
    skills: list[str]
    preferred_countries: list[str] = []
    visa_needed: bool = False
