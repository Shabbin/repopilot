from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    name: str
    github_url: str


class RepositoryOut(BaseModel):
    id: int
    name: str
    github_url: str
    local_path: str

    class Config:
        from_attributes = True