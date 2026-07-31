"""
RAG Pipeline — End-to-end orchestration:
Document Upload → Text Extraction → Chunking → Embedding → FAISS Storage
Query → Hybrid Retrieval → Context Ranking → Prompt Template → LLM → Structured JSON
"""
import os
import uuid
from typing import List, Dict, Any, Optional

from app.core.config import get_settings
from app.rag.document_loader import load_document
from app.rag.chunker import chunk_document_sections
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import get_vector_store
from app.rag.retriever import get_retriever


# ============================================================
# Document Processing Pipeline
# ============================================================

async def process_document(
    file_path: str,
    document_id: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> Dict[str, Any]:
    """
    Full document processing pipeline:
    1. Extract text from file
    2. Chunk text into overlapping segments
    3. Generate embeddings for each chunk
    4. Store in FAISS vector database

    Args:
        file_path: Path to the uploaded document file
        document_id: Unique document ID for indexing
        chunk_size: Override chunk size (chars)
        chunk_overlap: Override chunk overlap (chars)

    Returns:
        Dict with processing results (chunk_count, total_tokens, etc.)
    """
    print(f"[rag_pipeline] Processing document: {document_id} from {file_path}")

    # Step 1: Extract text
    sections = load_document(file_path)
    print(f"[rag_pipeline] Extracted {len(sections)} sections")

    # Step 2: Chunk
    chunks = chunk_document_sections(sections, chunk_size, chunk_overlap)
    print(f"[rag_pipeline] Created {len(chunks)} chunks")

    if not chunks:
        raise ValueError("No meaningful chunks could be created from the document")

    # Step 3: Generate embeddings
    chunk_texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings(chunk_texts)
    print(f"[rag_pipeline] Generated embeddings: shape {embeddings.shape}")

    # Step 4: Store in FAISS
    chunk_metadata = []
    for i, chunk in enumerate(chunks):
        meta = {
            **chunk.get("metadata", {}),
            "chunk_id": str(uuid.uuid4()),
            "document_id": document_id,
            "chunk_index": i,
            "token_count": chunk.get("token_count", 0),
        }
        chunk_metadata.append(meta)

    vector_store = get_vector_store()
    num_added = vector_store.add_document(
        document_id=document_id,
        embeddings=embeddings,
        texts=chunk_texts,
        metadata=chunk_metadata,
    )

    total_tokens = sum(c.get("token_count", 0) for c in chunks)

    result = {
        "document_id": document_id,
        "sections_extracted": len(sections),
        "chunks_created": len(chunks),
        "vectors_stored": num_added,
        "total_tokens": total_tokens,
        "embedding_dimension": embeddings.shape[1] if len(embeddings.shape) > 1 else 0,
        "chunk_texts": chunk_texts,  # Return for DB storage
        "chunk_metadata": chunk_metadata,
    }

    print(f"[rag_pipeline] Document {document_id} processed successfully: {num_added} vectors")
    return result


# ============================================================
# Query & Retrieval Pipeline
# ============================================================

def retrieve_context(
    query: str,
    document_ids: Optional[List[str]] = None,
    top_k: int = 5,
    use_hybrid: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context chunks for a query.

    Args:
        query: The search query (e.g., topic + difficulty description)
        document_ids: Limit to specific documents
        top_k: Number of chunks to retrieve
        use_hybrid: Use hybrid (FAISS + BM25) retrieval

    Returns:
        List of retrieved chunks with text, metadata, and scores
    """
    retriever = get_retriever()
    results = retriever.retrieve(
        query=query,
        document_ids=document_ids,
        top_k=top_k,
        use_hybrid=use_hybrid,
    )
    return results


def format_context_for_prompt(
    retrieved_chunks: List[Dict[str, Any]],
    max_context_tokens: int = 3000,
) -> str:
    """
    Format retrieved chunks into a single context string for the LLM prompt.
    Respects token limits and adds source attribution.
    """
    if not retrieved_chunks:
        return ""

    context_parts = []
    current_tokens = 0

    for i, chunk in enumerate(retrieved_chunks):
        text = chunk["text"]
        estimated_tokens = len(text) // 4

        if current_tokens + estimated_tokens > max_context_tokens:
            break

        # Add source attribution
        source_info = ""
        meta = chunk.get("metadata", {})
        if "page_number" in meta:
            source_info = f" (Page {meta['page_number']})"
        elif "slide_number" in meta:
            source_info = f" (Slide {meta['slide_number']})"
        elif "section" in meta:
            source_info = f" (Section: {meta['section']})"

        context_parts.append(f"[Context {i+1}{source_info}]:\n{text}")
        current_tokens += estimated_tokens

    return "\n\n---\n\n".join(context_parts)


def delete_document_index(document_id: str):
    """Remove a document's vectors from the store."""
    vector_store = get_vector_store()
    vector_store.delete_document(document_id)
