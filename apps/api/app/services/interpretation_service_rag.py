"""
Enhanced interpretation service with RAG (Retrieval-Augmented Generation) support.

This service extends the base interpretation service by adding the ability to
retrieve relevant astrological knowledge from a vector database before generating
interpretations, resulting in more accurate and contextually grounded responses.
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID

from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.interpretation_service import InterpretationService
from app.services.rag import hybrid_search_service


class InterpretationServiceRAG(InterpretationService):
    """Enhanced interpretation service with RAG support."""

    def __init__(self, db: AsyncSession, use_cache: bool = True, use_rag: bool = True):
        """
        Initialize RAG-enhanced interpretation service.

        Args:
            db: Database session
            use_cache: Whether to use interpretation cache
            use_rag: Whether to use RAG for context retrieval
        """
        super().__init__(db, use_cache)
        self.use_rag = use_rag
        self.rag_context_limit = 3  # Number of relevant documents to retrieve

    async def _get_embedding(self, text: str) -> list[float] | None:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if error
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def _retrieve_context(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context using hybrid search.

        Args:
            query: Search query
            filters: Optional metadata filters

        Returns:
            List of relevant documents
        """
        if not self.use_rag:
            return []

        try:
            # Generate embedding for semantic search
            query_vector = await self._get_embedding(query)

            # Perform hybrid search
            results = await hybrid_search_service.search(
                query=query,
                query_vector=query_vector,
                limit=self.rag_context_limit,
                fusion_method="rrf",
                filters=filters,
            )

            logger.info(f"Retrieved {len(results)} relevant documents for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []

    async def _format_rag_context(self, documents: list[dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string.

        Args:
            documents: Retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return ""

        context_parts = ["Contexto Astrológico Relevante:"]

        for i, doc in enumerate(documents, 1):
            # Extract relevant information from document
            content = doc.get("payload", {}).get("content", "")
            metadata = doc.get("payload", {}).get("metadata", {})

            # Add source information if available
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "")

            context_parts.append(f"\n[Fonte {i}]: {source}")
            if page:
                context_parts.append(f" (página {page})")

            # Add content preview
            context_parts.append(f"\n{content[:500]}...")

        return "\n".join(context_parts)

    async def generate_planet_interpretation(
        self,
        planet: str,
        sign: str,
        house: int,
        dignities: dict[str, Any] | None = None,
        sect: str | None = None,
        retrograde: bool = False,
        progress_callback: Callable[[int], None] | None = None,
    ) -> str:
        """
        Generate RAG-enhanced interpretation for a planet placement.

        Args:
            planet: Planet name
            sign: Zodiac sign
            house: House number
            dignities: Planet dignities
            sect: Chart sect
            retrograde: Whether planet is retrograde
            progress_callback: Optional callback for progress updates

        Returns:
            Generated interpretation text
        """
        # Validate input
        validated_dignities = self._validate_dignities(dignities) if dignities else {}
        validated_sect = sect if sect in ["diurno", "noturno"] else None

        # Build cache parameters
        cache_params = {
            "planet": planet,
            "sign": sign,
            "house": house,
            "dignities": validated_dignities,
            "sect": validated_sect,
            "retrograde": retrograde,
        }

        # Try cache first
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="planet_rag",
                parameters=cache_params,
                model=settings.OPENAI_MODEL,
                prompt_version=self.prompts.get("version", "1.0"),
            )
            if cached:
                self._cache_hits += 1
                logger.info(f"Using cached RAG interpretation for {planet} in {sign}")
                return cached

        self._cache_misses += 1

        # Build search query for RAG
        search_query = f"{planet} in {sign} house {house}"
        if validated_dignities:
            dignity_str = ", ".join(f"{k}: {v}" for k, v in validated_dignities.items())
            search_query += f" dignities {dignity_str}"
        if retrograde:
            search_query += " retrograde"

        # Retrieve relevant context
        if progress_callback:
            progress_callback(10)  # 10% - Starting retrieval

        documents = await self._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format RAG context
        rag_context = await self._format_rag_context(documents)

        if progress_callback:
            progress_callback(30)  # 30% - Context retrieved

        # Build enhanced prompt with RAG context
        dignity_context = self._format_dignities(validated_dignities)

        base_prompt = self.prompts["planet_prompts"]["base"].format(
            planet=planet,
            sign=sign,
            house=house,
            dignities=dignity_context,
            sect=validated_sect or "não especificado",
            retrograde="Sim" if retrograde else "Não",
        )

        # Add RAG context if available
        if rag_context:
            enhanced_prompt = f"{rag_context}\n\nCom base no contexto acima e seu conhecimento astrológico:\n\n{base_prompt}"
        else:
            enhanced_prompt = base_prompt

        if progress_callback:
            progress_callback(50)  # 50% - Generating interpretation

        # Generate interpretation
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": enhanced_prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            interpretation = response.choices[0].message.content
            interpretation_text = interpretation.strip() if interpretation else ""

            if progress_callback:
                progress_callback(80)  # 80% - Interpretation generated

            # Store in cache
            if interpretation_text and self.cache_service:
                await self.cache_service.set(
                    interpretation_type="planet_rag",
                    subject=planet,
                    parameters=cache_params,
                    content=interpretation_text,
                    model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                )

            # Log success
            if interpretation_text:
                logger.info(
                    f"Successfully generated RAG-enhanced interpretation for {planet} in {sign} "
                    f"(used {len(documents)} context documents)"
                )

            if progress_callback:
                progress_callback(100)  # 100% - Complete

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG interpretation for {planet} in {sign}: {e}")
            # Fall back to non-RAG interpretation
            return await super().generate_planet_interpretation(
                planet, sign, house, dignities, sect, retrograde, progress_callback
            )

    async def generate_aspect_interpretation(
        self,
        planet1: str,
        planet2: str,
        aspect: str,
        orb: float,
        planet1_sign: str | None = None,
        planet2_sign: str | None = None,
    ) -> str:
        """
        Generate RAG-enhanced interpretation for an aspect.

        Args:
            planet1: First planet
            planet2: Second planet
            aspect: Aspect name
            orb: Orb value
            planet1_sign: Sign of first planet
            planet2_sign: Sign of second planet

        Returns:
            Generated interpretation text
        """
        # Build search query
        search_query = f"{planet1} {aspect} {planet2}"
        if planet1_sign:
            search_query += f" {planet1} in {planet1_sign}"
        if planet2_sign:
            search_query += f" {planet2} in {planet2_sign}"

        # Retrieve context
        documents = await self._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format context
        rag_context = await self._format_rag_context(documents)

        # Build prompt
        base_prompt = self.prompts["aspect_prompts"]["base"].format(
            planet1=planet1,
            planet2=planet2,
            aspect=aspect,
            orb=orb,
            planet1_sign=planet1_sign or "não especificado",
            planet2_sign=planet2_sign or "não especificado",
        )

        if rag_context:
            enhanced_prompt = f"{rag_context}\n\nCom base no contexto acima:\n\n{base_prompt}"
        else:
            enhanced_prompt = base_prompt

        # Generate interpretation
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": enhanced_prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            interpretation = response.choices[0].message.content
            return interpretation.strip() if interpretation else ""

        except Exception as e:
            logger.error(f"Error generating RAG aspect interpretation: {e}")
            return await super().generate_aspect_interpretation(
                planet1, planet2, aspect, orb, planet1_sign, planet2_sign
            )

    async def get_statistics(self) -> dict[str, Any]:
        """
        Get service statistics including RAG usage.

        Returns:
            Statistics dictionary
        """
        base_stats = await super().get_statistics()

        # Add RAG-specific stats
        base_stats["rag_enabled"] = self.use_rag
        base_stats["rag_context_limit"] = self.rag_context_limit

        # Get hybrid search stats
        if self.use_rag:
            hybrid_stats = hybrid_search_service.get_stats()
            base_stats["hybrid_search"] = hybrid_stats

        return base_stats


# Factory function to create the appropriate service
def create_interpretation_service(
    db: AsyncSession,
    use_cache: bool = True,
    use_rag: bool = True,
) -> InterpretationService:
    """
    Create interpretation service with optional RAG support.

    Args:
        db: Database session
        use_cache: Whether to use caching
        use_rag: Whether to use RAG

    Returns:
        InterpretationService or InterpretationServiceRAG instance
    """
    if use_rag:
        return InterpretationServiceRAG(db, use_cache, use_rag)
    else:
        return InterpretationService(db, use_cache)