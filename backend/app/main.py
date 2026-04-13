from fastapi import FastAPI
from app.core.config import settings
from app.db.session import Base, engine
from app.api.repositories import router as repositories_router
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
)

app.include_router(repositories_router)


@app.get("/")
def root():
    return {"message": "RepoPilot backend is running"}