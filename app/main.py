from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.routes_jobs import router as jobs_router
from app.api.routes_recommend import router as analysis_router
from app.api.routes_recommendations import router as recommendations_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Job Scout Agent")

app.include_router(jobs_router)
app.include_router(analysis_router)
app.include_router(recommendations_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Job Scout Agent is running"}