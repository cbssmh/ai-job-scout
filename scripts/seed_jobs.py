from app.db.database import SessionLocal, Base, engine
from app.services.job_service import create_job, get_jobs
from app.db.schemas import JobCreate

sample_jobs = [
    JobCreate(
        source="sample_board",
        title="Backend Engineer",
        company="Tech GmbH",
        location="Berlin, Germany",
        url="https://example.com/jobs/backend-engineer",
        description_raw="""
We are looking for a Backend Engineer with experience in Python, FastAPI, Docker, and AWS.
3+ years of backend development experience required.
English working proficiency is required.
Visa sponsorship may be available for qualified candidates.
        """,
        posted_at="2026-03-13"
    ),
    JobCreate(
        source="sample_board",
        title="Data Engineer",
        company="DataWorks",
        location="Hamburg, Germany",
        url="https://example.com/jobs/data-engineer",
        description_raw="""
Seeking a Data Engineer skilled in Python, SQL, Airflow, and PostgreSQL.
Experience with cloud environments is preferred.
English is used internally. Relocation support possible.
        """,
        posted_at="2026-03-13"
    )
]

def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for job in sample_jobs:
            create_job(db, job)

        jobs = get_jobs(db)
        print(f"Inserted jobs count: {len(jobs)}")
        for job in jobs:
            print(job.id, job.title, job.company)
    finally:
        db.close()


if __name__ == "__main__":
    main()