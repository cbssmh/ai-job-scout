from app.domain.recommendation_models import EmbeddedJob, UserProfile, FilterDecision


class JobFilter:
    def apply(self, embedded_job: EmbeddedJob, user: UserProfile) -> FilterDecision:
        reasons: list[str] = []

        # 필수 스킬이 하나도 안 맞으면 완전 탈락시키고 싶다면 여기서 처리 가능
        # 지금은 너무 공격적으로 자르지 않기 위해 soft하게 둔다.
        # 대신 완전히 비어 있는 경우만 탈락 처리
        if not embedded_job.processed_job.tech_stack:
            reasons.append("No extracted tech stack")
            return FilterDecision(passed=False, reasons=reasons)

        # 예시: role이 전혀 없는 분석 결과는 품질이 낮다고 보고 제외
        if not embedded_job.processed_job.role:
            reasons.append("No analyzed role")
            return FilterDecision(passed=False, reasons=reasons)

        return FilterDecision(passed=True, reasons=[])