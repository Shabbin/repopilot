from pydantic import BaseModel


class CodeChunkOut(BaseModel):
    id: int
    file_id: int
    chunk_index: int
    content: str
    start_line: int
    end_line: int

    class Config:
        from_attributes = True