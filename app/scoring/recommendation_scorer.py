from app.agents.skill_matcher import calculate_match_score
from app.db.schemas import RecommendationRequest
from app.domain.recommendation_models import RecommendationContext, ScoreBreakdown
from app.processing.location_parser import LocationParser


class RecommendationScorer:
    def score(
        self,
        context: RecommendationContext,
        request: RecommendationRequest,
    ) -> ScoreBreakdown:
        preferred_countries_lower = [
            country.lower().strip()
            for country in request.preferred_countries
            if country and country.strip()
        ]

        skill_score, skill_reason = calculate_match_score(
            request.skills,
            context.tech_stack,
        )

        visa_bonus = self._calculate_visa_bonus(
            visa_needed=request.visa_needed,
            visa_sponsorship=context.visa_sponsorship,
        )

        language_bonus = self._calculate_language_bonus(
            context.language_requirement
        )

        location_bonus = self._calculate_location_bonus(
            location=context.location,
            preferred_countries_lower=preferred_countries_lower,
        )

        total_score = min(
            skill_score + visa_bonus + language_bonus + location_bonus,
            100,
        )

        reason_parts = [
            skill_reason,
            f"language_bonus={language_bonus}",
            f"visa_bonus={visa_bonus}",
            f"location_bonus={location_bonus}",
        ]

        return ScoreBreakdown(
            skill_score=skill_score,
            skill_reason=skill_reason,
            language_bonus=language_bonus,
            visa_bonus=visa_bonus,
            location_bonus=location_bonus,
            match_score=total_score,
            reason_parts=reason_parts,
        )

    def _calculate_visa_bonus(
        self,
        visa_needed: bool,
        visa_sponsorship: str | None,
    ) -> int:
        if visa_needed and visa_sponsorship == "possible":
            return 10
        return 0

    def _calculate_language_bonus(
        self,
        language_requirement: str | None,
    ) -> int:
        if language_requirement and "english" in language_requirement.lower():
            return 10
        return 0

    def _calculate_location_bonus(
        self,
        location: str | None,
        preferred_countries_lower: list[str],
    ) -> int:
        if not preferred_countries_lower:
            return 0

        job_country = LocationParser.extract_country(location)
        if job_country in preferred_countries_lower:
            return 10

        return 0