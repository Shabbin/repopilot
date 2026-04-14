from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    limit: int = 5
    code_only: bool = True
    exclude_docs: bool = True
    exclude_examples: bool = True


class AskContextItem(BaseModel):
    file_path: str
    file_type: str | None = None
    chunk_index: int
    start_line: int
    end_line: int
    content: str


class AskResponse(BaseModel):
    question: str
    repository_id: int
    answer: str
    contexts: list[AskContextItem]