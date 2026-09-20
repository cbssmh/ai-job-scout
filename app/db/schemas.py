from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.domain.analysis_outcome import (
    ANALYSIS_OUTCOME_PROVIDER_SUCCESS,
)


class JobCreate(BaseModel):
    source: str = Field(max_length=64)
    title: str = Field(max_length=256)
    company: str = Field(max_length=256)
    location: str | None = Field(default=None, max_length=256)
    url: str = Field(max_length=2048)
    description_raw: str = Field(max_length=32_000)
    posted_at: str | None = Field(default=None, max_length=64)


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
    analysis_outcome: Literal[
        "provider_success",
        "degraded_fallback",
    ] = ANALYSIS_OUTCOME_PROVIDER_SUCCESS


class AnalysisFailureResponse(BaseModel):
    job_id: int
    title: str
    error_type: str
    retryable: bool = True


class AnalysisBatchResponse(BaseModel):
    status: Literal["completed", "degraded", "partial", "failed"]
    requested_limit: int
    selected_count: int
    completed: list[JobAnalysisResponse] = Field(default_factory=list)
    degraded: list[JobAnalysisResponse] = Field(default_factory=list)
    failed: list[AnalysisFailureResponse] = Field(default_factory=list)
    remaining_count: int


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
