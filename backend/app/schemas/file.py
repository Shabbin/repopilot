from pydantic import BaseModel


class RepoFileOut(BaseModel):
    id: int
    repository_id: int
    path: str
    file_type: str | None = None

    class Config:
        from_attributes = True