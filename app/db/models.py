from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True)
    description_raw = Column(Text, nullable=False)
    posted_at = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class JobAnalysis(Base):
    __tablename__ = "job_analysis"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)

    role = Column(String, nullable=True)
    tech_stack = Column(Text, nullable=True)
    experience_level = Column(String, nullable=True)
    language_requirement = Column(String, nullable=True)
    visa_sponsorship = Column(String, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job")