#!/usr/bin/env python
"""
Script to seed RAG system with astrology knowledge documents.

This script populates:
1. PostgreSQL vector_documents table
2. Qdrant vector database
3. BM25 search index

Usage:
    # Run inside Docker container
    docker compose exec api uv run python scripts/seed_rag_documents.py

    # Run with verbose logging
    docker compose exec api uv run python scripts/seed_rag_documents.py --verbose

    # Clear existing documents first
    docker compose exec api uv run python scripts/seed_rag_documents.py --clear
"""

import asyncio
import sys

sys.path.insert(0, "/app")

from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal

# Import all models to avoid circular dependency issues
from app.models import (  # noqa: F401
    AuditLog,
    BirthChart,
    BlogPost,
    InterpretationCache,
    OAuthAccount,
    PasswordResetToken,
    PublicChart,
    PublicChartInterpretation,
    SearchIndex,
    User,
    UserConsent,
    VectorDocument,
)
from app.services.rag import document_ingestion_service

# Sample astrology documents to ingest
ASTROLOGY_DOCUMENTS = [
    {
        "title": "Fundamentos da Astrologia Tradicional",
        "content": """
# Fundamentos da Astrologia Tradicional

A astrologia tradicional é um sistema antigo de interpretação que remonta à Babilônia, Grécia e Roma.

## Planetas e Seus Significados

### Planetas Pessoais (rápidos)
- **Sol**: Identidade, ego, vitalidade, consciência
- **Lua**: Emoções, instintos, necessidades, mundo interno
- **Mercúrio**: Comunicação, pensamento, intelecto, aprendizagem
- **Vênus**: Amor, valores, beleza, relacionamentos, prazer
- **Marte**: Ação, desejo, coragem, competição, energia

### Planetas Sociais
- **Júpiter**: Expansão, sabedoria, filosofia, sorte, crescimento
- **Saturno**: Estrutura, disciplina, limitações, responsabilidade, tempo

### Planetas Transpessoais (lentos)
- **Urano**: Inovação, rebeldia, mudanças súbitas, liberdade
- **Netuno**: Espiritualidade, ilusão, inspiração, dissolução
- **Plutão**: Transformação, poder, morte e renascimento, profundidade

## Dignidades Essenciais

### Domicílio (Rulership)
Planeta em seu próprio signo possui máxima força:
- Sol em Leão
- Lua em Câncer
- Mercúrio em Gêmeos e Virgem
- Vênus em Touro e Libra
- Marte em Áries e Escorpião
- Júpiter em Sagitário e Peixes
- Saturno em Capricórnio e Aquário

### Exaltação
Planeta em signo de exaltação opera com grande eficácia:
- Sol em Áries (19°)
- Lua em Touro (3°)
- Mercúrio em Virgem (15°)
- Vênus em Peixes (27°)
- Marte em Capricórnio (28°)
- Júpiter em Câncer (15°)
- Saturno em Libra (21°)

### Detrimento
Planeta no signo oposto ao seu domicílio, opera com dificuldade.

### Queda
Planeta no signo oposto à sua exaltação, opera com fraqueza.

## Triplicidades (Elementos)

### Fogo (quente e seco)
Signos: Áries, Leão, Sagitário
Temperamento: Colérico - ativo, assertivo, impulsivo

### Terra (frio e seco)
Signos: Touro, Virgem, Capricórnio
Temperamento: Melancólico - prático, estável, material

### Ar (quente e úmido)
Signos: Gêmeos, Libra, Aquário
Temperamento: Sanguíneo - mental, social, comunicativo

### Água (frio e úmido)
Signos: Câncer, Escorpião, Peixes
Temperamento: Fleumático - emocional, intuitivo, receptivo

## Modalidades (Quadruplicidades)

### Cardeal
Iniciadores, líderes: Áries, Câncer, Libra, Capricórnio

### Fixo
Estabilizadores, persistentes: Touro, Leão, Escorpião, Aquário

### Mutável
Adaptadores, flexíveis: Gêmeos, Virgem, Sagitário, Peixes
        """,
        "document_type": "astrology_fundamentals",
        "metadata": {"category": "traditional_astrology", "language": "pt-BR"},
    },
    {
        "title": "Sistema de Casas Astrológicas",
        "content": """
# Sistema de Casas Astrológicas

As 12 casas representam diferentes áreas da vida e experiência humana.

## Casa 1 (Ascendente)
**Significado**: Personalidade, aparência física, self, início da vida
**Casa Angular**: Muito poderosa
**Planeta Natural**: Marte
**Signos e interpretações**:
- Ascendente em Áries: Personalidade assertiva, pioneira
- Ascendente em Touro: Personalidade estável, sensual
- Ascendente em Gêmeos: Personalidade comunicativa, curiosa

## Casa 2
**Significado**: Dinheiro, posses, valores pessoais, recursos
**Casa Succedente**: Estabilidade
**Planeta Natural**: Vênus

## Casa 3
**Significado**: Comunicação, irmãos, educação básica, vizinhança
**Casa Cadente**: Adaptabilidade
**Planeta Natural**: Mercúrio

## Casa 4 (Fundo do Céu - IC)
**Significado**: Lar, família, raízes, final da vida
**Casa Angular**: Muito poderosa
**Planeta Natural**: Lua

## Casa 5
**Significado**: Criatividade, romance, filhos, prazer, autoexpressão
**Casa Succedente**: Estabilidade
**Planeta Natural**: Sol

## Casa 6
**Significado**: Trabalho, saúde, rotina, serviço, empregados
**Casa Cadente**: Adaptabilidade
**Planeta Natural**: Mercúrio

## Casa 7 (Descendente)
**Significado**: Parcerias, casamento, contratos, relacionamentos
**Casa Angular**: Muito poderosa
**Planeta Natural**: Vênus

## Casa 8
**Significado**: Transformação, morte, sexo, recursos compartilhados, ocultismo
**Casa Succedente**: Estabilidade
**Planeta Natural**: Marte/Plutão

## Casa 9
**Significado**: Filosofia, viagens longas, educação superior, religião
**Casa Cadente**: Adaptabilidade
**Planeta Natural**: Júpiter

## Casa 10 (Meio do Céu - MC)
**Significado**: Carreira, reputação, status, vocação, sucesso público
**Casa Angular**: Muito poderosa
**Planeta Natural**: Saturno

## Casa 11
**Significado**: Amizades, grupos, aspirações, esperanças, comunidade
**Casa Succedente**: Estabilidade
**Planeta Natural**: Saturno/Urano

## Casa 12
**Significado**: Inconsciente, isolamento, espiritualidade, autossabotagem
**Casa Cadente**: Adaptabilidade
**Planeta Natural**: Júpiter/Netuno

## Sistemas de Casas

### Placidus (mais comum)
- Divide o dia em 12 partes desiguais
- Baseado no movimento diurno
- Funciona mal em latitudes extremas

### Koch
- Similar a Placidus
- Baseado no nascimento como movimento

### Whole Sign (Signo Inteiro)
- Sistema mais antigo
- Cada casa = um signo completo
- Ascendente sempre no início da Casa 1

### Equal House (Casas Iguais)
- Todas as casas têm 30°
- Simples e direto

### Campanus
- Baseado na esfera celeste
- Funciona em todas as latitudes

### Regiomontanus
- Divide o equador celeste
- Preferido por alguns astrólogos tradicionais
        """,
        "document_type": "houses",
        "metadata": {"category": "houses", "language": "pt-BR"},
    },
    {
        "title": "Aspectos Astrológicos Tradicionais",
        "content": """
# Aspectos Astrológicos

Aspectos são ângulos formados entre planetas no mapa natal.

## Aspectos Maiores

### Conjunção (0°)
**Orbe**: 8-10°
**Natureza**: Neutro (depende dos planetas)
**Significado**: União, fusão de energias, intensificação
**Exemplo**: Sol conjunção Lua = Nova Lua no mapa natal

### Oposição (180°)
**Orbe**: 8°
**Natureza**: Desafiante/Tenso
**Significado**: Polaridade, tensão, consciência, projeção
**Exemplo**: Sol oposto Saturno = tensão entre vitalidade e limitação

### Trígono (120°)
**Orbe**: 8°
**Natureza**: Harmônico/Benéfico
**Significado**: Fluidez, talento natural, facilidade
**Elemento**: Mesmo elemento (fogo-fogo, terra-terra)
**Exemplo**: Vênus trígono Júpiter = facilidade em amor e expansão

### Quadratura (90°)
**Orbe**: 8°
**Natureza**: Desafiante/Dinâmico
**Significado**: Conflito, tensão criativa, ação
**Modalidade**: Mesma modalidade (cardeal-cardeal)
**Exemplo**: Marte quadrado Plutão = conflitos de poder e intensidade

### Sextil (60°)
**Orbe**: 6°
**Natureza**: Harmônico/Oportunidade
**Significado**: Oportunidade, cooperação, habilidade
**Elemento**: Elementos compatíveis (fogo-ar, terra-água)
**Exemplo**: Mercúrio sextil Urano = mente inovadora

## Aspectos Menores

### Quincunce/Inconjunção (150°)
**Orbe**: 2-3°
**Significado**: Ajuste, desconforto, incompatibilidade

### Semisextil (30°)
**Orbe**: 2°
**Significado**: Leve tensão, crescimento

### Semiquadratura (45°)
**Orbe**: 2°
**Significado**: Fricção, irritação menor

### Sesquiquadratura (135°)
**Orbe**: 2°
**Significado**: Desconforto persistente

## Aspectos Aplicativos vs. Separativos

### Aplicativo (Applying)
- Planeta mais rápido se aproxima do mais lento
- Aspecto ainda não exato
- Significado: Energia crescente, futuro, desenvolvimento

### Exato (Exact)
- Aspecto perfeito (0° de orbe)
- Máxima intensidade

### Separativo (Separating)
- Planeta mais rápido se afasta do mais lento
- Aspecto já passou
- Significado: Energia decrescente, passado, conclusão

## Padrões de Aspectos

### T-Square (Quadrado em T)
- Dois planetas em oposição
- Terceiro planeta em quadratura com ambos
- Intensa tensão criativa

### Grande Cruz
- Quatro planetas formando quadraturas
- Dois pares em oposição
- Máxima tensão e potencial de realização

### Grande Trígono
- Três planetas em trígono (triângulo)
- Mesmo elemento
- Grande talento, mas pode indicar preguiça

### Yod (Dedo de Deus)
- Dois planetas em sextil
- Terceiro em quincunce com ambos
- Destino, missão especial

### Stellium
- Três ou mais planetas na mesma casa ou signo
- Concentração de energia em uma área
        """,
        "document_type": "aspects",
        "metadata": {"category": "aspects", "language": "pt-BR"},
    },
    {
        "title": "Signos do Zodíaco - Características Detalhadas",
        "content": """
# Signos do Zodíaco

Descrição completa dos 12 signos astrológicos.

## ÁRIES (21/03 - 19/04)
**Elemento**: Fogo
**Modalidade**: Cardeal
**Regente**: Marte
**Exaltação**: Sol
**Características**: Pioneiro, corajoso, impulsivo, competitivo
**Corpo**: Cabeça, rosto
**Palavras-chave**: Iniciativa, ação, independência

## TOURO (20/04 - 20/05)
**Elemento**: Terra
**Modalidade**: Fixo
**Regente**: Vênus
**Exaltação**: Lua
**Características**: Estável, sensual, persistente, materialista
**Corpo**: Pescoço, garganta
**Palavras-chave**: Estabilidade, prazer, recursos

## GÊMEOS (21/05 - 20/06)
**Elemento**: Ar
**Modalidade**: Mutável
**Regente**: Mercúrio
**Exaltação**: Norte (Nodo Norte)
**Características**: Comunicativo, versátil, curioso, dual
**Corpo**: Braços, mãos, pulmões
**Palavras-chave**: Comunicação, variedade, aprendizagem

## CÂNCER (21/06 - 22/07)
**Elemento**: Água
**Modalidade**: Cardeal
**Regente**: Lua
**Exaltação**: Júpiter
**Características**: Emocional, nutritivo, protetor, sensível
**Corpo**: Estômago, seios
**Palavras-chave**: Emoção, lar, família

## LEÃO (23/07 - 22/08)
**Elemento**: Fogo
**Modalidade**: Fixo
**Regente**: Sol
**Exaltação**: Plutão
**Características**: Criativo, generoso, dramático, orgulhoso
**Corpo**: Coração, coluna
**Palavras-chave**: Criatividade, autoexpressão, liderança

## VIRGEM (23/08 - 22/09)
**Elemento**: Terra
**Modalidade**: Mutável
**Regente**: Mercúrio
**Exaltação**: Mercúrio
**Características**: Analítico, perfeccionista, prático, servicial
**Corpo**: Intestinos, sistema digestivo
**Palavras-chave**: Análise, serviço, saúde

## LIBRA (23/09 - 22/10)
**Elemento**: Ar
**Modalidade**: Cardeal
**Regente**: Vênus
**Exaltação**: Saturno
**Características**: Diplomático, harmonioso, justo, indeciso
**Corpo**: Rins, região lombar
**Palavras-chave**: Equilíbrio, relacionamentos, beleza

## ESCORPIÃO (23/10 - 21/11)
**Elemento**: Água
**Modalidade**: Fixo
**Regente**: Marte/Plutão
**Exaltação**: Urano
**Características**: Intenso, profundo, transformador, secreto
**Corpo**: Órgãos reprodutivos
**Palavras-chave**: Transformação, intensidade, poder

## SAGITÁRIO (22/11 - 21/12)
**Elemento**: Fogo
**Modalidade**: Mutável
**Regente**: Júpiter
**Exaltação**: Sul (Nodo Sul)
**Características**: Filosófico, otimista, aventureiro, franco
**Corpo**: Coxas, fígado
**Palavras-chave**: Expansão, filosofia, viagens

## CAPRICÓRNIO (22/12 - 19/01)
**Elemento**: Terra
**Modalidade**: Cardeal
**Regente**: Saturno
**Exaltação**: Marte
**Características**: Ambicioso, disciplinado, responsável, conservador
**Corpo**: Joelhos, ossos
**Palavras-chave**: Ambição, estrutura, responsabilidade

## AQUÁRIO (20/01 - 18/02)
**Elemento**: Ar
**Modalidade**: Fixo
**Regente**: Saturno/Urano
**Exaltação**: Netuno
**Características**: Inovador, humanitário, rebelde, excêntrico
**Corpo**: Tornozelos, circulação
**Palavras-chave**: Inovação, humanitarismo, liberdade

## PEIXES (19/02 - 20/03)
**Elemento**: Água
**Modalidade**: Mutável
**Regente**: Júpiter/Netuno
**Exaltação**: Vênus
**Características**: Compassivo, intuitivo, sonhador, escapista
**Corpo**: Pés, sistema linfático
**Palavras-chave**: Compaixão, espiritualidade, dissolução
        """,
        "document_type": "signs",
        "metadata": {"category": "zodiac_signs", "language": "pt-BR"},
    },
    {
        "title": "Sect: Mapas Diurnos e Noturnos",
        "content": """
# Sect na Astrologia Tradicional

Sect é um conceito fundamental da astrologia tradicional que divide mapas em diurnos e noturnos.

## Determinação do Sect

### Mapa Diurno
- Sol acima do horizonte (Casas 7, 8, 9, 10, 11, 12)
- Nascimento durante o dia
- Planetas diurnos funcionam melhor

### Mapa Noturno
- Sol abaixo do horizonte (Casas 1, 2, 3, 4, 5, 6)
- Nascimento durante a noite
- Planetas noturnos funcionam melhor

## Classificação dos Planetas por Sect

### Planetas Diurnos (Sect Diurno)
- **Sol**: Luminária diurna
- **Júpiter**: Benéfico diurno
- **Saturno**: Maléfico diurno

### Planetas Noturnos (Sect Noturno)
- **Lua**: Luminária noturna
- **Vênus**: Benéfica noturna
- **Marte**: Maléfico noturno

### Planetas Neutros
- **Mercúrio**: Assume o sect do planeta que o aspecta

## Planeta em Sect vs. Fora de Sect

### Em Sect (In Sect)
- Planeta diurno em mapa diurno
- Planeta noturno em mapa noturno
- Opera de forma mais clara e favorável
- Expressão direta e positiva

### Fora de Sect (Out of Sect)
- Planeta diurno em mapa noturno
- Planeta noturno em mapa diurno
- Opera com mais dificuldade
- Expressão problemática ou exagerada

## Benéficos e Maléficos por Sect

### Benéficos
- **Júpiter em mapa diurno**: Benéfico em sect, máxima benevolência
- **Júpiter em mapa noturno**: Fora de sect, excessivo, exagerado
- **Vênus em mapa noturno**: Benéfica em sect, máxima benevolência
- **Vênus em mapa diurno**: Fora de sect, superficial, vaidosa

### Maléficos
- **Saturno em mapa diurno**: Maléfico em sect, menos destrutivo
- **Saturno em mapa noturno**: Fora de sect, muito destrutivo
- **Marte em mapa noturno**: Maléfico em sect, menos agressivo
- **Marte em mapa diurno**: Fora de sect, muito agressivo e violento

## Aplicação Prática

### Exemplo 1: Saturno
- Em mapa diurno (em sect): Disciplina necessária, estrutura útil
- Em mapa noturno (fora de sect): Depressão, opressão, medo

### Exemplo 2: Marte
- Em mapa noturno (em sect): Coragem controlada, ação efetiva
- Em mapa diurno (fora de sect): Raiva descontrolada, violência

### Exemplo 3: Júpiter
- Em mapa diurno (em sect): Expansão saudável, otimismo realista
- Em mapa noturno (fora de sect): Excesso, arrogância, promessas vazias

## Importância na Interpretação

1. **Temperamento**: Sect modifica o temperamento da pessoa
2. **Qualidade de vida**: Planetas em sect facilitam a vida
3. **Escolha de tempo (Eleições)**: Preferir planetas em sect
4. **Interpretação de casas**: Casa onde cai o regente de sect é importante
        """,
        "document_type": "sect",
        "metadata": {"category": "traditional_techniques", "language": "pt-BR"},
    },
]


