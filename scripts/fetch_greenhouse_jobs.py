import logging

from app.db import models
from app.db.database import SessionLocal, Base, engine
from app.domain.job_lifecycle import (
    UPSERT_CREATED,
    UPSERT_UNCHANGED,
    UPSERT_UPDATED,
)
from app.db.schemas import JobCreate
from app.crawler.greenhouse import fetch_greenhouse_jobs
from app.logging_config import configure_logging
from app.services.job_service import upsert_job

BOARD_TOKENS = ["stripe"]
logger = logging.getLogger(__name__)


def main():
    configure_logging()
    logger.info("job ingestion started boards=%s", BOARD_TOKENS)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for token in BOARD_TOKENS:
            logger.info("job ingestion fetching board=%s", token)

            jobs = fetch_greenhouse_jobs(token)
            logger.info("job ingestion fetched board=%s matched_count=%s", token, len(jobs))

            created = 0
            unchanged = 0
            updated = 0
            failed = 0

            for job in jobs:
                job_data = JobCreate(**job)

                try:
                    result = upsert_job(db, job_data)
                    if result.result == UPSERT_CREATED:
                        created += 1
                    elif result.result == UPSERT_UNCHANGED:
                        unchanged += 1
                    elif result.result == UPSERT_UPDATED:
                        updated += 1
                except Exception as e:
                    db.rollback()
                    failed += 1
                    logger.exception(
                        "job ingestion failed board=%s url=%s error_type=%s",
                        token,
                        job["url"],
                        type(e).__name__,
                    )

            logger.info(
                "job ingestion completed board=%s fetched=%s created=%s unchanged=%s updated=%s failed=%s",
                token,
                len(jobs),
                created,
                unchanged,
                updated,
                failed,
            )

        logger.info("job ingestion finished")

    finally:
        db.close()


if __name__ == "__main__":
    main()
