"""
Vector Store — FAISS index management for dense vector search.
Supports per-document and global indices with disk persistence.
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import get_settings

try:
    import faiss
except ImportError:
    faiss = None
    print("[vector_store] WARNING: faiss-cpu not installed. Vector search will not work.")


class FAISSVectorStore:
    """
    FAISS-based vector store with metadata tracking and disk persistence.
    Each document gets its own index, and a global index spans all documents.
    """

    def __init__(self, store_path: str = None):
        settings = get_settings()
        self.store_path = store_path or settings.VECTOR_STORE_PATH
        os.makedirs(self.store_path, exist_ok=True)

        # In-memory indices: document_id -> faiss.Index
        self._indices: Dict[str, Any] = {}
        # Metadata mapping: document_id -> list of chunk metadata dicts
        self._metadata: Dict[str, List[Dict[str, Any]]] = {}
        # Chunk texts: document_id -> list of chunk text strings
        self._texts: Dict[str, List[str]] = {}

    def add_document(
        self,
        document_id: str,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: List[Dict[str, Any]],
    ) -> int:
        """
        Add a document's chunk embeddings to the vector store.

        Args:
            document_id: Unique document identifier
            embeddings: numpy array of shape (num_chunks, embedding_dim)
            texts: List of chunk text strings
            metadata: List of chunk metadata dicts

        Returns:
            Number of vectors added
        """
        if faiss is None:
            raise RuntimeError("faiss-cpu is not installed")

        if len(embeddings) == 0:
            return 0

        dim = embeddings.shape[1]

        # Create a flat L2 index (exact search, suitable for <100k vectors)
        index = faiss.IndexFlatIP(dim)  # Inner Product (cosine sim with normalized vectors)
        index.add(embeddings.astype(np.float32))

        self._indices[document_id] = index
        self._metadata[document_id] = metadata
        self._texts[document_id] = texts

        # Persist to disk
        self._save_document_index(document_id)

        print(f"[vector_store] Added {len(embeddings)} vectors for document {document_id}")
        return len(embeddings)

    def search(
        self,
        query_embedding: np.ndarray,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search across one or more document indices.

        Args:
            query_embedding: Query vector of shape (embedding_dim,)
            document_ids: Limit search to these documents. None = search all.
            top_k: Number of results to return

        Returns:
            List of dicts with 'text', 'metadata', 'score', 'document_id'
        """
        if faiss is None:
            raise RuntimeError("faiss-cpu is not installed")

        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        target_doc_ids = document_ids or list(self._indices.keys())
        all_results = []

        for doc_id in target_doc_ids:
            if doc_id not in self._indices:
                # Try loading from disk
                self._load_document_index(doc_id)
                if doc_id not in self._indices:
                    continue

            index = self._indices[doc_id]
            n_vectors = index.ntotal
            k = min(top_k, n_vectors)

            if k == 0:
                continue

            scores, indices = index.search(query_embedding.astype(np.float32), k)

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                result = {
                    "text": self._texts[doc_id][idx],
                    "metadata": self._metadata[doc_id][idx],
                    "score": float(score),
                    "document_id": doc_id,
                    "chunk_index": idx,
                }
                all_results.append(result)

        # Sort by score descending and return top_k
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def delete_document(self, document_id: str):
        """Remove a document's index from memory and disk."""
        self._indices.pop(document_id, None)
        self._metadata.pop(document_id, None)
        self._texts.pop(document_id, None)

        # Remove from disk
        index_path = os.path.join(self.store_path, f"{document_id}.index")
        meta_path = os.path.join(self.store_path, f"{document_id}.meta.json")
        for path in [index_path, meta_path]:
            if os.path.exists(path):
                os.remove(path)

        print(f"[vector_store] Deleted index for document {document_id}")

    def has_document(self, document_id: str) -> bool:
        """Check if a document's index exists (in memory or on disk)."""
        if document_id in self._indices:
            return True
        index_path = os.path.join(self.store_path, f"{document_id}.index")
        return os.path.exists(index_path)

    def get_document_count(self, document_id: str) -> int:
        """Get number of vectors for a document."""
        if document_id in self._indices:
            return self._indices[document_id].ntotal
        return 0

    def _save_document_index(self, document_id: str):
        """Persist a document's FAISS index and metadata to disk."""
        if document_id not in self._indices:
            return

        index_path = os.path.join(self.store_path, f"{document_id}.index")
        meta_path = os.path.join(self.store_path, f"{document_id}.meta.json")

        faiss.write_index(self._indices[document_id], index_path)

        meta_data = {
            "metadata": self._metadata.get(document_id, []),
            "texts": self._texts.get(document_id, []),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

    def _load_document_index(self, document_id: str):
        """Load a document's FAISS index and metadata from disk."""
        index_path = os.path.join(self.store_path, f"{document_id}.index")
        meta_path = os.path.join(self.store_path, f"{document_id}.meta.json")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return

        self._indices[document_id] = faiss.read_index(index_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

        self._metadata[document_id] = meta_data.get("metadata", [])
        self._texts[document_id] = meta_data.get("texts", [])

    def load_all(self):
        """Load all persisted document indices from disk."""
        if not os.path.exists(self.store_path):
            return

        for filename in os.listdir(self.store_path):
            if filename.endswith(".index"):
                doc_id = filename.replace(".index", "")
                self._load_document_index(doc_id)

        print(f"[vector_store] Loaded {len(self._indices)} document indices from disk")


# --- Module-level singleton ---
_vector_store_instance: Optional[FAISSVectorStore] = None


def get_vector_store() -> FAISSVectorStore:
    """Get or create the global vector store singleton."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = FAISSVectorStore()
        _vector_store_instance.load_all()
    return _vector_store_instance
