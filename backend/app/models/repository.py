from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.session import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    github_url = Column(String, nullable=False, unique=True)
    local_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())