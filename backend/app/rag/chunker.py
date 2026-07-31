"""
Text Chunker — Split documents into overlapping chunks for embedding.
Uses recursive character splitting with configurable size and overlap.
Preserves paragraph/section boundaries where possible.
"""
from typing import List, Dict, Any
from app.core.config import get_settings


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
    metadata: dict = None,
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.

    Args:
        text: The full text to chunk
        chunk_size: Max characters per chunk (defaults from config)
        chunk_overlap: Overlap between consecutive chunks
        metadata: Additional metadata to attach to each chunk

    Returns:
        List of dicts with 'content', 'token_count', and 'metadata'
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.CHUNK_SIZE * 4  # Convert tokens to ~chars
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP * 4

    if not text or len(text.strip()) < 50:
        return []

    metadata = metadata or {}
    chunks = []

    # Split by paragraphs first, then sentences, then words
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]
    raw_chunks = _recursive_split(text, separators, chunk_size)

    # Apply overlap between chunks
    for i, chunk_text_content in enumerate(raw_chunks):
        chunk_content = chunk_text_content.strip()
        if len(chunk_content) < 20:
            continue

        # Add overlap from previous chunk
        if i > 0 and chunk_overlap > 0:
            prev_text = raw_chunks[i - 1]
            overlap_text = prev_text[-chunk_overlap:] if len(prev_text) > chunk_overlap else prev_text
            # Only prepend if it doesn't make the chunk too large
            if len(overlap_text) + len(chunk_content) <= chunk_size * 1.2:
                chunk_content = overlap_text.strip() + " " + chunk_content

        chunk_meta = {**metadata, "chunk_index": i}
        chunks.append({
            "content": chunk_content,
            "token_count": _estimate_tokens(chunk_content),
            "metadata": chunk_meta,
        })

    return chunks


def _recursive_split(text: str, separators: List[str], chunk_size: int) -> List[str]:
    """Recursively split text using progressively finer separators."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # Find the first separator that actually exists in the text
    best_separator = None
    for sep in separators:
        if sep in text:
            best_separator = sep
            break

    if best_separator is None:
        # No separator found — hard split by chunk_size
        result = []
        for i in range(0, len(text), chunk_size):
            piece = text[i:i + chunk_size]
            if piece.strip():
                result.append(piece)
        return result

    # Split by the separator
    parts = text.split(best_separator)
    chunks = []
    current_chunk = ""

    for part in parts:
        test_chunk = current_chunk + best_separator + part if current_chunk else part

        if len(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
            if current_chunk.strip():
                chunks.append(current_chunk)
            # If this single part is still too large, recursively split it
            if len(part) > chunk_size:
                remaining_separators = separators[separators.index(best_separator) + 1:]
                if remaining_separators:
                    sub_chunks = _recursive_split(part, remaining_separators, chunk_size)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    # Fallback: hard split
                    for i in range(0, len(part), chunk_size):
                        piece = part[i:i + chunk_size]
                        if piece.strip():
                            chunks.append(piece)
                    current_chunk = ""
            else:
                current_chunk = part

    if current_chunk.strip():
        chunks.append(current_chunk)

    return chunks


def chunk_document_sections(
    sections: List[Dict[str, Any]],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Dict[str, Any]]:
    """
    Chunk multiple document sections (from document_loader.load_document).
    Preserves section-level metadata in each chunk.
    """
    all_chunks = []
    global_index = 0

    for section in sections:
        section_chunks = chunk_text(
            text=section["content"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=section.get("metadata", {}),
        )
        for chunk in section_chunks:
            chunk["metadata"]["global_chunk_index"] = global_index
            all_chunks.append(chunk)
            global_index += 1

    return all_chunks
