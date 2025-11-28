#!/usr/bin/env python3
"""
Seed public charts with famous personalities, including Catholic Church figures.

This script:
1. Deletes existing public charts and interpretations
2. Adds new personalities with accurate birth data from AstroDatabank
3. Generates astrological charts for each personality
4. Generates AI interpretations in Portuguese and English using RAG system

Usage:
    uv run python scripts/seed_public_charts.py [--clear] [--verbose]

Arguments:
    --clear: Clear existing public charts before seeding (default: False)
    --verbose: Enable verbose logging (default: False)
"""

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.core.database import AsyncSessionLocal
from app.models.public_chart import PublicChart
from app.models.public_chart_interpretation import PublicChartInterpretation
from app.services.astro_service import calculate_birth_chart

# Famous personalities with accurate birth data from AstroDatabank
PERSONALITIES = [
    # Scientists and Thinkers
    {
        "name": "Albert Einstein",
        "slug": "albert-einstein",
        "birth_datetime": datetime(1879, 3, 14, 11, 30, tzinfo=None),
        "birth_timezone": "Europe/Berlin",
        "latitude": 48.4011,
        "longitude": 9.9876,
        "location_name": "Ulm, Germany",
        "categories": ["scientist", "historical"],
        "short_description": "Physicist, Theory of Relativity",
        "meta_description": "Albert Einstein's natal chart - Theoretical physicist who developed the theory of relativity",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Albert_Einstein_Head.jpg",
    },
    {
        "name": "Steve Jobs",
        "slug": "steve-jobs",
        "birth_datetime": datetime(1955, 2, 24, 19, 15, tzinfo=None),
        "birth_timezone": "America/Los_Angeles",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "location_name": "San Francisco, CA, USA",
        "categories": ["entrepreneur", "historical"],
        "short_description": "Co-founder of Apple Inc.",
        "meta_description": "Steve Jobs' natal chart - Visionary entrepreneur and co-founder of Apple",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/dc/Steve_Jobs_Headshot_2010-CROP_%28cropped_2%29.jpg",
    },
    # Artists and Musicians
    {
        "name": "Pablo Picasso",
        "slug": "pablo-picasso",
        "birth_datetime": datetime(1881, 10, 25, 23, 15, tzinfo=None),
        "birth_timezone": "Europe/Madrid",
        "latitude": 36.7213,
        "longitude": -4.4214,
        "location_name": "Málaga, Spain",
        "categories": ["artist", "historical"],
        "short_description": "Painter, Sculptor, Co-founder of Cubism",
        "meta_description": "Pablo Picasso's natal chart - Revolutionary artist and co-founder of Cubism",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/9/98/Pablo_picasso_1.jpg",
    },
    {
        "name": "Elvis Presley",
        "slug": "elvis-presley",
        "birth_datetime": datetime(1935, 1, 8, 4, 35, tzinfo=None),
        "birth_timezone": "America/Chicago",
        "latitude": 34.5965,
        "longitude": -88.6883,
        "location_name": "Tupelo, MS, USA",
        "categories": ["musician", "historical"],
        "short_description": "King of Rock and Roll",
        "meta_description": "Elvis Presley's natal chart - Legendary musician known as the King of Rock and Roll",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/Elvis_Presley_promoting_Jailhouse_Rock.jpg",
    },
    # Political and Historical Leaders
    {
        "name": "Mahatma Gandhi",
        "slug": "mahatma-gandhi",
        "birth_datetime": datetime(1869, 10, 2, 7, 12, tzinfo=None),
        "birth_timezone": "Asia/Kolkata",
        "latitude": 21.7644,
        "longitude": 72.1519,
        "location_name": "Porbandar, India",
        "categories": ["leader", "historical"],
        "short_description": "Leader of Indian Independence Movement",
        "meta_description": "Mahatma Gandhi's natal chart - Peaceful revolutionary and leader of Indian independence",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Mahatma-Gandhi%2C_studio%2C_1931.jpg",
    },
    {
        "name": "Winston Churchill",
        "slug": "winston-churchill",
        "birth_datetime": datetime(1874, 11, 30, 1, 30, tzinfo=None),
        "birth_timezone": "Europe/London",
        "latitude": 51.8783,
        "longitude": -1.3158,
        "location_name": "Woodstock, UK",
        "categories": ["leader", "historical"],
        "short_description": "British Prime Minister during WWII",
        "meta_description": "Winston Churchill's natal chart - British statesman and wartime leader",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Sir_Winston_Churchill_-_19086236948.jpg",
    },
    {
        "name": "John F. Kennedy",
        "slug": "john-f-kennedy",
        "birth_datetime": datetime(1917, 5, 29, 15, 0, tzinfo=None),
        "birth_timezone": "America/New_York",
        "latitude": 42.3601,
        "longitude": -71.0589,
        "location_name": "Brookline, MA, USA",
        "categories": ["leader", "historical"],
        "short_description": "35th President of the United States",
        "meta_description": "John F. Kennedy's natal chart - 35th US President and charismatic leader",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/John_F._Kennedy%2C_White_House_color_photo_portrait.jpg",
    },
    {
        "name": "Nelson Mandela",
        "slug": "nelson-mandela",
        "birth_datetime": datetime(1918, 7, 18, 14, 54, tzinfo=None),
        "birth_timezone": "Africa/Johannesburg",
        "latitude": -31.5497,
        "longitude": 28.7378,
        "location_name": "Mvezo, South Africa",
        "categories": ["leader", "historical"],
        "short_description": "Anti-apartheid Revolutionary and President",
        "meta_description": "Nelson Mandela's natal chart - Anti-apartheid revolutionary and South African president",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/02/Nelson_Mandela_1994.jpg",
    },
    # Icons and Cultural Figures
    {
        "name": "Princess Diana",
        "slug": "princess-diana",
        "birth_datetime": datetime(1961, 7, 1, 19, 45, tzinfo=None),
        "birth_timezone": "Europe/London",
        "latitude": 52.5833,
        "longitude": -1.3333,
        "location_name": "Sandringham, UK",
        "categories": ["historical", "leader"],
        "short_description": "Princess of Wales",
        "meta_description": "Princess Diana's natal chart - Beloved Princess of Wales and humanitarian",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/7/72/Diana%2C_Princess_of_Wales_1997_%282%29.jpg",
    },
    {
        "name": "Marilyn Monroe",
        "slug": "marilyn-monroe",
        "birth_datetime": datetime(1926, 6, 1, 9, 30, tzinfo=None),
        "birth_timezone": "America/Los_Angeles",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "location_name": "Los Angeles, CA, USA",
        "categories": ["actor", "historical"],
        "short_description": "Actress and Cultural Icon",
        "meta_description": "Marilyn Monroe's natal chart - Legendary actress and cultural icon",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Marilyn_Monroe%2C_Korea%2C_1954_cropped.jpg",
    },
    # Additional Scientists
    {
        "name": "Marie Curie",
        "slug": "marie-curie",
        "birth_datetime": datetime(1867, 11, 7, 12, 0, tzinfo=None),
        "birth_timezone": "Europe/Warsaw",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "location_name": "Varsóvia, Polônia",
        "categories": ["scientist", "historical"],
        "short_description": "Física e química polonesa-francesa, primeira mulher a ganhar um Prêmio Nobel e única pessoa a ganhar em duas ciências diferentes",
        "meta_description": "Marie Curie's natal chart - Physicist and chemist, first woman to win a Nobel Prize",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Marie_Curie_c._1920s.jpg",
    },
    {
        "name": "Nikola Tesla",
        "slug": "nikola-tesla",
        "birth_datetime": datetime(1856, 7, 10, 0, 0, tzinfo=None),
        "birth_timezone": "Europe/Belgrade",
        "latitude": 44.5644,
        "longitude": 15.3781,
        "location_name": "Smiljan, Croácia",
        "categories": ["scientist", "historical"],
        "short_description": "Inventor e engenheiro sérvio-americano, pioneiro da eletricidade moderna",
        "meta_description": "Nikola Tesla's natal chart - Inventor and electrical engineer, pioneer of modern electricity",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d4/N.Tesla.JPG",
    },
    # Additional Artists
    {
        "name": "Leonardo da Vinci",
        "slug": "leonardo-da-vinci",
        "birth_datetime": datetime(1452, 4, 15, 21, 40, tzinfo=None),
        "birth_timezone": "Europe/Rome",
        "latitude": 43.7875,
        "longitude": 10.8661,
        "location_name": "Vinci, Itália",
        "categories": ["artist", "historical"],
        "short_description": "Polímata italiano do Renascimento. Pintor, escultor, arquiteto, músico, matemático, engenheiro e inventor",
        "meta_description": "Leonardo da Vinci's natal chart - Renaissance polymath, painter of Mona Lisa",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/b/ba/Leonardo_self.jpg",
    },
    {
        "name": "Frida Kahlo",
        "slug": "frida-kahlo",
        "birth_datetime": datetime(1907, 7, 6, 8, 30, tzinfo=None),
        "birth_timezone": "America/Mexico_City",
        "latitude": 19.4326,
        "longitude": -99.1332,
        "location_name": "Cidade do México, México",
        "categories": ["artist", "historical"],
        "short_description": "Pintora mexicana conhecida por seus autorretratos intensos e arte surrealista",
        "meta_description": "Frida Kahlo's natal chart - Mexican painter known for intense self-portraits",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg",
    },
    {
        "name": "Vincent van Gogh",
        "slug": "vincent-van-gogh",
        "birth_datetime": datetime(1853, 3, 30, 11, 0, tzinfo=None),
        "birth_timezone": "Europe/Amsterdam",
        "latitude": 51.5907,
        "longitude": 4.7794,
        "location_name": "Zundert, Holanda",
        "categories": ["artist", "historical"],
        "short_description": "Pintor pós-impressionista holandês. Criou cerca de 2.100 obras em uma década",
        "meta_description": "Vincent van Gogh's natal chart - Post-impressionist painter, creator of Starry Night",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project_%28454045%29.jpg",
    },
    # Athletes
    {
        "name": "Pelé",
        "slug": "pele",
        "birth_datetime": datetime(1940, 10, 23, 3, 0, tzinfo=None),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -21.1333,
        "longitude": -45.2500,
        "location_name": "Três Corações, Brasil",
        "categories": ["athlete", "historical"],
        "short_description": "Considerado o maior jogador de futebol de todos os tempos. Tricampeão mundial",
        "meta_description": "Pelé's natal chart - Greatest football player of all time, three-time World Cup champion",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Pele_con_brasil_%28cropped%29.jpg",
    },
    {
        "name": "Ayrton Senna",
        "slug": "ayrton-senna",
        "birth_datetime": datetime(1960, 3, 21, 2, 35, tzinfo=None),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "location_name": "São Paulo, Brasil",
        "categories": ["athlete", "historical"],
        "short_description": "Tricampeão mundial de Fórmula 1, considerado um dos maiores pilotos da história",
        "meta_description": "Ayrton Senna's natal chart - Three-time Formula 1 World Champion",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Ayrton_Senna_8_%28cropped%29.jpg",
    },
    # Writers
    {
        "name": "William Shakespeare",
        "slug": "william-shakespeare",
        "birth_datetime": datetime(1564, 4, 23, 4, 0, tzinfo=None),
        "birth_timezone": "Europe/London",
        "latitude": 52.1917,
        "longitude": -1.7083,
        "location_name": "Stratford-upon-Avon, Inglaterra",
        "categories": ["writer", "historical"],
        "short_description": "Dramaturgo e poeta inglês, considerado o maior escritor da língua inglesa",
        "meta_description": "William Shakespeare's natal chart - Greatest writer in English language, author of Hamlet",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Shakespeare.jpg",
    },
    {
        "name": "Machado de Assis",
        "slug": "machado-de-assis",
        "birth_datetime": datetime(1839, 6, 21, 12, 0, tzinfo=None),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -22.9068,
        "longitude": -43.1729,
        "location_name": "Rio de Janeiro, Brasil",
        "categories": ["writer", "historical"],
        "short_description": "Considerado o maior escritor brasileiro. Fundador da Academia Brasileira de Letras",
        "meta_description": "Machado de Assis' natal chart - Greatest Brazilian writer, founder of Brazilian Academy of Letters",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Machado_de_Assis_1904.jpg",
    },
    # Catholic Church Figures
    {
        "name": "Pope John Paul II",
        "slug": "pope-john-paul-ii",
        "birth_datetime": datetime(1920, 5, 18, 17, 0, tzinfo=None),
        "birth_timezone": "Europe/Warsaw",
        "latitude": 49.8344,
        "longitude": 19.9479,
        "location_name": "Wadowice, Poland",
        "categories": ["leader", "historical", "other"],
        "short_description": "Pope (1978-2005), Saint",
        "meta_description": "Pope John Paul II's natal chart - Beloved Pope and Saint of the Catholic Church",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/3/37/Pope_John_Paul_II_%281979%29.jpg",
    },
    {
        "name": "Pope Francis",
        "slug": "pope-francis",
        "birth_datetime": datetime(1936, 12, 17, 21, 0, tzinfo=None),
        "birth_timezone": "America/Argentina/Buenos_Aires",
        "latitude": -34.6037,
        "longitude": -58.3816,
        "location_name": "Buenos Aires, Argentina",
        "categories": ["leader", "other"],
        "short_description": "Current Pope (2013-present)",
        "meta_description": "Pope Francis' natal chart - Current Pope known for humility and social justice",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Pope_Francis_Korea_Haemi_Castle_19_%28cropped%29.jpg",
    },
    {
        "name": "Mother Teresa",
        "slug": "mother-teresa",
        "birth_datetime": datetime(1910, 8, 26, 14, 25, tzinfo=None),
        "birth_timezone": "Europe/Skopje",
        "latitude": 41.9973,
        "longitude": 21.4280,
        "location_name": "Skopje, North Macedonia",
        "categories": ["leader", "historical", "other"],
        "short_description": "Missionary, Nobel Peace Prize, Saint",
        "meta_description": "Mother Teresa's natal chart - Nobel Peace Prize winner and Saint, devoted to serving the poor",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/Mother_Teresa_1.jpg",
    },
    {
        "name": "Saint Francis of Assisi",
        "slug": "saint-francis-of-assisi",
        "birth_datetime": datetime(1181, 9, 26, 12, 0, tzinfo=None),
        "birth_timezone": "Europe/Rome",
        "latitude": 43.0703,
        "longitude": 12.6089,
        "location_name": "Assisi, Italy",
        "categories": ["historical", "other"],
        "short_description": "Founder of Franciscan Order, Patron Saint of Animals",
        "meta_description": "Saint Francis of Assisi's natal chart - Founder of Franciscan Order and lover of nature",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Francesco_d%27Assisi_%28Giovanni_Cimabue%29.jpg",
    },
    {
        "name": "Saint Thomas Aquinas",
        "slug": "saint-thomas-aquinas",
        "birth_datetime": datetime(1225, 1, 28, 12, 0, tzinfo=None),
        "birth_timezone": "Europe/Rome",
        "latitude": 41.4901,
        "longitude": 13.8958,
        "location_name": "Roccasecca, Italy",
        "categories": ["historical", "other"],
        "short_description": "Dominican Friar, Philosopher, Theologian",
        "meta_description": "Saint Thomas Aquinas' natal chart - Dominican philosopher and Doctor of the Church",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/f/f0/St-thomas-aquinas.jpg",
    },
    {
        "name": "Saint Padre Pio",
        "slug": "saint-padre-pio",
        "birth_datetime": datetime(1887, 5, 25, 17, 0, tzinfo=None),
        "birth_timezone": "Europe/Rome",
        "latitude": 41.6361,
        "longitude": 15.0025,
        "location_name": "Pietrelcina, Italy",
        "categories": ["historical", "other"],
        "short_description": "Capuchin Friar, Mystic, Saint with Stigmata",
        "meta_description": "Saint Padre Pio's natal chart - Mystic friar known for stigmata and healing",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/0/05/Padre_Pio_of_Pietrelcina.jpg",
    },
]


