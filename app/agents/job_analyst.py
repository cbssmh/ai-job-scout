import json
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """
You are a job posting analysis assistant.

Extract structured information from the job description.

Return ONLY valid JSON with these fields:
- role
- tech_stack
- experience_level
- language_requirement
- visa_sponsorship
- summary

Rules:
- tech_stack must be a comma-separated string, not a list
- experience_level must be a short string
- language_requirement must be a short string
- visa_sponsorship must be a short string such as possible, unknown, unlikely
- summary must be one short sentence
"""


def _clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def analyze_job_text_rule_based(text: str, title: str = "") -> dict:
    combined = f"{title}\n{text}".lower()

    tech_candidates = [
        "python",
        "fastapi",
        "docker",
        "aws",
        "sql",
        "postgresql",
        "airflow",
        "kubernetes",
        "java",
        "go",
        "scala",
        "spark",
        "react",
        "typescript",
        "node.js",
        "nodejs",
    ]
    found_tech = [tech for tech in tech_candidates if tech in combined]

    role = "Unknown"
    if "backend" in combined or "api engineer" in combined:
        role = "Backend Engineer"
    elif "frontend" in combined:
        role = "Frontend Engineer"
    elif "full stack" in combined or "fullstack" in combined:
        role = "Full Stack Engineer"
    elif "data engineer" in combined:
        role = "Data Engineer"
    elif "data scientist" in combined:
        role = "Data Scientist"
    elif "machine learning" in combined or "ml engineer" in combined:
        role = "ML Engineer"
    elif "software engineer" in combined:
        role = "Software Engineer"
    elif "android engineer" in combined:
        role = "Android Engineer"
    elif "ios engineer" in combined:
        role = "iOS Engineer"

    experience = "unknown"
    if "7+ years" in combined:
        experience = "7+ years"
    elif "5+ years" in combined:
        experience = "5+ years"
    elif "3+ years" in combined:
        experience = "3+ years"
    elif "2+ years" in combined:
        experience = "2+ years"
    elif "1+ years" in combined:
        experience = "1+ years"

    language = "unknown"
    if "english" in combined:
        language = "English required/preferred"

    visa = "unknown"
    if "visa sponsorship" in combined or "relocation support" in combined:
        visa = "possible"

    summary = (
        f"Rule-based fallback: role={role}, "
        f"tech={', '.join(found_tech)}, "
        f"experience={experience}"
    )

    return {
        "role": role,
        "tech_stack": ", ".join(found_tech),
        "experience_level": experience,
        "language_requirement": language,
        "visa_sponsorship": visa,
        "summary": summary,
    }


def analyze_job_text(text: str, title: str = "") -> dict:
    prompt = f"""
Job title:
{title}

Job description:
{text}

Return JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content or ""
        content = _clean_json_text(content)
        data = json.loads(content)

        tech_stack = data.get("tech_stack")
        if isinstance(tech_stack, list):
            tech_stack = ", ".join(str(x) for x in tech_stack)

        return {
            "role": str(data.get("role", "")) or "Unknown",
            "tech_stack": str(tech_stack or ""),
            "experience_level": str(data.get("experience_level", "")) or "unknown",
            "language_requirement": str(data.get("language_requirement", "")) or "unknown",
            "visa_sponsorship": str(data.get("visa_sponsorship", "")) or "unknown",
            "summary": str(data.get("summary", "")) or "No summary",
        }

    except Exception as e:
        fallback = analyze_job_text_rule_based(text, title)
        fallback["summary"] = (
            f"{fallback['summary']} | "
            f"LLM fallback reason: {type(e).__name__}"
        )
        return fallback