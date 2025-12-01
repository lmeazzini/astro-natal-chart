"""Hybrid search service combining dense and sparse retrieval."""

from typing import Any

from loguru import logger

from app.services.rag.bm25_service import bm25_service
from app.services.rag.qdrant_service import qdrant_service


class HybridSearchService:
    """Service for hybrid search combining BM25 and vector search."""

    def __init__(
        self,
        alpha: float = 0.5,
        normalize_scores: bool = True,
    ) -> None:
        """
        Initialize hybrid search service.

        Args:
            alpha: Weight for dense search (1-alpha for sparse)
            normalize_scores: Whether to normalize scores before fusion
        """
        self.alpha = alpha
        self.normalize_scores = normalize_scores
        self.qdrant = qdrant_service
        self.bm25 = bm25_service

    def _normalize_score(self, score: float, min_score: float, max_score: float) -> float:
        """
        Normalize score to [0, 1] range.

        Args:
            score: Original score
            min_score: Minimum score in the set
            max_score: Maximum score in the set

        Returns:
            Normalized score
        """
        if max_score == min_score:
            return 0.5  # All scores are the same

        return (score - min_score) / (max_score - min_score)

    def _reciprocal_rank_fusion(
        self,
        dense_results: list[dict[str, Any]],
        sparse_results: list[dict[str, Any]],
        k: int = 60,
    ) -> list[dict[str, Any]]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).

        Args:
            dense_results: Results from vector search
            sparse_results: Results from BM25 search
            k: RRF constant (default 60)

        Returns:
            Fused and ranked results
        """
        # Calculate RRF scores
        rrf_scores: dict[str, float] = {}

        # Process dense results
        for rank, result in enumerate(dense_results, start=1):
            doc_id = result.get("id", result.get("document_id"))
            if doc_id:
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (k + rank))

        # Process sparse results
        for rank, result in enumerate(sparse_results, start=1):
            doc_id = result.get("document_id", result.get("id"))
            if doc_id:
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (k + rank))

        # Create result mapping for metadata
        result_map: dict[str, dict[str, Any]] = {}

        for result in dense_results:
            doc_id = result.get("id", result.get("document_id"))
            if doc_id:
                result_map[doc_id] = {
                    "dense_score": result.get("score", 0),
                    "payload": result.get("payload", {}),
                }

        for result in sparse_results:
            doc_id = result.get("document_id", result.get("id"))
            if doc_id and doc_id in result_map:
                result_map[doc_id]["sparse_score"] = result.get("score", 0)
            elif doc_id:
                result_map[doc_id] = {
                    "sparse_score": result.get("score", 0),
                    "tokens": result.get("tokens", []),
                }

        # Sort by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        # Build final results
        fused_results = []
        for doc_id in sorted_ids:
            result = {
                "document_id": doc_id,
                "rrf_score": rrf_scores[doc_id],
                **result_map.get(doc_id, {}),
            }
            fused_results.append(result)

        return fused_results

    def _weighted_fusion(
        self,
        dense_results: list[dict[str, Any]],
        sparse_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Combine results using weighted score fusion.

        Args:
            dense_results: Results from vector search
            sparse_results: Results from BM25 search

        Returns:
            Fused and ranked results
        """
        # Normalize scores if requested
        if self.normalize_scores and dense_results:
            dense_scores = [r.get("score", 0) for r in dense_results]
            min_dense = min(dense_scores)
            max_dense = max(dense_scores)

            for result in dense_results:
                result["normalized_score"] = self._normalize_score(
                    result.get("score", 0), min_dense, max_dense
                )

        if self.normalize_scores and sparse_results:
            sparse_scores = [r.get("score", 0) for r in sparse_results]
            min_sparse = min(sparse_scores)
            max_sparse = max(sparse_scores)

            for result in sparse_results:
                result["normalized_score"] = self._normalize_score(
                    result.get("score", 0), min_sparse, max_sparse
                )

        # Calculate weighted scores
        weighted_scores: dict[str, float] = {}
        result_map: dict[str, dict[str, Any]] = {}

        # Process dense results
        for result in dense_results:
            doc_id = result.get("id", result.get("document_id"))
            if doc_id:
                score = (
                    result.get("normalized_score", result.get("score", 0))
                    if self.normalize_scores
                    else result.get("score", 0)
                )
                weighted_scores[doc_id] = self.alpha * score
                result_map[doc_id] = {
                    "dense_score": result.get("score", 0),
                    "payload": result.get("payload", {}),
                }

        # Process sparse results
        for result in sparse_results:
            doc_id = result.get("document_id", result.get("id"))
            if doc_id:
                score = (
                    result.get("normalized_score", result.get("score", 0))
                    if self.normalize_scores
                    else result.get("score", 0)
                )

                if doc_id in weighted_scores:
                    weighted_scores[doc_id] += (1 - self.alpha) * score
                    result_map[doc_id]["sparse_score"] = result.get("score", 0)
                else:
                    weighted_scores[doc_id] = (1 - self.alpha) * score
                    result_map[doc_id] = {
                        "sparse_score": result.get("score", 0),
                        "tokens": result.get("tokens", []),
                    }

        # Sort by weighted score
        sorted_ids = sorted(weighted_scores.keys(), key=lambda x: weighted_scores[x], reverse=True)

        # Build final results
        fused_results = []
        for doc_id in sorted_ids:
            result = {
                "document_id": doc_id,
                "hybrid_score": weighted_scores[doc_id],
                **result_map.get(doc_id, {}),
            }
            fused_results.append(result)

        return fused_results

    async def search(
        self,
        query: str,
        query_vector: list[float] | None = None,
        limit: int = 10,
        fusion_method: str = "rrf",  # "rrf" or "weighted"
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse retrieval.

        Args:
            query: Text query for BM25
            query_vector: Embedding vector for dense search
            limit: Maximum number of results
            fusion_method: Method to combine results ("rrf" or "weighted")
            filters: Optional filters for vector search

        Returns:
            Combined and ranked search results
        """
        results = []

        # Perform dense search if vector provided
        dense_results = []
        if query_vector and self.qdrant.enabled:
            dense_results = await self.qdrant.search(
                query_vector=query_vector,
                limit=limit * 2,  # Get more results for fusion
                filters=filters,
            )
            logger.debug(f"Dense search returned {len(dense_results)} results")

        # Perform sparse search
        sparse_results = []
        if query:
            sparse_results = self.bm25.search(
                query=query,
                limit=limit * 2,  # Get more results for fusion
            )
            logger.debug(f"Sparse search returned {len(sparse_results)} results")

        # If only one type of results available, return them
        if not dense_results and sparse_results:
            return sparse_results[:limit]
        elif dense_results and not sparse_results:
            return dense_results[:limit]
        elif not dense_results and not sparse_results:
            return []

        # Combine results using selected fusion method
        if fusion_method == "rrf":
            results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        else:  # weighted
            results = self._weighted_fusion(dense_results, sparse_results)

        # Limit final results
        results = results[:limit]

        logger.info(
            f"Hybrid search ({fusion_method}) returned {len(results)} results "
            f"(dense: {len(dense_results)}, sparse: {len(sparse_results)})"
        )

        return results

    def set_alpha(self, alpha: float) -> None:
        """
        Set the alpha parameter for weighted fusion.

        Args:
            alpha: Weight for dense search (0-1)
        """
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        self.alpha = alpha
        logger.info(f"Set hybrid search alpha to {alpha}")

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the hybrid search system.

        Returns:
            Dictionary with search statistics
        """
        stats = {
            "alpha": self.alpha,
            "normalize_scores": self.normalize_scores,
            "qdrant_enabled": self.qdrant.enabled,
            "bm25_stats": self.bm25.get_index_stats(),
        }

        # Add Qdrant stats if available
        qdrant_info = None
        if self.qdrant.enabled:
            import asyncio

            loop = asyncio.get_event_loop()
            qdrant_info = loop.run_until_complete(self.qdrant.get_collection_info())

        if qdrant_info:
            stats["qdrant_stats"] = qdrant_info

        return stats


# Singleton instance
hybrid_search_service = HybridSearchService()
