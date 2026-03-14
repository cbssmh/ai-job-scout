def calculate_match_score(user_skills: list[str], job_tech_stack: str | None) -> tuple[int, str]:
    if not job_tech_stack:
        return 0, "No extracted tech stack."

    job_skills = [skill.strip().lower() for skill in job_tech_stack.split(",") if skill.strip()]
    user_skills_lower = [skill.lower() for skill in user_skills]

    matched = [skill for skill in job_skills if skill in user_skills_lower]

    if not job_skills:
        return 0, "No valid job skills found."

    score = int((len(matched) / len(job_skills)) * 100)

    if matched:
        reason = f"Matched skills: {', '.join(matched)}"
    else:
        reason = "No matching skills found."

    return score, reason