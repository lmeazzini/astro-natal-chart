"""
Script to populate initial public charts with famous people's birth data.

Run with: cd apps/api && uv run python scripts/populate_public_charts.py
"""

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Import all models to register them with SQLAlchemy
from app.models import PublicChart  # noqa: F401
from app.models.interpretation import ChartInterpretation  # noqa: F401
from app.services.astro_service import calculate_birth_chart

# Famous people birth data from AstroDatabank and historical records
FAMOUS_PEOPLE = [
    # Scientists
    {
        "slug": "albert-einstein",
        "full_name": "Albert Einstein",
        "category": "scientist",
        "birth_datetime": datetime(1879, 3, 14, 11, 30, tzinfo=ZoneInfo("Europe/Berlin")),
        "birth_timezone": "Europe/Berlin",
        "latitude": 48.4011,
        "longitude": 9.9876,
        "city": "Ulm",
        "country": "Alemanha",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/440px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg",
        "short_bio": "Físico teórico alemão, considerado um dos maiores gênios da história. Desenvolveu a Teoria da Relatividade e ganhou o Prêmio Nobel de Física em 1921.",
        "highlights": [
            "Sol em Peixes confere intuição profunda e pensamento abstrato",
            "Mercúrio conjunto ao Sol favorece a comunicação de ideias complexas",
            "Ascendente em Câncer traz sensibilidade emocional",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "marie-curie",
        "full_name": "Marie Curie",
        "category": "scientist",
        "birth_datetime": datetime(1867, 11, 7, 12, 0, tzinfo=ZoneInfo("Europe/Warsaw")),
        "birth_timezone": "Europe/Warsaw",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "city": "Varsóvia",
        "country": "Polônia",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/440px-Marie_Curie_c._1920s.jpg",
        "short_bio": "Física e química polonesa-francesa, primeira mulher a ganhar um Prêmio Nobel e única pessoa a ganhar em duas ciências diferentes.",
        "highlights": [
            "Sol em Escorpião traz intensidade e determinação inabalável",
            "Vênus em Sagitário favorece a busca pelo conhecimento",
            "Marte em Virgem confere precisão no trabalho científico",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "nikola-tesla",
        "full_name": "Nikola Tesla",
        "category": "scientist",
        "birth_datetime": datetime(1856, 7, 10, 0, 0, tzinfo=ZoneInfo("Europe/Belgrade")),
        "birth_timezone": "Europe/Belgrade",
        "latitude": 44.5644,
        "longitude": 15.3781,
        "city": "Smiljan",
        "country": "Croácia",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/N.Tesla.JPG/440px-N.Tesla.JPG",
        "short_bio": "Inventor e engenheiro sérvio-americano, pioneiro da eletricidade moderna. Inventou o motor de corrente alternada e contribuiu para o desenvolvimento do rádio.",
        "highlights": [
            "Sol em Câncer traz intuição e memória excepcional",
            "Lua pode estar em posição que favorece visualizações mentais",
            "Urano forte no mapa indica genialidade inventiva",
        ],
        "is_published": True,
        "featured": False,
    },
    # Artists
    {
        "slug": "leonardo-da-vinci",
        "full_name": "Leonardo da Vinci",
        "category": "artist",
        "birth_datetime": datetime(1452, 4, 15, 21, 40, tzinfo=ZoneInfo("Europe/Rome")),
        "birth_timezone": "Europe/Rome",
        "latitude": 43.7875,
        "longitude": 10.8661,
        "city": "Vinci",
        "country": "Itália",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Leonardo_self.jpg/440px-Leonardo_self.jpg",
        "short_bio": "Polímata italiano do Renascimento. Pintor, escultor, arquiteto, músico, matemático, engenheiro e inventor. Autor da Mona Lisa e A Última Ceia.",
        "highlights": [
            "Sol em Touro confere talento artístico e apreciação pela beleza",
            "Mercúrio em Áries traz mente rápida e inventiva",
            "Vênus em Touro (domicílio) favorece as artes visuais",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "frida-kahlo",
        "full_name": "Frida Kahlo",
        "category": "artist",
        "birth_datetime": datetime(1907, 7, 6, 8, 30, tzinfo=ZoneInfo("America/Mexico_City")),
        "birth_timezone": "America/Mexico_City",
        "latitude": 19.4326,
        "longitude": -99.1332,
        "city": "Cidade do México",
        "country": "México",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg/440px-Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg",
        "short_bio": "Pintora mexicana conhecida por seus autorretratos intensos e arte surrealista. Sua obra reflete dor, paixão e identidade mexicana.",
        "highlights": [
            "Sol em Câncer traz profundidade emocional em sua arte",
            "Plutão angular confere transformação através do sofrimento",
            "Vênus forte favorece expressão artística única",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "vincent-van-gogh",
        "full_name": "Vincent van Gogh",
        "category": "artist",
        "birth_datetime": datetime(1853, 3, 30, 11, 0, tzinfo=ZoneInfo("Europe/Amsterdam")),
        "birth_timezone": "Europe/Amsterdam",
        "latitude": 51.5907,
        "longitude": 4.7794,
        "city": "Zundert",
        "country": "Holanda",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project_%28454045%29.jpg/440px-Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project_%28454045%29.jpg",
        "short_bio": "Pintor pós-impressionista holandês. Criou cerca de 2.100 obras em uma década, incluindo Noite Estrelada e Os Girassóis.",
        "highlights": [
            "Sol em Áries traz intensidade e originalidade artística",
            "Netuno forte favorece visão artística única",
            "Saturno desafiador indica lutas com depressão",
        ],
        "is_published": True,
        "featured": False,
    },
    # Leaders
    {
        "slug": "mahatma-gandhi",
        "full_name": "Mahatma Gandhi",
        "category": "leader",
        "birth_datetime": datetime(1869, 10, 2, 7, 12, tzinfo=ZoneInfo("Asia/Kolkata")),
        "birth_timezone": "Asia/Kolkata",
        "latitude": 21.6417,
        "longitude": 69.6293,
        "city": "Porbandar",
        "country": "Índia",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Mahatma-Gandhi%2C_studio%2C_1931.jpg/440px-Mahatma-Gandhi%2C_studio%2C_1931.jpg",
        "short_bio": "Líder da independência indiana e defensor da não-violência. Inspirou movimentos de direitos civis e liberdade em todo o mundo.",
        "highlights": [
            "Sol em Libra favorece diplomacia e busca pela justiça",
            "Vênus forte traz carisma e habilidade de inspirar outros",
            "Saturno em Sagitário confere disciplina espiritual",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "nelson-mandela",
        "full_name": "Nelson Mandela",
        "category": "leader",
        "birth_datetime": datetime(1918, 7, 18, 14, 54, tzinfo=ZoneInfo("Africa/Johannesburg")),
        "birth_timezone": "Africa/Johannesburg",
        "latitude": -31.5461,
        "longitude": 28.7892,
        "city": "Mvezo",
        "country": "África do Sul",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Nelson_Mandela_1994.jpg/440px-Nelson_Mandela_1994.jpg",
        "short_bio": "Líder anti-apartheid e primeiro presidente negro da África do Sul. Prêmio Nobel da Paz em 1993.",
        "highlights": [
            "Sol em Câncer confere forte conexão com seu povo",
            "Júpiter em Câncer (exaltado) traz generosidade e proteção",
            "Saturno forte indica capacidade de resistência",
        ],
        "is_published": True,
        "featured": True,
    },
    # Brazilian celebrities
    {
        "slug": "pele",
        "full_name": "Pelé",
        "category": "athlete",
        "birth_datetime": datetime(1940, 10, 23, 3, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -21.1333,
        "longitude": -45.2500,
        "city": "Três Corações",
        "country": "Brasil",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Pele_con_brasil_%28cropped%29.jpg/440px-Pele_con_brasil_%28cropped%29.jpg",
        "short_bio": "Considerado o maior jogador de futebol de todos os tempos. Tricampeão mundial com a Seleção Brasileira.",
        "highlights": [
            "Sol em Escorpião traz intensidade competitiva",
            "Marte forte favorece habilidade atlética excepcional",
            "Júpiter em Touro confere prosperidade e reconhecimento",
        ],
        "is_published": True,
        "featured": True,
    },
    {
        "slug": "ayrton-senna",
        "full_name": "Ayrton Senna",
        "category": "athlete",
        "birth_datetime": datetime(1960, 3, 21, 2, 35, tzinfo=ZoneInfo("America/Sao_Paulo")),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "city": "São Paulo",
        "country": "Brasil",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Ayrton_Senna_8_%28cropped%29.jpg/440px-Ayrton_Senna_8_%28cropped%29.jpg",
        "short_bio": "Tricampeão mundial de Fórmula 1, considerado um dos maiores pilotos da história do automobilismo.",
        "highlights": [
            "Sol em Áries (0°) confere competitividade e liderança",
            "Marte em Aquário traz técnica inovadora",
            "Plutão angular indica intensidade e transformação",
        ],
        "is_published": True,
        "featured": True,
    },
    # Writers
    {
        "slug": "william-shakespeare",
        "full_name": "William Shakespeare",
        "category": "writer",
        "birth_datetime": datetime(1564, 4, 23, 4, 0, tzinfo=ZoneInfo("Europe/London")),
        "birth_timezone": "Europe/London",
        "latitude": 52.1917,
        "longitude": -1.7083,
        "city": "Stratford-upon-Avon",
        "country": "Inglaterra",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/440px-Shakespeare.jpg",
        "short_bio": "Dramaturgo e poeta inglês, considerado o maior escritor da língua inglesa. Autor de Hamlet, Romeu e Julieta e outras obras-primas.",
        "highlights": [
            "Sol em Touro confere talento para expressão sensorial",
            "Mercúrio em Áries traz escrita dinâmica e direta",
            "Vênus favorece temas de amor e beleza",
        ],
        "is_published": True,
        "featured": False,
    },
    {
        "slug": "machado-de-assis",
        "full_name": "Machado de Assis",
        "category": "writer",
        "birth_datetime": datetime(1839, 6, 21, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
        "birth_timezone": "America/Sao_Paulo",
        "latitude": -22.9068,
        "longitude": -43.1729,
        "city": "Rio de Janeiro",
        "country": "Brasil",
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Machado_de_Assis_%28cropped%29.jpg/440px-Machado_de_Assis_%28cropped%29.jpg",
        "short_bio": "Considerado o maior escritor brasileiro. Fundador da Academia Brasileira de Letras, autor de Dom Casmurro e Memórias Póstumas de Brás Cubas.",
        "highlights": [
            "Sol em Gêmeos favorece versatilidade literária",
            "Mercúrio forte traz ironia e análise psicológica aguçada",
            "Saturno confere profundidade filosófica",
        ],
        "is_published": True,
        "featured": True,
    },
]


async def populate_public_charts():
    """Populate the public_charts table with famous people's data."""
    # Create async engine
    db_url = str(settings.DATABASE_URL)
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for person in FAMOUS_PEOPLE:
            # Check if already exists
            stmt = select(PublicChart).where(PublicChart.slug == person["slug"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Skipping {person['full_name']} - already exists")
                continue

            # Calculate chart data
            print(f"Calculating chart for {person['full_name']}...")
            try:
                chart_data = calculate_birth_chart(
                    birth_datetime=person["birth_datetime"],
                    timezone=person["birth_timezone"],
                    latitude=person["latitude"],
                    longitude=person["longitude"],
                    house_system="placidus",
                )
            except Exception as e:
                print(f"  Error calculating chart: {e}")
                continue

            # Create PublicChart
            chart = PublicChart(
                slug=person["slug"],
                full_name=person["full_name"],
                category=person["category"],
                birth_datetime=person["birth_datetime"],
                birth_timezone=person["birth_timezone"],
                latitude=person["latitude"],
                longitude=person["longitude"],
                city=person["city"],
                country=person["country"],
                chart_data=chart_data,
                house_system="placidus",
                photo_url=person.get("photo_url"),
                short_bio=person.get("short_bio"),
                highlights=person.get("highlights"),
                is_published=person.get("is_published", False),
                featured=person.get("featured", False),
            )

            session.add(chart)
            print(f"  Created {person['full_name']}")

        await session.commit()
        print("\nDone! Public charts populated successfully.")


if __name__ == "__main__":
    asyncio.run(populate_public_charts())
