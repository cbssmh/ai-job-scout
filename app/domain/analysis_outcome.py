ANALYSIS_OUTCOME_PROVIDER_SUCCESS = "provider_success"
ANALYSIS_OUTCOME_DEGRADED_FALLBACK = "degraded_fallback"
FALLBACK_SUMMARY_PREFIX = "Rule-based fallback:"


def outcome_from_summary(summary: str | None) -> str:
    if summary and summary.startswith(FALLBACK_SUMMARY_PREFIX):
        return ANALYSIS_OUTCOME_DEGRADED_FALLBACK
    return ANALYSIS_OUTCOME_PROVIDER_SUCCESS
