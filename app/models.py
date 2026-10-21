from datetime import datetime

from pydantic import BaseModel


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    text_length: int
    chunks: int


class SourceInfo(BaseModel):
    document_id: str
    filename: str
    page: int | None = None