"""Qdrant vector database service for semantic search."""

from typing import Any

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings


class QdrantService:
    """Service for managing vector operations with Qdrant."""

    def __init__(self) -> None:
        """Initialize Qdrant client."""
        self.client: QdrantClient | None = None
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.QDRANT_VECTOR_SIZE
        self.enabled = False
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Qdrant client with proper configuration."""
        try:
            # Get Qdrant URL from settings
            qdrant_url = settings.QDRANT_URL

            # Initialize client
            self.client = QdrantClient(
                url=qdrant_url,
                timeout=30,
            )

            # Test connection
            self.client.get_collections()
            self.enabled = True

            # Ensure collection exists
            self._ensure_collection()

            logger.info(f"Qdrant service initialized successfully at {qdrant_url}")

        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant: {e}. Running in degraded mode.")
            self.enabled = False

    def _ensure_collection(self) -> None:
        """Ensure the collection exists with proper configuration."""
        if not self.client or not self.enabled:
            return

        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # Create collection with hybrid search configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.vector_size,
                        distance=qmodels.Distance.COSINE,
                    ),
                    on_disk_payload=True,  # Store payload on disk for large documents
                )

                # Create payload indexes for filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_type",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )

                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="tradition",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )

                logger.info(f"Created Qdrant collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            self.enabled = False

    async def upsert_vectors(
        self,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> bool:
        """
        Insert or update vectors in Qdrant.

        Args:
            vectors: List of embedding vectors
            payloads: List of metadata dictionaries
            ids: Optional list of point IDs

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            logger.warning("Qdrant not available, skipping vector upsert")
            return False

        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(i) for i in range(len(vectors))]

            # Create points
            points = [
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                for point_id, vector, payload in zip(ids, vectors, payloads, strict=False)
            ]

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,  # Wait for operation to complete
            )

            logger.info(f"Successfully upserted {len(vectors)} vectors to Qdrant")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            return False

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Optional filters for metadata

        Returns:
            List of search results with scores and payloads
        """
        if not self.enabled or not self.client:
            logger.warning("Qdrant not available, returning empty results")
            return []

        try:
            # Build filter conditions
            filter_conditions = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Match any value in list
                        must_conditions.append(
                            qmodels.FieldCondition(
                                key=key,
                                match=qmodels.MatchAny(any=value),
                            )
                        )
                    else:
                        # Exact match
                        must_conditions.append(
                            qmodels.FieldCondition(
                                key=key,
                                match=qmodels.MatchValue(value=value),
                            )
                        )

                if must_conditions:
                    filter_conditions = qmodels.Filter(must=must_conditions)

            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_conditions,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,  # Don't return vectors to save bandwidth
            )

            # Format results
            results = []
            for point in search_result:
                result = {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload or {},
                }
                results.append(result)

            logger.debug(f"Found {len(results)} similar vectors in Qdrant")
            return results

        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            return []

    async def delete_vectors(self, ids: list[str]) -> bool:
        """
        Delete vectors from Qdrant by IDs.

        Args:
            ids: List of point IDs to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            logger.warning("Qdrant not available, skipping vector deletion")
            return False

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.PointIdsList(points=ids),
                wait=True,
            )

            logger.info(f"Successfully deleted {len(ids)} vectors from Qdrant")
            return True

        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False

    async def get_collection_info(self) -> dict[str, Any] | None:
        """
        Get information about the collection.

        Returns:
            Collection information or None if unavailable
        """
        if not self.enabled or not self.client:
            return None

        try:
            info = self.client.get_collection(self.collection_name)
            vectors_config = info.config.params.vectors
            # Handle both single vector config and named vectors
            if isinstance(vectors_config, dict):
                # Named vectors - get first one
                first_config = next(iter(vectors_config.values()), None)
                vector_size = first_config.size if first_config else 0
                distance = str(first_config.distance) if first_config else "unknown"
            elif vectors_config is not None:
                vector_size = vectors_config.size
                distance = str(vectors_config.distance)
            else:
                vector_size = 0
                distance = "unknown"

            return {
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
                "config": {
                    "vector_size": vector_size,
                    "distance": distance,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

    def close(self) -> None:
        """Close Qdrant client connection."""
        if self.client:
            self.client.close()
            logger.info("Qdrant client connection closed")


# Singleton instance
qdrant_service = QdrantService()
