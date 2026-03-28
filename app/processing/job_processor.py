from app.db.models import Job, JobAnalysis
from app.domain.recommendation_models import ProcessedJob


class JobProcessor:
    def process(self, job: Job, analysis: JobAnalysis) -> ProcessedJob:
        tech_stack = self._normalize_tech_stack(analysis.tech_stack)

        return ProcessedJob(
            job_id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            role=analysis.role,
            tech_stack=tech_stack,
            language_requirement=analysis.language_requirement,
            visa_sponsorship=analysis.visa_sponsorship,
            summary=analysis.summary,
        )

    def _normalize_tech_stack(self, tech_stack: str | None) -> list[str]:
        if not tech_stack:
            return []

        normalized = []
        for item in tech_stack.split(","):
            skill = item.strip().lower()
            if not skill:
                continue

            skill = skill.replace("nodejs", "node.js")
            skill = skill.replace("postgre sql", "postgresql")

            if skill not in normalized:
                normalized.append(skill)

        return normalized