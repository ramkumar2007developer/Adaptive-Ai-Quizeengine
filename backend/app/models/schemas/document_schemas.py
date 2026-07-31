"""
Pydantic Schemas — Request/Response models for Document endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UploadDocumentResponse(BaseModel):
    success: bool = True
    document_id: str
    filename: str
    file_type: str
    subject: str
    chapter: Optional[str] = None
    status: str = "UPLOADED"
    message: str = "Document uploaded successfully. Processing will begin shortly."


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    subject: str
    chapter: Optional[str] = None
    status: str
    chunk_count: int
    total_tokens: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    success: bool = True
    total_documents: int
    documents: List[DocumentResponse]


class DocumentStatusResponse(BaseModel):
    success: bool = True
    document_id: str
    status: str
    chunk_count: int
    total_tokens: int
    error_message: Optional[str] = None


class ProcessDocumentRequest(BaseModel):
    document_id: str
    subject: str
    chapter: Optional[str] = None
