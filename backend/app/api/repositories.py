import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.code_chunk import CodeChunk
from app.models.file import RepoFile
from app.models.repository import Repository
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.code_chunk import CodeChunkOut
from app.schemas.file import RepoFileOut
from app.schemas.repository import RepositoryCreate, RepositoryOut
from app.schemas.search import ChunkSearchResult
from app.services.chunk_service import (
    chunk_lines,
    is_chunkable_file,
    read_file_content,
)
from app.services.file_service import scan_repository_files
from app.services.repo_service import clone_repository

router = APIRouter(prefix="/repositories", tags=["repositories"])


def expand_question_to_queries(question: str) -> list[str]:
    raw = question.strip()

    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw)
    stopwords = {
        "how", "does", "do", "is", "are", "the", "a", "an", "what",
        "where", "when", "why", "which", "who", "and", "or", "to",
        "in", "of", "for", "with", "on"
    }

    keywords = [
        token for token in tokens
        if token.lower() not in stopwords and len(token) > 2
    ]

    prioritized = []

    lowered = {k.lower() for k in keywords}

    if "router" in lowered or "routers" in lowered:
        prioritized.extend(["include_router", "APIRouter", "router"])

    if "fastapi" in lowered:
        prioritized.extend(["FastAPI(", "class FastAPI"])

    prioritized.extend(keywords)
    prioritized.append(raw)

    seen = set()
    unique_queries = []
    for q in prioritized:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)

    return unique_queries[:8]

@router.post("/", response_model=RepositoryOut)
def create_repository(payload: RepositoryCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Repository)
        .filter(Repository.github_url == payload.github_url)
        .first()
    )
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


@router.post("/{repo_id}/ingest-chunks")
def ingest_repository_chunks(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    files = db.query(RepoFile).filter(RepoFile.repository_id == repo_id).all()
    inserted_chunks = 0

    for file in files:
        if not is_chunkable_file(file.path):
            continue

        existing_chunk = (
            db.query(CodeChunk).filter(CodeChunk.file_id == file.id).first()
        )
        if existing_chunk:
            continue

        full_path = Path(repo.local_path) / file.path
        lines = read_file_content(str(full_path))
        chunks = chunk_lines(lines)

        for chunk in chunks:
            db.add(
                CodeChunk(
                    file_id=file.id,
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                )
            )
            inserted_chunks += 1

    db.commit()
    return {
        "message": "Chunk ingestion complete",
        "repository_id": repo_id,
        "inserted_chunks": inserted_chunks,
    }


@router.get("/{repo_id}/chunks", response_model=list[CodeChunkOut])
def list_repository_chunks(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return (
        db.query(CodeChunk)
        .join(RepoFile, CodeChunk.file_id == RepoFile.id)
        .filter(RepoFile.repository_id == repo_id)
        .limit(200)
        .all()
    )


@router.get("/{repo_id}/search", response_model=list[ChunkSearchResult])
def search_repository_chunks(
    repo_id: int,
    q: str,
    code_only: bool = False,
    exclude_docs: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    preferred_types = [
        "py",
        "js",
        "ts",
        "tsx",
        "jsx",
        "java",
        "go",
        "rs",
        "cpp",
        "c",
        "cs",
    ]
    normalized_path = func.replace(RepoFile.path, "\\", "/")
    limit = max(1, min(limit, 100))

    query = (
        db.query(
            CodeChunk.id,
            CodeChunk.file_id,
            RepoFile.path.label("file_path"),
            RepoFile.file_type,
            CodeChunk.chunk_index,
            CodeChunk.content,
            CodeChunk.start_line,
            CodeChunk.end_line,
        )
        .join(RepoFile, CodeChunk.file_id == RepoFile.id)
        .filter(RepoFile.repository_id == repo_id)
        .filter(CodeChunk.content.ilike(f"%{q}%"))
    )

    if code_only:
        query = query.filter(RepoFile.file_type.in_(preferred_types))

    if exclude_docs:
        query = query.filter(~normalized_path.like("docs/%"))
        query = query.filter(~normalized_path.like("docs_src/%"))

    results = (
        query.order_by(
            RepoFile.file_type.in_(preferred_types).desc(),
            RepoFile.path.asc(),
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "file_id": row.file_id,
            "file_path": row.file_path,
            "file_type": row.file_type,
            "chunk_index": row.chunk_index,
            "content": row.content,
            "start_line": row.start_line,
            "end_line": row.end_line,
        }
        for row in results
    ]


def retrieve_relevant_chunks(
    db: Session,
    repo_id: int,
    query_text: str,
    limit: int = 5,
    code_only: bool = True,
    exclude_docs: bool = True,
):
    preferred_types = [
        "py",
        "js",
        "ts",
        "tsx",
        "jsx",
        "java",
        "go",
        "rs",
        "cpp",
        "c",
        "cs",
    ]
    normalized_path = func.replace(RepoFile.path, "\\", "/")
    limit = max(1, min(limit, 20))

    search_queries = expand_question_to_queries(query_text)

    collected = []
    seen_keys = set()

    for search_q in search_queries:
        query = (
            db.query(
                CodeChunk.id,
                CodeChunk.file_id,
                RepoFile.path.label("file_path"),
                RepoFile.file_type,
                CodeChunk.chunk_index,
                CodeChunk.content,
                CodeChunk.start_line,
                CodeChunk.end_line,
            )
            .join(RepoFile, CodeChunk.file_id == RepoFile.id)
            .filter(RepoFile.repository_id == repo_id)
            .filter(CodeChunk.content.ilike(f"%{search_q}%"))
        )

        if code_only:
            query = query.filter(RepoFile.file_type.in_(preferred_types))

        if exclude_docs:
            query = query.filter(~normalized_path.like("docs/%"))
            query = query.filter(~normalized_path.like("docs_src/%"))

        results = (
            query.order_by(
                RepoFile.file_type.in_(preferred_types).desc(),
                RepoFile.path.asc(),
            )
            .limit(limit)
            .all()
        )

        for row in results:
            key = (row.file_path, row.chunk_index)
            if key in seen_keys:
                continue

            seen_keys.add(key)
            collected.append(
                {
                    "file_path": row.file_path,
                    "file_type": row.file_type,
                    "chunk_index": row.chunk_index,
                    "start_line": row.start_line,
                    "end_line": row.end_line,
                    "content": row.content,
                }
            )

            if len(collected) >= limit:
                return collected

    return collected


@router.post("/{repo_id}/ask", response_model=AskResponse)
def ask_repository(repo_id: int, payload: AskRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    contexts = retrieve_relevant_chunks(
        db=db,
        repo_id=repo_id,
        query_text=payload.question,
        limit=payload.limit,
        code_only=payload.code_only,
        exclude_docs=payload.exclude_docs,
    )

    if not contexts:
        answer = "No relevant code found in the repository."
    else:
        files = list({c["file_path"] for c in contexts[:3]})
        answer = (
            f"Found relevant code in: {', '.join(files)}. "
            f"Top matches suggest this relates to '{payload.question}'."
        )

    return {
        "question": payload.question,
        "repository_id": repo_id,
        "answer": answer,
        "contexts": contexts,
    }