from app.domain.recommendation_models import ProcessedJob, UserProfile, EmbeddedJob


class EmbeddingService:
    """
    현재 버전:
    - 실제 임베딩 API 대신 skill overlap 기반 semantic-like similarity
    - 나중에 OpenAI embedding / sentence-transformers로 교체 가능
    """

    def build_features(self, processed_job: ProcessedJob, user: UserProfile) -> EmbeddedJob:
        similarity_score = self._calculate_similarity(processed_job.tech_stack, user.skills)
        return EmbeddedJob(
            processed_job=processed_job,
            similarity_score=similarity_score,
        )

    def _calculate_similarity(self, job_skills: list[str], user_skills: list[str]) -> int:
        if not job_skills or not user_skills:
            return 0

        job_set = {skill.strip().lower() for skill in job_skills if skill.strip()}
        user_set = {skill.strip().lower() for skill in user_skills if skill.strip()}

        if not job_set or not user_set:
            return 0

        intersection = job_set.intersection(user_set)
        union = job_set.union(user_set)

        score = int((len(intersection) / len(union)) * 100)
        return max(0, min(score, 100))