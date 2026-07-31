"""
Document Repository — Data access layer for Document and DocumentChunk entities.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Document ---
    async def create_document(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_document(self, document_id: str) -> Optional[Document]:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def get_user_documents(self, user_id: str) -> List[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_document_status(
        self, document_id: str, status: str,
        chunk_count: int = 0, total_tokens: int = 0,
        error_message: str = None
    ) -> Optional[Document]:
        doc = await self.get_document(document_id)
        if doc:
            doc.status = status
            doc.chunk_count = chunk_count
            doc.total_tokens = total_tokens
            if error_message:
                doc.error_message = error_message
            await self.db.flush()
        return doc

    async def delete_document(self, document_id: str) -> bool:
        doc = await self.get_document(document_id)
        if doc:
            await self.db.delete(doc)
            await self.db.flush()
            return True
        return False

    # --- Chunks ---
    async def create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.db.add_all(chunks)
        await self.db.flush()
        return chunks

    async def get_chunks_for_document(self, document_id: str) -> List[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        if not chunk_ids:
            return []
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        )
        return list(result.scalars().all())

    async def get_ready_documents_for_subject(self, user_id: str, subject: str) -> List[Document]:
        result = await self.db.execute(
            select(Document).where(
                Document.user_id == user_id,
                Document.subject == subject,
                Document.status == "READY"
            )
        )
        return list(result.scalars().all())
