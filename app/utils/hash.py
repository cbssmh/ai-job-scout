import hashlib
import json


def generate_job_content_hash(
    *,
    title: str,
    company: str,
    location: str | None,
    description_raw: str,
) -> str:
    payload = {
        "title": title.strip(),
        "company": company.strip(),
        "location": (location or "").strip(),
        "description_raw": description_raw.strip(),
    }
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