async def generate_embedding(text: str, client: AsyncOpenAI) -> list[float] | None:
    """Generate embedding for text using OpenAI."""
    try:
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


async def clear_existing_documents(db: AsyncSession) -> None:
    """Clear all existing documents from database."""
    try:
        logger.info("Clearing existing documents...")
        await db.execute(delete(SearchIndex))
        await db.execute(delete(VectorDocument))
        await db.commit()
        logger.info("✅ Cleared existing documents")
    except Exception as e:
        logger.error(f"Failed to clear documents: {e}")
        await db.rollback()
        raise


async def seed_documents(clear: bool = False, verbose: bool = False) -> None:
    """
    Seed RAG system with astrology knowledge documents.

    Args:
        clear: If True, clear existing documents first
        verbose: Enable verbose logging
    """
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    logger.info("=" * 70)
    logger.info("RAG SYSTEM SEEDING")
    logger.info("=" * 70)
    logger.info(f"Documents to ingest: {len(ASTROLOGY_DOCUMENTS)}")
    logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info("=" * 70)

    # Initialize OpenAI client
    if not settings.OPENAI_API_KEY:
        logger.warning("⚠️  OpenAI API key not configured - embeddings will fail")
        logger.warning("Set OPENAI_API_KEY in .env file")
        return

    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Create embedding function
    async def get_embeddings(text: str) -> list[float] | None:
        return await generate_embedding(text, openai_client)

    # Connect to database
    async with AsyncSessionLocal() as db:
        # Clear existing documents if requested
        if clear:
            await clear_existing_documents(db)

        # Ingest each document
        total_chunks = 0
        failed = 0

        for idx, doc_data in enumerate(ASTROLOGY_DOCUMENTS, 1):
            try:
                logger.info(f"\n[{idx}/{len(ASTROLOGY_DOCUMENTS)}] Ingesting: {doc_data['title']}")

                documents = await document_ingestion_service.ingest_text(
                    db=db,
                    title=doc_data["title"],
                    content=doc_data["content"],
                    document_type=doc_data["document_type"],
                    metadata=doc_data.get("metadata", {}),
                    get_embeddings_func=get_embeddings,
                )

                total_chunks += len(documents)
                logger.info(
                    f"✅ Successfully ingested '{doc_data['title']}' ({len(documents)} chunks)"
                )

            except Exception as e:
                logger.error(f"❌ Failed to ingest '{doc_data['title']}': {e}")
                failed += 1

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("SEEDING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total documents: {len(ASTROLOGY_DOCUMENTS)}")
    logger.info(f"✅ Successfully ingested: {len(ASTROLOGY_DOCUMENTS) - failed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📦 Total chunks created: {total_chunks}")
    logger.info("=" * 70)

    # Get final stats
    async with AsyncSessionLocal() as db:
        stats = await document_ingestion_service.get_ingestion_stats(db)
        logger.info("\nFINAL STATISTICS:")
        logger.info(f"Total documents in database: {stats.get('total_documents', 0)}")
        logger.info(f"Indexed documents: {stats.get('indexed_documents', 0)}")
        logger.info(f"Documents by type: {stats.get('documents_by_type', {})}")

        if stats.get("qdrant_stats"):
            logger.info(f"Qdrant collection info: {stats['qdrant_stats']}")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed RAG system with astrology knowledge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before seeding",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        asyncio.run(seed_documents(clear=args.clear, verbose=args.verbose))
        return 0
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
