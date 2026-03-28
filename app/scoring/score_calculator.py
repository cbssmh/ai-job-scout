from app.domain.recommendation_models import EmbeddedJob, UserProfile, ScoredJob


class ScoreCalculator:
    def calculate(self, embedded_job: EmbeddedJob, user: UserProfile) -> ScoredJob:
        processed = embedded_job.processed_job

        skill_score, skill_reason = self._calculate_skill_score(
            user.skills,
            processed.tech_stack,
        )

        similarity_score = embedded_job.similarity_score
        language_bonus = self._calculate_language_bonus(processed.language_requirement)
        visa_bonus = self._calculate_visa_bonus(user.visa_needed, processed.visa_sponsorship)
        location_bonus = self._calculate_location_bonus(
            processed.location,
            user.preferred_countries,
        )

        raw_total = (
            int(skill_score * 0.5)
            + int(similarity_score * 0.2)
            + language_bonus
            + visa_bonus
            + location_bonus
        )

        total_score = max(0, min(raw_total, 100))

        reason_parts = [
            skill_reason,
            f"similarity_score={similarity_score}",
            f"language_bonus={language_bonus}",
            f"visa_bonus={visa_bonus}",
            f"location_bonus={location_bonus}",
        ]

        return ScoredJob(
            job_id=processed.job_id,
            title=processed.title,
            company=processed.company,
            role=processed.role,
            tech_stack=", ".join(processed.tech_stack) if processed.tech_stack else None,
            skill_score=skill_score,
            similarity_score=similarity_score,
            language_bonus=language_bonus,
            visa_bonus=visa_bonus,
            location_bonus=location_bonus,
            match_score=total_score,
            visa_sponsorship=processed.visa_sponsorship,
            reason_parts=reason_parts,
        )

    def _calculate_skill_score(self, user_skills: list[str], job_tech_stack: list[str]) -> tuple[int, str]:
        if not job_tech_stack:
            return 0, "No extracted tech stack"

        user_skills_lower = [skill.strip().lower() for skill in user_skills if skill.strip()]
        job_skills_lower = [skill.strip().lower() for skill in job_tech_stack if skill.strip()]

        if not job_skills_lower:
            return 0, "No valid job skills found"

        matched = [skill for skill in job_skills_lower if skill in user_skills_lower]
        score = int((len(matched) / len(job_skills_lower)) * 100)

        if matched:
            return score, f"Matched skills: {', '.join(matched)}"
        return score, "No matching skills found"

    def _calculate_language_bonus(self, language_requirement: str | None) -> int:
        if not language_requirement:
            return 0

        text = language_requirement.lower()
        if "english" in text:
            return 10
        return 0

    def _calculate_visa_bonus(self, visa_needed: bool, visa_sponsorship: str | None) -> int:
        if not visa_needed:
            return 0

        if not visa_sponsorship:
            return 0

        if visa_sponsorship.lower() == "possible":
            return 10

        return 0

    def _calculate_location_bonus(self, location: str | None, preferred_countries: list[str]) -> int:
        if not preferred_countries or not location:
            return 0

        job_country = self._extract_country_from_location(location)
        preferred_countries_lower = [country.strip().lower() for country in preferred_countries if country.strip()]

        if job_country and job_country in preferred_countries_lower:
            return 10

        return 0

    def _extract_country_from_location(self, location: str | None) -> str:
        if not location:
            return ""

        parts = [part.strip() for part in location.split(",") if part.strip()]
        if not parts:
            return ""

        return parts[-1].lower()