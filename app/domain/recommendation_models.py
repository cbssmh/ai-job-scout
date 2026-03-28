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