from sqlalchemy.orm import Session

from app.agents.job_analyst import analyze_job_text
from app.db.schemas import RecommendationRequest
from app.domain.recommendation_models import RecommendationContext
from app.recommendation.recommendation_builder import RecommendationBuilder
from app.repository.analysis_repository import AnalysisRepository
from app.repository.recommendation_repository import RecommendationRepository
from app.scoring.recommendation_scorer import RecommendationScorer


def analyze_all_jobs(db: Session, limit: int = 20):
    analysis_repository = AnalysisRepository(db)
    jobs = analysis_repository.get_jobs_without_analysis(limit=limit)

    results = []

    print(f"[analyze_all_jobs] jobs selected = {len(jobs)}")

    for job in jobs:
        print(f"[analyze_all_jobs] processing job_id={job.id}, title={job.title}")

        try:
            analyzed = analyze_job_text(job.description_raw, job.title)
            print(f"[analyze_all_jobs] analyzed result for job_id={job.id}: {analyzed}")

            row = analysis_repository.save_analysis(job, analyzed)
            results.append(row)

        except Exception as e:
            db.rollback()
            print(f"[analyze_all_jobs] ERROR for job_id={job.id}: {repr(e)}")
            raise

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
    return recommendations