import requests

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

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
    print(f"[crawler] start board={board_token}")

    url = f"{BASE_URL}/{board_token}/jobs?content=true"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    print(f"[crawler] raw jobs count={len(data.get('jobs', []))}")

    jobs = []

    for i, job in enumerate(data.get("jobs", []), start=1):
        title = job.get("title", "")
        title_lower = title.lower()

        if not any(keyword in title_lower for keyword in TARGET_KEYWORDS):
            continue

        print(f"[crawler] parsing {i}: {title}")

        jobs.append({
            "source": "greenhouse",
            "title": title,
            "company": board_token,
            "location": job.get("location", {}).get("name") if job.get("location") else None,
            "url": job.get("absolute_url", ""),
            "description_raw": job.get("content", "") or "",
            "posted_at": None,
        })

    print(f"[crawler] finished board={board_token}")
    return jobs