async def clear_public_charts(db: AsyncSession) -> None:
    """Delete all existing public charts and interpretations."""
    logger.info("Clearing existing public charts...")

    # Delete interpretations first (foreign key constraint)
    result = await db.execute(select(PublicChartInterpretation))
    interpretations = result.scalars().all()
    for interp in interpretations:
        await db.delete(interp)

    # Delete charts
    result = await db.execute(select(PublicChart))
    charts = result.scalars().all()
    for chart in charts:
        await db.delete(chart)

    await db.commit()
    logger.success(f"Deleted {len(interpretations)} interpretations and {len(charts)} charts")


def generate_chart_data(personality: dict[str, Any]) -> dict[str, Any]:
    """Generate astrological chart data for a personality."""
    chart_data = calculate_birth_chart(
        birth_datetime=personality["birth_datetime"],
        timezone=personality["birth_timezone"],
        latitude=personality["latitude"],
        longitude=personality["longitude"],
        house_system="placidus",
    )

    return chart_data


async def seed_personality(db: AsyncSession, personality: dict[str, Any]) -> None:
    """Seed a single personality with chart (interpretations generated on-demand)."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing: {personality['name']}")
    logger.info(f"{'='*60}")

    # Generate chart data
    logger.info("Calculating astrological chart...")
    chart_data = generate_chart_data(personality)
    logger.success(f"✓ Chart calculated with {len(chart_data.get('planets', []))} planets")

    # Parse location into city and country
    location = personality["location_name"]
    if ", " in location:
        parts = location.split(", ")
        city = parts[0]
        country = parts[-1]
    else:
        city = location
        country = None

    # Create public chart
    chart = PublicChart(
        id=uuid4(),
        full_name=personality["name"],
        slug=personality["slug"],
        birth_datetime=personality["birth_datetime"],
        birth_timezone=personality["birth_timezone"],
        latitude=personality["latitude"],
        longitude=personality["longitude"],
        city=city,
        country=country,
        chart_data=chart_data,
        house_system="placidus",
        category=personality["categories"][0]
        if personality["categories"]
        else None,  # Use first category
        photo_url=personality.get("photo_url"),
        short_bio=personality["short_description"],
        meta_title=f"{personality['name']} - Natal Chart",
        meta_description=personality["meta_description"],
        meta_keywords=personality["categories"],  # Use categories as keywords
        view_count=0,
        is_published=True,  # Publish immediately
        featured=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db.add(chart)
    await db.commit()
    logger.success(f"✓ Saved chart for {personality['name']} (ID: {chart.id})")
    logger.info("  Interpretations will be generated on-demand via API")


async def seed_all_personalities(clear: bool = False, verbose: bool = False) -> None:
    """Seed all personalities with charts (interpretations generated on-demand via API)."""
    if verbose:
        logger.enable("app")
    else:
        logger.disable("app")

    logger.info(f"\n{'='*60}")
    logger.info("PUBLIC CHARTS SEEDING SCRIPT")
    logger.info(f"{'='*60}")
    logger.info(f"Total personalities to process: {len(PERSONALITIES)}")
    logger.info(f"Clear existing charts: {clear}")
    logger.info(f"{'='*60}\n")

    async with AsyncSessionLocal() as db:
        try:
            # Clear existing charts if requested
            if clear:
                await clear_public_charts(db)

            # Seed each personality
            success_count = 0
            fail_count = 0

            for i, personality in enumerate(PERSONALITIES, 1):
                try:
                    logger.info(f"\n[{i}/{len(PERSONALITIES)}] Starting {personality['name']}...")
                    await seed_personality(db, personality)
                    success_count += 1
                    logger.success(
                        f"[{i}/{len(PERSONALITIES)}] ✓ Completed {personality['name']}\n"
                    )

                except Exception as e:
                    fail_count += 1
                    logger.error(
                        f"[{i}/{len(PERSONALITIES)}] ✗ Failed {personality['name']}: {e}\n"
                    )
                    continue

            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("SEEDING COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"✓ Success: {success_count}/{len(PERSONALITIES)}")
            if fail_count > 0:
                logger.warning(f"✗ Failed: {fail_count}/{len(PERSONALITIES)}")
            logger.info(f"{'='*60}\n")

        except Exception as e:
            logger.error(f"Fatal error during seeding: {e}")
            await db.rollback()
            raise


async def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed public charts with famous personalities")
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing public charts before seeding"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    await seed_all_personalities(clear=args.clear, verbose=args.verbose)


if __name__ == "__main__":
    asyncio.run(main())
