from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.db.session import Base


class RepoFile(Base):
    __tablename__ = "repo_files"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())