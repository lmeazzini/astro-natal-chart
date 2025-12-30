"""
Interpretation service with RAG (Retrieval-Augmented Generation) support.

This service provides AI-powered astrological interpretations enhanced by
retrieving relevant knowledge from a vector database before generating
interpretations, resulting in more accurate and contextually grounded responses.
"""

import asyncio
from pathlib import Path
from typing import Any, TypedDict

import yaml
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.astro.dignities import get_sign_ruler
from app.core.config import settings
from app.models.chart import BirthChart
from app.services.interpretation_cache_service import InterpretationCacheService
from app.services.rag import hybrid_search_service

# =============================================================================
# Constants
# =============================================================================

# RAG model and version identifiers
RAG_MODEL_ID = "gpt-4o-mini-rag"
RAG_PROMPT_VERSION = "rag-v1"

# Semaphore to limit concurrent OpenAI API calls (avoid rate limits)
# Using 5 concurrent calls as a safe default for OpenAI's rate limits
OPENAI_CONCURRENCY_LIMIT = 5


# =============================================================================
# Type Definitions
# =============================================================================


class PlanetData(TypedDict, total=False):
    """Type definition for planet data structure."""

    name: str
    sign: str
    house: int
    longitude: float
    latitude: float
    speed: float
    retrograde: bool
    dignities: dict[str, Any]


class HouseData(TypedDict, total=False):
    """Type definition for house data structure."""

    house: int
    number: int  # Alternative key for house number
    sign: str
    cusp: float


class AspectData(TypedDict, total=False):
    """Type definition for aspect data structure."""

    planet1: str
    planet2: str
    aspect: str
    orb: float
    applying: bool


class ArabicPartData(TypedDict, total=False):
    """Type definition for Arabic Part data structure."""

    longitude: float
    sign: str
    degree: float
    house: int


# Arabic Parts definitions
ARABIC_PARTS: dict[str, dict[str, str]] = {
    "fortune": {
        "name": "Part of Fortune",
        "name_pt": "Lote da Fortuna",
    },
    "spirit": {
        "name": "Part of Spirit",
        "name_pt": "Lote do Espírito",
    },
    "eros": {
        "name": "Part of Eros",
        "name_pt": "Lote de Eros",
    },
    "necessity": {
        "name": "Part of Necessity",
        "name_pt": "Lote da Necessidade",
    },
    # Extended Arabic Parts (Issue #110 - Phase 2)
    "marriage": {
        "name": "Part of Marriage",
        "name_pt": "Lote do Casamento",
    },
    "victory": {
        "name": "Part of Victory",
        "name_pt": "Lote da Vitória",
    },
    "father": {
        "name": "Part of Father",
        "name_pt": "Lote do Pai",
    },
    "mother": {
        "name": "Part of Mother",
        "name_pt": "Lote da Mãe",
    },
    "children": {
        "name": "Part of Children",
        "name_pt": "Lote dos Filhos",
    },
    "exaltation": {
        "name": "Part of Exaltation",
        "name_pt": "Lote da Exaltação",
    },
    "illness": {
        "name": "Part of Illness",
        "name_pt": "Lote da Doença",
    },
    "courage": {
        "name": "Part of Courage",
        "name_pt": "Lote da Coragem",
    },
    "reputation": {
        "name": "Part of Reputation",
        "name_pt": "Lote da Reputação",
    },
}


