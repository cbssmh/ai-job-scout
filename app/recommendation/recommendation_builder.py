from app.domain.recommendation_models import RecommendationContext, ScoreBreakdown


class RecommendationBuilder:
    def build(
        self,
        context: RecommendationContext,
        score: ScoreBreakdown,
    ) -> dict:
        return {
            "job_id": context.job_id,
            "title": context.title,
            "company": context.company,
            "role": context.role,
            "tech_stack": context.tech_stack,
            "skill_score": score.skill_score,
            "language_bonus": score.language_bonus,
            "visa_bonus": score.visa_bonus,
            "location_bonus": score.location_bonus,
            "match_score": score.match_score,
            "visa_sponsorship": context.visa_sponsorship,
            "reason": "; ".join(score.reason_parts),
        }