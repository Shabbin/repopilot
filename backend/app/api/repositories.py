from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.repository import Repository
from app.models.file import RepoFile
from app.schemas.repository import RepositoryCreate, RepositoryOut
from app.schemas.file import RepoFileOut
from app.services.repo_service import clone_repository
from app.services.file_service import scan_repository_files

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/", response_model=RepositoryOut)
def create_repository(payload: RepositoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Repository).filter(Repository.github_url == payload.github_url).first()
    if existing:
        return existing

    local_path = clone_repository(payload.name, payload.github_url)

    repo = Repository(
        name=payload.name,
        github_url=payload.github_url,
        local_path=local_path,
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    files = scan_repository_files(local_path)
    for file in files:
        db.add(
            RepoFile(
                repository_id=repo.id,
                path=file["path"],
                file_type=file["file_type"],
            )
        )

    db.commit()
    return repo


@router.get("/", response_model=list[RepositoryOut])
def list_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).all()


@router.get("/{repo_id}/files", response_model=list[RepoFileOut])
def list_repository_files(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return db.query(RepoFile).filter(RepoFile.repository_id == repo_id).all()