class InterpretationServiceRAG:
    """Interpretation service with RAG support for enhanced astrological interpretations."""

    def __init__(
        self,
        db: AsyncSession,
        use_cache: bool = True,
        use_rag: bool = True,
        language: str = "pt-BR",
    ):
        """
        Initialize RAG interpretation service.

        Args:
            db: Database session
            use_cache: Whether to use interpretation cache
            use_rag: Whether to use RAG for context retrieval
            language: Language for interpretations ('pt-BR' or 'en-US')
        """
        self.db = db
        self.use_cache = use_cache
        self.use_rag = use_rag
        self.language = language
        self.rag_context_limit = 3  # Number of relevant documents to retrieve

        # Semaphore for limiting concurrent OpenAI calls
        self._semaphore = asyncio.Semaphore(OPENAI_CONCURRENCY_LIMIT)

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Initialize cache service
        self.cache_service = InterpretationCacheService(db) if use_cache else None

        # Initialize interpretation repository for upsert operations
        from app.repositories.interpretation_repository import InterpretationRepository

        self.repo = InterpretationRepository(db)

        # Cache statistics
        self._cache_hits = 0
        self._cache_misses = 0

        # Load interpretation prompts
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict[str, Any]:
        """Load interpretation prompts from YAML file."""
        prompts_path = Path(__file__).parent.parent / "astro" / "interpretation_prompts.yaml"

        try:
            with open(prompts_path, encoding="utf-8") as f:
                result: dict[str, Any] = yaml.safe_load(f)
                return result
        except Exception as e:
            logger.error(f"Failed to load interpretation prompts: {e}")
            return {
                "version": "1.0",
                "system_prompt": "Você é um astrólogo tradicional especializado.",
                "planet_prompts": {"base": "Interprete {planet} em {sign} na casa {house}."},
                "house_prompts": {"base": "Interprete a casa {house} em {sign}."},
                "aspect_prompts": {"base": "Interprete {aspect} entre {planet1} e {planet2}."},
                "arabic_part_prompts": {
                    "base": "Interprete {part_name} em {sign} na casa {house}."
                },
            }

    def _get_language_instruction(self) -> str:
        """
        Get language instruction to append to system prompt.

        Returns:
            Language instruction string for non-Portuguese languages,
            empty string for Portuguese (default prompt language).
        """
        if self.language.startswith("en"):
            return (
                "\n\nIMPORTANT: You MUST respond in English (en-US). "
                "Translate all astrological terms to English and produce natural, fluent English output. "
                "Do NOT respond in Portuguese."
            )
        # Portuguese is the default prompt language, no instruction needed
        return ""

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt with language instruction appended.

        Returns:
            System prompt with optional language instruction.
        """
        system_prompt: str = self.prompts["system_prompt"]
        return system_prompt + self._get_language_instruction()

    def _validate_dignities(
        self, planet: str, sign: str, dignities: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate and ensure dignities are properly formatted.

        Args:
            planet: Planet name
            sign: Zodiac sign
            dignities: Dignities dictionary

        Returns:
            Validated dignities dictionary
        """
        if not dignities:
            return {}

        validated: dict[str, Any] = {}
        for key, value in dignities.items():
            if isinstance(value, bool):
                validated[key] = value
            elif isinstance(value, int | float):
                validated[key] = value
            elif isinstance(value, str):
                validated[key] = value
            else:
                validated[key] = str(value)

        return validated

    def _format_dignities(self, dignities: dict[str, Any]) -> str:
        """
        Format dignities dictionary into readable text.

        Args:
            dignities: Dignities dictionary

        Returns:
            Formatted string
        """
        if not dignities:
            return "Sem dignidades essenciais (peregrino)"

        parts = []
        dignity_names = {
            "ruler": "Domicílio",
            "exalted": "Exaltação",
            "triplicity": "Triplicidade",
            "term": "Termo",
            "face": "Face",
            "detriment": "Detrimento",
            "fall": "Queda",
        }

        for key, value in dignities.items():
            if key in dignity_names and value:
                parts.append(f"{dignity_names[key]}: {value}")
            elif key == "score":
                parts.append(f"Pontuação: {value}")

        return "; ".join(parts) if parts else "Sem dignidades essenciais"

    def get_session_cache_stats(self) -> dict[str, Any]:
        """Get session cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
        }

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

    async def retrieve_context(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context using hybrid search.

        This method performs a hybrid search combining semantic and keyword search
        to find relevant astrological documents for interpretation context.

        Args:
            query: Search query describing the astrological element to interpret
            filters: Optional metadata filters (e.g., {"document_type": ["text", "pdf"]})

        Returns:
            List of relevant documents with scores and metadata
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
        # Validate input
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
                language=self.language,
            )
            if cached:
                self._cache_hits += 1
                logger.info(
                    f"Using cached RAG interpretation for {planet} in {sign} ({self.language})"
                )
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
        documents = await self.retrieve_context(
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
                    {"role": "system", "content": self._get_system_prompt()},
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
                    language=self.language,
                )

            # Log success
            if interpretation_text:
                logger.info(
                    f"Successfully generated RAG-enhanced interpretation for {planet} in {sign} "
                    f"({self.language}, used {len(documents)} context documents)"
                )

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG interpretation for {planet} in {sign}: {e}")
            if self.language.startswith("en"):
                return f"Interpretation not available for {planet} in {sign}."
            return f"Interpretação não disponível para {planet} em {sign}."

    async def generate_house_interpretation(
        self,
        house: int,
        sign: str,
        ruler: str,
        ruler_dignities: dict[str, Any],
        sect: str,
    ) -> str:
        """
        Generate RAG-enhanced interpretation for a house.

        Args:
            house: House number (1-12)
            sign: Sign on the cusp
            ruler: Planet ruling the sign
            ruler_dignities: Dignities of the ruler
            sect: Chart sect

        Returns:
            Generated interpretation text
        """
        # Build cache parameters
        cache_params = {
            "house": house,
            "sign": sign,
            "ruler": ruler,
            "ruler_dignities": ruler_dignities,
            "sect": sect,
        }

        # Try cache first
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="house_rag",
                parameters=cache_params,
                model=settings.OPENAI_MODEL,
                prompt_version=self.prompts.get("version", "1.0"),
                language=self.language,
            )
            if cached:
                self._cache_hits += 1
                logger.info(
                    f"Using cached RAG interpretation for house {house} in {sign} ({self.language})"
                )
                return cached

        self._cache_misses += 1

        # Build search query
        search_query = f"house {house} in {sign} ruled by {ruler}"

        # Retrieve context
        documents = await self.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format context
        rag_context = await self._format_rag_context(documents)

        # Format dignities
        ruler_context = self._format_dignities(ruler_dignities)

        # Build prompt
        base_prompt = self.prompts["house_prompts"]["base"].format(
            house=house,
            sign=sign,
            ruler=ruler,
            ruler_dignities=ruler_context,
            sect=sect,
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
                    {"role": "system", "content": self._get_system_prompt()},
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
                    interpretation_type="house_rag",
                    subject=str(house),
                    parameters=cache_params,
                    content=interpretation_text,
                    model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                    language=self.language,
                )

            if interpretation_text:
                logger.info(
                    f"Successfully generated RAG-enhanced interpretation for house {house} in {sign} "
                    f"({self.language}, used {len(documents)} context documents)"
                )

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG house interpretation: {e}")
            if self.language.startswith("en"):
                return f"Interpretation not available for house {house} in {sign}."
            return f"Interpretação não disponível para casa {house} em {sign}."

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
        # Build cache parameters (orb excluded to maximize cache hits)
        cache_params = {
            "planet1": planet1,
            "planet2": planet2,
            "aspect": aspect,
            "sign1": sign1,
            "sign2": sign2,
            "applying": applying,
            "sect": sect,
            "dignities1": dignities1,
            "dignities2": dignities2,
        }

        # Try cache first
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="aspect_rag",
                parameters=cache_params,
                model=settings.OPENAI_MODEL,
                prompt_version=self.prompts.get("version", "1.0"),
                language=self.language,
            )
            if cached:
                self._cache_hits += 1
                logger.info(
                    f"Using cached RAG interpretation for {planet1} {aspect} {planet2} ({self.language})"
                )
                return cached

        self._cache_misses += 1

        # Build search query
        search_query = f"{planet1} {aspect} {planet2} in {sign1} and {sign2}"

        # Retrieve context
        documents = await self.retrieve_context(
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
                    {"role": "system", "content": self._get_system_prompt()},
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
                    interpretation_type="aspect_rag",
                    subject=f"{planet1}-{aspect}-{planet2}",
                    parameters=cache_params,
                    content=interpretation_text,
                    model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                    language=self.language,
                )

            if interpretation_text:
                logger.info(
                    f"Successfully generated RAG-enhanced interpretation for {planet1} {aspect} {planet2} "
                    f"({self.language}, used {len(documents)} context documents)"
                )

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG aspect interpretation: {e}")
            if self.language.startswith("en"):
                return f"Interpretation not available for {aspect} between {planet1} and {planet2}."
            return f"Interpretação não disponível para {aspect} entre {planet1} e {planet2}."

    async def generate_arabic_part_interpretation(
        self,
        part_key: str,
        sign: str,
        house: int,
        degree: float,
        sect: str,
    ) -> str:
        """
        Generate RAG-enhanced interpretation for an Arabic Part.

        Args:
            part_key: Part key (fortune, spirit, eros, necessity)
            sign: Zodiac sign where the part falls
            house: House number (1-12)
            degree: Degree within the sign
            sect: Chart sect ("diurnal" or "nocturnal")

        Returns:
            Generated interpretation text
        """
        if part_key not in ARABIC_PARTS:
            return ""

        part_info = ARABIC_PARTS[part_key]
        part_name = part_info["name"]
        part_name_pt = part_info["name_pt"]

        # Build cache parameters
        cache_params = {
            "part_key": part_key,
            "sign": sign,
            "house": house,
            "sect": sect,
        }

        # Try cache first
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="arabic_part_rag",
                parameters=cache_params,
                model=settings.OPENAI_MODEL,
                prompt_version=self.prompts.get("version", "1.0"),
                language=self.language,
            )
            if cached:
                self._cache_hits += 1
                logger.info(
                    f"Using cached RAG interpretation for {part_name} in {sign} ({self.language})"
                )
                return cached

        self._cache_misses += 1

        # Build search query for RAG
        search_query = f"{part_name} {part_name_pt} in {sign} house {house}"

        # Retrieve relevant context
        documents = await self.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        # Format RAG context
        rag_context = await self._format_rag_context(documents)

        # Get sign ruler (imported at module level)
        sign_ruler = get_sign_ruler(sign) or "Unknown"

        # Build prompt
        base_prompt = self.prompts["arabic_part_prompts"]["base"].format(
            part_name=part_name,
            part_name_pt=part_name_pt,
            sign=sign,
            house=house,
            degree=round(degree, 1),
            sect=sect,
            sign_ruler=sign_ruler,
            ruler_dignities="(consultar posição no mapa)",
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
                    {"role": "system", "content": self._get_system_prompt()},
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
                    interpretation_type="arabic_part_rag",
                    subject=part_key,
                    parameters=cache_params,
                    content=interpretation_text,
                    model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                    language=self.language,
                )

            if interpretation_text:
                logger.info(
                    f"Successfully generated RAG-enhanced interpretation for {part_name} in {sign} "
                    f"({self.language}, used {len(documents)} context documents)"
                )

            return interpretation_text

        except Exception as e:
            logger.error(f"Error generating RAG interpretation for {part_name}: {e}")
            if self.language.startswith("en"):
                return f"Interpretation not available for {part_name} in {sign}."
            return f"Interpretação não disponível para {part_name_pt} em {sign}."

    async def _generate_with_semaphore(
        self,
        coro: Any,
        key: str,
        category: str,
    ) -> tuple[str, str, str]:
        """
        Execute a coroutine with semaphore limiting for rate control.

        Args:
            coro: The coroutine to execute
            key: The key identifier for this interpretation
            category: The category (planets, houses, aspects, arabic_parts)

        Returns:
            Tuple of (category, key, interpretation_text)
        """
        async with self._semaphore:
            try:
                result = await coro
                return (category, key, result)
            except Exception as e:
                logger.error(f"Failed to generate {category} interpretation for {key}: {e}")
                return (category, key, "")

    async def generate_all_rag_interpretations(
        self,
        chart: BirthChart,
        chart_data: dict[str, Any],
        force: bool = False,
    ) -> dict[str, dict[str, str]]:
        """
        Generate all RAG-enhanced interpretations for a chart and save to database.

        Uses parallel processing with semaphore limiting to speed up generation
        while respecting OpenAI rate limits (max 5 concurrent calls).

        Args:
            chart: BirthChart model instance
            chart_data: Calculated chart data
            force: If True, regenerate interpretations even if they exist.
                   If False (default), skip generation if interpretation already exists.

        Returns:
            Dictionary with all interpretations grouped by type
        """
        results: dict[str, dict[str, str]] = {
            "planets": {},
            "houses": {},
            "aspects": {},
            "arabic_parts": {},
        }

        # Extract language-specific data (supports both legacy flat and language-first format)
        from app.utils.chart_data_accessor import extract_language_data

        lang_data = extract_language_data(chart_data, self.language)
        planets = lang_data.get("planets", [])
        houses = lang_data.get("houses", [])
        aspects = lang_data.get("aspects", [])
        arabic_parts = lang_data.get("arabic_parts", {})
        sect = lang_data.get("sect", "diurnal")

        # Phase 1: Check which interpretations already exist and collect tasks
        tasks: list[tuple[Any, str, str, str, dict[str, Any]]] = []
        # Format: (coroutine, category, key, interpretation_type, params_for_db)

        # Collect planet interpretation tasks
        for planet in planets:
            planet_name = planet.get("name", "")
            if not planet_name:
                continue

            sign = planet.get("sign", "")
            house = planet.get("house", 1)
            retrograde = planet.get("retrograde", False)
            dignities = planet.get("dignities", {})

            # Check if interpretation already exists (unless force=True)
            if not force:
                existing = await self.repo.get_by_chart_and_subject(
                    chart_id=chart.id,  # type: ignore[arg-type]
                    subject=planet_name,
                    interpretation_type="planet",
                    language=self.language,
                )
                if existing:
                    logger.debug(
                        f"Skipping planet {planet_name} - interpretation already exists ({self.language})"
                    )
                    results["planets"][planet_name] = existing.content
                    continue

            # Add to tasks for parallel generation
            coro = self.generate_planet_interpretation(
                planet=planet_name,
                sign=sign,
                house=house,
                dignities=dignities,
                sect=sect,
                retrograde=retrograde,
            )
            tasks.append((coro, "planets", planet_name, "planet", {}))

        # Collect house interpretation tasks
        for house_data in houses:
            house_number = house_data.get("house", 0) or house_data.get("number", 0)
            house_sign = house_data.get("sign", "")

            if not house_number or not house_sign:
                continue

            house_key = str(house_number)

            if not force:
                existing = await self.repo.get_by_chart_and_subject(
                    chart_id=chart.id,  # type: ignore[arg-type]
                    subject=house_key,
                    interpretation_type="house",
                    language=self.language,
                )
                if existing:
                    logger.debug(
                        f"Skipping house {house_number} - interpretation already exists ({self.language})"
                    )
                    results["houses"][house_key] = existing.content
                    continue

            ruler = get_sign_ruler(house_sign) or "Unknown"
            coro = self.generate_house_interpretation(
                house=house_number,
                sign=house_sign,
                ruler=ruler,
                ruler_dignities={},
                sect=sect,
            )
            tasks.append((coro, "houses", house_key, "house", {"house_sign": house_sign}))

        # Collect aspect interpretation tasks
        max_aspects = settings.RAG_MAX_ASPECTS
        for aspect in aspects[:max_aspects]:
            planet1 = aspect.get("planet1", "")
            planet2 = aspect.get("planet2", "")
            aspect_name = aspect.get("aspect", "")
            orb = aspect.get("orb", 0.0)

            if not all([planet1, planet2, aspect_name]):
                continue

            aspect_key = f"{planet1}-{aspect_name}-{planet2}"

            if not force:
                existing = await self.repo.get_by_chart_and_subject(
                    chart_id=chart.id,  # type: ignore[arg-type]
                    subject=aspect_key,
                    interpretation_type="aspect",
                    language=self.language,
                )
                if existing:
                    logger.debug(
                        f"Skipping aspect {aspect_key} - interpretation already exists ({self.language})"
                    )
                    results["aspects"][aspect_key] = existing.content
                    continue

            planet1_data: dict[str, Any] = next(
                (p for p in planets if p.get("name") == planet1), {}
            )
            planet2_data: dict[str, Any] = next(
                (p for p in planets if p.get("name") == planet2), {}
            )

            coro = self.generate_aspect_interpretation(
                planet1=planet1,
                planet2=planet2,
                aspect=aspect_name,
                sign1=planet1_data.get("sign", ""),
                sign2=planet2_data.get("sign", ""),
                orb=orb,
                applying=aspect.get("applying", False),
                sect=sect,
                dignities1=planet1_data.get("dignities", {}),
                dignities2=planet2_data.get("dignities", {}),
            )
            tasks.append((coro, "aspects", aspect_key, "aspect", {}))

        # Collect Arabic Parts interpretation tasks
        for part_key, part_data in arabic_parts.items():
            if part_key not in ARABIC_PARTS:
                continue

            if not force:
                existing = await self.repo.get_by_chart_and_subject(
                    chart_id=chart.id,  # type: ignore[arg-type]
                    subject=part_key,
                    interpretation_type="arabic_part",
                    language=self.language,
                )
                if existing:
                    logger.debug(
                        f"Skipping arabic_part {part_key} - interpretation already exists ({self.language})"
                    )
                    results["arabic_parts"][part_key] = existing.content
                    continue

            coro = self.generate_arabic_part_interpretation(
                part_key=part_key,
                sign=part_data.get("sign", ""),
                house=part_data.get("house", 1),
                degree=part_data.get("degree", 0.0),
                sect=sect,
            )
            tasks.append((coro, "arabic_parts", part_key, "arabic_part", {}))

        # Phase 2: Generate all interpretations in parallel with semaphore
        if tasks:
            logger.info(
                f"Generating {len(tasks)} interpretations in parallel "
                f"(semaphore limit: {OPENAI_CONCURRENCY_LIMIT}) for chart {chart.id}"
            )

            # Create semaphore-wrapped tasks
            semaphore_tasks = [
                self._generate_with_semaphore(coro, key, category)
                for coro, category, key, _, _ in tasks
            ]

            # Run all tasks in parallel
            generation_results = await asyncio.gather(*semaphore_tasks, return_exceptions=True)

            # Process results and prepare for database save
            task_map = {
                (t[1], t[2]): (t[3], t[4]) for t in tasks
            }  # (category, key) -> (type, params)

            for result in generation_results:
                if isinstance(result, BaseException):
                    logger.error(f"Task failed with exception: {result}")
                    continue

                # result is tuple[str, str, str | None] from _generate_with_semaphore
                category, key, interpretation = result  # type: ignore[misc]
                if not interpretation:
                    # Handle empty interpretation for houses
                    if category == "houses":
                        task_info: tuple[str | None, dict[str, str]] = task_map.get(
                            (category, key), (None, {})
                        )
                        params = task_info[1] if task_info else {}
                        house_sign = params.get("house_sign", "")
                        interpretation = (
                            f"Casa {key} ({house_sign}): "
                            f"Esta casa governa áreas específicas da vida conforme sua posição em {house_sign}."
                        )
                    else:
                        continue

                results[category][key] = interpretation

        # Phase 3: Save all new interpretations to database
        for category, interpretations in results.items():
            # Map category to interpretation_type
            type_map = {
                "planets": "planet",
                "houses": "house",
                "aspects": "aspect",
                "arabic_parts": "arabic_part",
            }
            interpretation_type = type_map[category]

            for key, content in interpretations.items():
                # Only save if this was a newly generated interpretation
                was_generated = any(t[1] == category and t[2] == key for t in tasks)
                if was_generated and content:
                    try:
                        await self.repo.upsert_interpretation(
                            chart_id=chart.id,
                            interpretation_type=interpretation_type,
                            subject=key,
                            content=content,
                            language=self.language,
                            openai_model=RAG_MODEL_ID,
                            prompt_version=RAG_PROMPT_VERSION,
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to save {interpretation_type} interpretation for {key}: {e}"
                        )

        # Commit all interpretations
        await self.db.flush()
        logger.info(
            f"Generated and saved {len(results['planets'])} planet, "
            f"{len(results['houses'])} house, {len(results['aspects'])} aspect, "
            f"and {len(results['arabic_parts'])} Arabic Part "
            f"RAG interpretations for chart {chart.id}"
        )

        return results

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
