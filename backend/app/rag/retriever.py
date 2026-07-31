"""
Retriever — Hybrid retrieval combining BM25 (sparse/keyword) + FAISS (dense/semantic).
Uses Reciprocal Rank Fusion to merge results from both retrievers.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from app.rag.embeddings import generate_single_embedding
from app.rag.vector_store import get_vector_store

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None
    print("[retriever] WARNING: rank_bm25 not installed. BM25 retrieval disabled.")


class HybridRetriever:
    """
    Hybrid retriever combining:
    1. FAISS vector search (semantic similarity)
    2. BM25 keyword search (lexical matching)
    3. Reciprocal Rank Fusion (RRF) to merge results

    This ensures both semantically similar AND keyword-matching chunks are retrieved.
    """

    def __init__(
        self,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
        rrf_k: int = 60,
    ):
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.rrf_k = rrf_k  # RRF constant
        self.vector_store = get_vector_store()

    def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        use_hybrid: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query text
            document_ids: Limit to specific documents
            top_k: Number of results to return
            use_hybrid: If True, combine FAISS + BM25. If False, FAISS only.

        Returns:
            List of ranked results with text, metadata, and scores
        """
        # 1. FAISS vector search
        vector_results = self._vector_search(query, document_ids, top_k=top_k * 2)

        if not use_hybrid or BM25Okapi is None or not vector_results:
            return vector_results[:top_k]

        # 2. BM25 keyword search (over the same corpus)
        corpus_texts = [r["text"] for r in vector_results]
        bm25_results = self._bm25_search(query, vector_results, top_k=top_k * 2)

        # 3. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(vector_results, bm25_results)

        return fused[:top_k]

    def _vector_search(
        self, query: str, document_ids: Optional[List[str]], top_k: int
    ) -> List[Dict[str, Any]]:
        """Dense vector search via FAISS."""
        query_embedding = generate_single_embedding(query)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            document_ids=document_ids,
            top_k=top_k,
        )
        # Add retrieval source tag
        for r in results:
            r["retrieval_source"] = "vector"
        return results

    def _bm25_search(
        self, query: str, corpus_results: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """Sparse BM25 keyword search over the same corpus as vector search."""
        if not corpus_results or BM25Okapi is None:
            return []

        # Tokenize corpus
        tokenized_corpus = [doc["text"].lower().split() for doc in corpus_results]
        tokenized_query = query.lower().split()

        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(tokenized_query)

        # Rank by BM25 score
        scored_results = []
        for i, score in enumerate(scores):
            result = {**corpus_results[i]}
            result["bm25_score"] = float(score)
            result["retrieval_source"] = "bm25"
            scored_results.append(result)

        scored_results.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_results[:top_k]

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge two ranked lists using Reciprocal Rank Fusion.
        RRF score = Σ 1 / (k + rank_i) for each ranker i
        """
        # Create a unique key for each result
        def _key(result: Dict) -> str:
            return f"{result.get('document_id', '')}_{result.get('chunk_index', '')}"

        # Compute RRF scores
        rrf_scores: Dict[str, float] = {}
        result_map: Dict[str, Dict] = {}

        for rank, result in enumerate(vector_results):
            key = _key(result)
            rrf_scores[key] = rrf_scores.get(key, 0) + self.vector_weight / (self.rrf_k + rank + 1)
            result_map[key] = result

        for rank, result in enumerate(bm25_results):
            key = _key(result)
            rrf_scores[key] = rrf_scores.get(key, 0) + self.bm25_weight / (self.rrf_k + rank + 1)
            if key not in result_map:
                result_map[key] = result

        # Sort by fused RRF score
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)

        fused_results = []
        for key in sorted_keys:
            result = result_map[key]
            result["rrf_score"] = rrf_scores[key]
            result["retrieval_source"] = "hybrid"
            fused_results.append(result)

        return fused_results


def get_retriever(**kwargs) -> HybridRetriever:
    """Factory function for HybridRetriever."""
    return HybridRetriever(**kwargs)
