from pydantic import BaseModel


class ChunkSearchResult(BaseModel):
    id: int
    file_id: int
    file_path: str
    file_type: str | None = None
    chunk_index: int
    content: str
    start_line: int
    end_line: int