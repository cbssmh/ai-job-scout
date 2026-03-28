from app.domain.recommendation_models import ScoredJob


class RecommendationService:
    def build(self, scored_jobs: list[ScoredJob]) -> list[dict]:
        scored_jobs.sort(key=lambda x: x.match_score, reverse=True)

        results: list[dict] = []
        for item in scored_jobs:
            results.append({
                "job_id": item.job_id,
                "title": item.title,
                "company": item.company,
                "role": item.role,
                "tech_stack": item.tech_stack,
                "skill_score": item.skill_score,
                "similarity_score": item.similarity_score,
                "language_bonus": item.language_bonus,
                "visa_bonus": item.visa_bonus,
                "location_bonus": item.location_bonus,
                "match_score": item.match_score,
                "visa_sponsorship": item.visa_sponsorship,
                "reason": "; ".join(item.reason_parts),
            })
        return results