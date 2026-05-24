from app.db import models
from app.db.database import SessionLocal, Base, engine
from app.services.job_service import create_job
from app.db.schemas import JobCreate
from app.crawler.greenhouse import fetch_greenhouse_jobs

BOARD_TOKENS = ["stripe"]


def main():
    print("fetch_greenhouse_jobs.py started")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        for token in BOARD_TOKENS:
            print(f"Fetching board: {token}")

            jobs = fetch_greenhouse_jobs(token)
            print(f"Fetched {len(jobs)} jobs from {token}")

            inserted = 0

            for job in jobs:
                job_data = JobCreate(**job)

                try:
                    create_job(db, job_data)
                    inserted += 1
                except Exception as e:
                    db.rollback()
                    print(f"Skipped duplicate or failed insert: {job['url']} | {type(e).__name__}")

            print(f"Inserted {inserted} jobs from {token}")

        print("Greenhouse jobs fetched successfully")

    finally:
        db.close()


if __name__ == "__main__":
    main()