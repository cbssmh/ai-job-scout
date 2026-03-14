from sqlalchemy.orm import Session

from app.db.models import Job, JobAnalysis
from app.agents.job_analyst import analyze_job_text
from app.agents.skill_matcher import calculate_match_score
from app.db.schemas import RecommendationRequest


def analyze_all_jobs(db: Session, limit: int = 20):
    jobs = (
        db.query(Job)
        .outerjoin(JobAnalysis, Job.id == JobAnalysis.job_id)
        .filter(JobAnalysis.id.is_(None))
        .limit(limit)
        .all()
    )

    results = []

    print(f"[analyze_all_jobs] jobs selected = {len(jobs)}")

    for job in jobs:
        print(f"[analyze_all_jobs] processing job_id={job.id}, title={job.title}")

        try:
            analyzed = analyze_job_text(job.description_raw, job.title)
            print(f"[analyze_all_jobs] analyzed result for job_id={job.id}: {analyzed}")

            row = JobAnalysis(
                job_id=job.id,
                role=str(analyzed.get("role", "")) if analyzed.get("role") is not None else None,
                tech_stack=str(analyzed.get("tech_stack", "")) if analyzed.get("tech_stack") is not None else None,
                experience_level=str(analyzed.get("experience_level", "")) if analyzed.get("experience_level") is not None else None,
                language_requirement=str(analyzed.get("language_requirement", "")) if analyzed.get("language_requirement") is not None else None,
                visa_sponsorship=str(analyzed.get("visa_sponsorship", "")) if analyzed.get("visa_sponsorship") is not None else None,
                summary=str(analyzed.get("summary", "")) if analyzed.get("summary") is not None else None,
            )

            db.add(row)
            db.commit()
            db.refresh(row)
            results.append(row)

        except Exception as e:
            db.rollback()
            print(f"[analyze_all_jobs] ERROR for job_id={job.id}: {repr(e)}")
            raise

    return results


def get_all_analysis(db: Session):
    return db.query(JobAnalysis).order_by(JobAnalysis.created_at.desc()).all()


def _extract_country_from_location(location: str | None) -> str:
    if not location:
        return ""

    parts = [part.strip() for part in location.split(",") if part.strip()]
    if not parts:
        return ""

    return parts[-1].lower()


def get_recommendations(db: Session):
    default_request = RecommendationRequest(
        skills=["Python", "FastAPI", "Docker", "AWS"],
        preferred_countries=[],
        visa_needed=False,
    )
    return get_recommendations_by_profile(db, default_request)


def get_recommendations_by_profile(db: Session, request: RecommendationRequest):
    rows = (
        db.query(Job, JobAnalysis)
        .join(JobAnalysis, Job.id == JobAnalysis.job_id)
        .all()
    )

    recommendations = []
    preferred_countries_lower = [country.lower() for country in request.preferred_countries]

    for job, analysis in rows:
        skill_score, skill_reason = calculate_match_score(request.skills, analysis.tech_stack)

        visa_bonus = 0
        if request.visa_needed and analysis.visa_sponsorship == "possible":
            visa_bonus = 10

        language_bonus = 0
        if analysis.language_requirement and "english" in analysis.language_requirement.lower():
            language_bonus = 10

        location_bonus = 0
        job_country = _extract_country_from_location(job.location)
        if preferred_countries_lower and job_country in preferred_countries_lower:
            location_bonus = 10

        total_score = min(skill_score + visa_bonus + language_bonus + location_bonus, 100)

        reason_parts = [skill_reason]
        reason_parts.append(f"language_bonus={language_bonus}")
        reason_parts.append(f"visa_bonus={visa_bonus}")
        reason_parts.append(f"location_bonus={location_bonus}")

        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "role": analysis.role,
            "tech_stack": analysis.tech_stack,
            "skill_score": skill_score,
            "language_bonus": language_bonus,
            "visa_bonus": visa_bonus,
            "location_bonus": location_bonus,
            "match_score": total_score,
            "visa_sponsorship": analysis.visa_sponsorship,
            "reason": "; ".join(reason_parts),
        })

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations