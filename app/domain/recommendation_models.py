from dataclasses import dataclass, field


@dataclass
class RecommendationContext:
    job_id: int
    title: str
    company: str
    location: str | None
    role: str | None
    tech_stack: str | None
    language_requirement: str | None
    visa_sponsorship: str | None


@dataclass
class ScoreBreakdown:
    skill_score: int
    skill_reason: str
    language_bonus: int
    visa_bonus: int
    location_bonus: int
    match_score: int
    reason_parts: list[str] = field(default_factory=list)


@dataclass
class ProcessedJob:
    job_id: int
    title: str
    company: str
    location: str | None
    role: str | None
    tech_stack: list[str]
    language_requirement: str | None
    visa_sponsorship: str | None
    summary: str | None


@dataclass
class UserProfile:
    skills: list[str]
    preferred_countries: list[str] = field(default_factory=list)
    visa_needed: bool = False


@dataclass
class EmbeddedJob:
    processed_job: ProcessedJob
    similarity_score: int


@dataclass
class FilterDecision:
    passed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class ScoredJob:
    job_id: int
    title: str
    company: str
    role: str | None
    tech_stack: str | None
    skill_score: int
    similarity_score: int
    language_bonus: int
    visa_bonus: int
    location_bonus: int
    match_score: int
    visa_sponsorship: str | None
    reason_parts: list[str] = field(default_factory=list)
