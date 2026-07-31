from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid

from app.core.database import get_db
from app.core.config import get_settings
from app.rag.rag_pipeline import process_document, delete_document_index
from app.models.schemas.document_schemas import (
    UploadDocumentResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentStatusResponse
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/documents", tags=["Documents"])


async def bg_process_document(file_path: str, document_id: str, db: AsyncSession):
    """Background task to run the RAG pipeline on an uploaded file."""
    repo = DocumentRepository(db)
    try:
        # Update status to PROCESSING
        await repo.update_document_status(document_id, "PROCESSING")
        
        # Run pipeline
        result = await process_document(file_path=file_path, document_id=document_id)
        
        # Update status to READY
        await repo.update_document_status(
            document_id=document_id,
            status="READY",
            chunk_count=result["chunks_created"],
            total_tokens=result["total_tokens"]
        )
    except Exception as e:
        print(f"[documents] Pipeline error for {document_id}: {e}")
        # Update status to FAILED
        await repo.update_document_status(
            document_id=document_id,
            status="FAILED",
            error_message=str(e)
        )

@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    subject: str = Form("General Knowledge"),
    user_id: Optional[str] = Form("default_user"),
    chapter: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    settings = get_settings()
    target_user_id = user_id or "default_user"

    # Auto-ensure user exists in DB
    user_repo = UserRepository(db)
    await user_repo.ensure_user_exists(target_user_id)
    
    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = [".pdf", ".docx", ".pptx", ".txt"]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Must be one of {allowed_exts}")

    # 2. Create DB Record
    repo = DocumentRepository(db)
    doc = await repo.create_document(
        user_id=target_user_id,
        filename=file.filename,
        file_type=ext.replace(".", "").upper(),
        subject=subject,
        chapter=chapter,
        status="UPLOADED"
    )

    # 3. Save file to disk
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc.id}{ext}")
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update size
        doc.file_size_bytes = len(content)
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    # 4. Trigger Background Processing
    background_tasks.add_task(bg_process_document, file_path, doc.id, db)

    return UploadDocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        subject=doc.subject,
        chapter=doc.chapter
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str, db: AsyncSession = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return DocumentStatusResponse(
        document_id=doc.id,
        status=doc.status,
        chunk_count=doc.chunk_count,
        total_tokens=doc.total_tokens,
        error_message=doc.error_message
    )

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = await repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from FAISS
    delete_document_index(document_id)
    
    # Delete file
    settings = get_settings()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.{doc.file_type.lower()}")
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # Delete from DB
    await repo.delete_document(document_id)
    
    return {"success": True, "message": "Document deleted"}
