import logging

import requests

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"
logger = logging.getLogger(__name__)

TARGET_KEYWORDS = [
    "engineer",
    "developer",
    "backend",
    "frontend",
    "full stack",
    "software",
    "data",
    "machine learning",
    "ml",
    "ai",
]


def fetch_greenhouse_jobs(board_token: str):
    logger.info("greenhouse crawl started board=%s", board_token)

    url = f"{BASE_URL}/{board_token}/jobs?content=true"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    raw_count = len(data.get("jobs", []))
    logger.info("greenhouse crawl fetched board=%s raw_count=%s", board_token, raw_count)

    jobs = []

    for i, job in enumerate(data.get("jobs", []), start=1):
        title = job.get("title", "")
        title_lower = title.lower()

        if not any(keyword in title_lower for keyword in TARGET_KEYWORDS):
            continue

        logger.debug("greenhouse crawl parsing board=%s index=%s title=%s", board_token, i, title)

        jobs.append({
            "source": "greenhouse",
            "title": title,
            "company": board_token,
            "location": job.get("location", {}).get("name") if job.get("location") else None,
            "url": job.get("absolute_url", ""),
            "description_raw": job.get("content", "") or "",
            "posted_at": None,
        })

    logger.info(
        "greenhouse crawl finished board=%s matched_count=%s skipped_count=%s",
        board_token,
        len(jobs),
        raw_count - len(jobs),
    )
    return jobs
