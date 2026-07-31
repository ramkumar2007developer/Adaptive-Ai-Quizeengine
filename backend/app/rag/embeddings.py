"""
Embeddings Module — Generate dense vector embeddings using Sentence Transformers.
Runs locally (no API calls needed). Model: all-MiniLM-L6-v2 (384 dimensions).
"""
import numpy as np
from typing import List
from functools import lru_cache
from app.core.config import get_settings


_model_instance = None


def _get_model():
    """Lazy-load the sentence transformer model (singleton)."""
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer
        settings = get_settings()
        print(f"[embeddings] Loading model: {settings.EMBEDDING_MODEL}")
        _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"[embeddings] Model loaded successfully. Dimension: {_model_instance.get_sentence_embedding_dimension()}")
    return _model_instance


def generate_embeddings(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed
        batch_size: Batch size for encoding (larger = faster but more memory)

    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.array([])

    model = _get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 100,
        normalize_embeddings=True,  # L2 normalize for cosine similarity via dot product
    )
    return np.array(embeddings, dtype=np.float32)


def generate_single_embedding(text: str) -> np.ndarray:
    """Generate embedding for a single text query."""
    model = _get_model()
    embedding = model.encode(
        [text],
        normalize_embeddings=True,
    )
    return np.array(embedding[0], dtype=np.float32)


def get_embedding_dimension() -> int:
    """Get the dimension of the embedding model."""
    model = _get_model()
    return model.get_sentence_embedding_dimension()
