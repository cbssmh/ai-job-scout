import logging

from sqlalchemy.orm import Session

from app.agents.job_analyst import analyze_job_text
from app.db.schemas import RecommendationRequest
from app.domain.recommendation_models import RecommendationContext
from app.recommendation.recommendation_builder import RecommendationBuilder
from app.repository.analysis_repository import AnalysisRepository
from app.repository.recommendation_repository import RecommendationRepository
from app.scoring.recommendation_scorer import RecommendationScorer

logger = logging.getLogger(__name__)


def analyze_all_jobs(db: Session, limit: int = 20):
    analysis_repository = AnalysisRepository(db)
    jobs = analysis_repository.get_jobs_without_analysis(limit=limit)

    results = []
    failed_count = 0

    logger.info("analysis batch started selected_count=%s limit=%s", len(jobs), limit)

    for job in jobs:
        try:
            analyzed = analyze_job_text(job.description_raw, job.title)

            row = analysis_repository.save_analysis(job, analyzed)
            results.append(row)
            logger.info("analysis succeeded job_id=%s title=%s", job.id, job.title)

        except Exception as e:
            db.rollback()
            failed_count += 1
            logger.exception("analysis failed job_id=%s title=%s error=%s", job.id, job.title, repr(e))
            logger.error(
                "analysis batch aborted selected_count=%s success_count=%s failed_count=%s",
                len(jobs),
                len(results),
                failed_count,
            )
            raise

    logger.info(
        "analysis batch finished selected_count=%s success_count=%s failed_count=%s",
        len(jobs),
        len(results),
        failed_count,
    )
    return results


def get_all_analysis(db: Session):
    analysis_repository = AnalysisRepository(db)
    return analysis_repository.get_all_analysis()


def get_recommendations(db: Session):
    default_request = RecommendationRequest(
        skills=["Python", "FastAPI", "Docker", "AWS"],
        preferred_countries=[],
        visa_needed=False,
    )
    return get_recommendations_by_profile(db, default_request)


def get_recommendations_by_profile(db: Session, request: RecommendationRequest):
    recommendation_repository = RecommendationRepository(db)
    scorer = RecommendationScorer()
    builder = RecommendationBuilder()

    logger.info(
        "recommendation run started skills=%s preferred_countries=%s visa_needed=%s",
        request.skills,
        request.preferred_countries,
        request.visa_needed,
    )

    rows = recommendation_repository.get_jobs_with_analysis()
    recommendations = []

    for job, analysis in rows:
        context = RecommendationContext(
            job_id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            role=analysis.role,
            tech_stack=analysis.tech_stack,
            language_requirement=analysis.language_requirement,
            visa_sponsorship=analysis.visa_sponsorship,
        )

        score = scorer.score(context, request)
        recommendation = builder.build(context, score)
        recommendations.append(recommendation)

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    logger.info(
        "recommendation run finished analyzed_jobs=%s result_count=%s",
        len(rows),
        len(recommendations),
    )
    return recommendations
