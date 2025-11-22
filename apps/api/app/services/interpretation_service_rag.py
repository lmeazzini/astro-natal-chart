"""
Enhanced interpretation service with RAG (Retrieval-Augmented Generation) support.

This service extends the base interpretation service by adding the ability to
retrieve relevant astrological knowledge from a vector database before generating
interpretations, resulting in more accurate and contextually grounded responses.
"""

from typing import Any

from loguru import logger
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
        dignities: dict[str, Any],
        sect: str,
        retrograde: bool,
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

        Returns:
            Generated interpretation text
        """
        # Validate input using parent method
        validated_dignities = self._validate_dignities(planet, sign, dignities)
        validated_sect = sect if sect in ["diurnal", "nocturnal"] else sect

        # Build cache parameters
        cache_params = {
            "planet": planet,
            "sign": sign,
            "house": house,
            "dignities": validated_dignities,
            "sect": sect,
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
        documents = await self._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format RAG context
        rag_context = await self._format_rag_context(documents)

        # Build enhanced prompt with RAG context
        dignity_context = self._format_dignities(validated_dignities)

        base_prompt = self.prompts["planet_prompts"]["base"].format(
            planet=planet,
            sign=sign,
            house=house,
            dignities=dignity_context,
            sect=validated_sect,
            retrograde="Sim" if retrograde else "Não",
        )

        # Add RAG context if available
        if rag_context:
            enhanced_prompt = f"{rag_context}\n\nCom base no contexto acima e seu conhecimento astrológico:\n\n{base_prompt}"
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
            interpretation_text = interpretation.strip() if interpretation else ""

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

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG interpretation for {planet} in {sign}: {e}")
            # Fall back to non-RAG interpretation
            return await super().generate_planet_interpretation(
                planet, sign, house, dignities, sect, retrograde
            )

    async def generate_aspect_interpretation(
        self,
        planet1: str,
        planet2: str,
        aspect: str,
        sign1: str,
        sign2: str,
        orb: float,
        applying: bool,
        sect: str,
        dignities1: dict[str, Any],
        dignities2: dict[str, Any],
    ) -> str:
        """
        Generate RAG-enhanced interpretation for an aspect.

        Args:
            planet1: First planet name
            planet2: Second planet name
            aspect: Aspect type (e.g., "Trine", "Square")
            sign1: Sign of first planet
            sign2: Sign of second planet
            orb: Orb in degrees
            applying: Whether aspect is applying
            sect: Chart sect
            dignities1: Dignities of first planet
            dignities2: Dignities of second planet

        Returns:
            Generated interpretation text
        """
        # Build search query
        search_query = f"{planet1} {aspect} {planet2} in {sign1} and {sign2}"

        # Retrieve context
        documents = await self._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format context
        rag_context = await self._format_rag_context(documents)

        # Format dignities
        dignities1_context = self._format_dignities(dignities1)
        dignities2_context = self._format_dignities(dignities2)

        # Build prompt
        base_prompt = self.prompts["aspect_prompts"]["base"].format(
            aspect=aspect,
            planet1=planet1,
            planet2=planet2,
            sign1=sign1,
            sign2=sign2,
            orb=round(orb, 1),
            applying="Sim" if applying else "Não",
            sect=sect,
            dignities1=dignities1_context,
            dignities2=dignities2_context,
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
                planet1, planet2, aspect, sign1, sign2, orb, applying, sect, dignities1, dignities2
            )

    def get_statistics(self) -> dict[str, Any]:
        """
        Get service statistics including RAG usage.

        Returns:
            Statistics dictionary
        """
        # Get base session cache stats
        base_stats = self.get_session_cache_stats()

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
