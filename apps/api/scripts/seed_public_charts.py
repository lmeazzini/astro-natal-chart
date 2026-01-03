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
        # i18n multilingual fields
        "short_bio_i18n": {
            "pt-BR": "Físico teórico alemão que desenvolveu a teoria da relatividade, um dos dois pilares da física moderna",
            "en-US": "German theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics",
        },
        "meta_title_i18n": {
            "pt-BR": "Albert Einstein - Mapa Astral",
            "en-US": "Albert Einstein - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Albert Einstein - Físico teórico que desenvolveu a teoria da relatividade",
            "en-US": "Albert Einstein's natal chart - Theoretical physicist who developed the theory of relativity",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["cientista", "histórico", "física", "relatividade"],
            "en-US": ["scientist", "historical", "physics", "relativity"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Cofundador da Apple Inc. e Pixar. Visionário que revolucionou a computação pessoal, a música digital e os smartphones",
            "en-US": "Co-founder of Apple Inc. and Pixar. Visionary who revolutionized personal computing, digital music and smartphones",
        },
        "meta_title_i18n": {
            "pt-BR": "Steve Jobs - Mapa Astral",
            "en-US": "Steve Jobs - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Steve Jobs - Empreendedor visionário e cofundador da Apple",
            "en-US": "Steve Jobs' natal chart - Visionary entrepreneur and co-founder of Apple",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["empreendedor", "histórico", "tecnologia", "apple"],
            "en-US": ["entrepreneur", "historical", "technology", "apple"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Pintor, escultor e cofundador do Cubismo. Um dos artistas mais influentes do século XX",
            "en-US": "Painter, sculptor and co-founder of Cubism. One of the most influential artists of the 20th century",
        },
        "meta_title_i18n": {
            "pt-BR": "Pablo Picasso - Mapa Astral",
            "en-US": "Pablo Picasso - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Pablo Picasso - Artista revolucionário e cofundador do Cubismo",
            "en-US": "Pablo Picasso's natal chart - Revolutionary artist and co-founder of Cubism",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["artista", "histórico", "cubismo", "pintor"],
            "en-US": ["artist", "historical", "cubism", "painter"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "O Rei do Rock and Roll. Cantor e ator americano, um dos ícones culturais mais significativos do século XX",
            "en-US": "The King of Rock and Roll. American singer and actor, one of the most significant cultural icons of the 20th century",
        },
        "meta_title_i18n": {
            "pt-BR": "Elvis Presley - Mapa Astral",
            "en-US": "Elvis Presley - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Elvis Presley - Músico lendário conhecido como o Rei do Rock and Roll",
            "en-US": "Elvis Presley's natal chart - Legendary musician known as the King of Rock and Roll",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["músico", "histórico", "rock", "cantor"],
            "en-US": ["musician", "historical", "rock", "singer"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Líder do Movimento de Independência da Índia. Advogado e ativista que liderou a resistência não-violenta contra o domínio britânico",
            "en-US": "Leader of Indian Independence Movement. Lawyer and activist who led non-violent resistance against British rule",
        },
        "meta_title_i18n": {
            "pt-BR": "Mahatma Gandhi - Mapa Astral",
            "en-US": "Mahatma Gandhi - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Mahatma Gandhi - Revolucionário pacífico e líder da independência indiana",
            "en-US": "Mahatma Gandhi's natal chart - Peaceful revolutionary and leader of Indian independence",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "paz", "independência"],
            "en-US": ["leader", "historical", "peace", "independence"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Sir_Winston_Churchill_-_19086236948.jpg",
        "short_bio_i18n": {
            "pt-BR": "Primeiro-Ministro britânico durante a Segunda Guerra Mundial. Estadista, oficial do exército e escritor vencedor do Nobel",
            "en-US": "British Prime Minister during World War II. Statesman, army officer and Nobel Prize-winning writer",
        },
        "meta_title_i18n": {
            "pt-BR": "Winston Churchill - Mapa Astral",
            "en-US": "Winston Churchill - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Winston Churchill - Estadista britânico e líder de guerra",
            "en-US": "Winston Churchill's natal chart - British statesman and wartime leader",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "político", "guerra"],
            "en-US": ["leader", "historical", "politician", "war"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "35º Presidente dos Estados Unidos. Líder carismático da era da Guerra Fria e defensor dos direitos civis",
            "en-US": "35th President of the United States. Charismatic leader of the Cold War era and civil rights advocate",
        },
        "meta_title_i18n": {
            "pt-BR": "John F. Kennedy - Mapa Astral",
            "en-US": "John F. Kennedy - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de John F. Kennedy - 35º Presidente dos EUA e líder carismático",
            "en-US": "John F. Kennedy's natal chart - 35th US President and charismatic leader",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "presidente", "político"],
            "en-US": ["leader", "historical", "president", "politician"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Revolucionário anti-apartheid e Presidente da África do Sul. Passou 27 anos preso e tornou-se símbolo global de resistência",
            "en-US": "Anti-apartheid revolutionary and South African President. Spent 27 years in prison and became a global symbol of resistance",
        },
        "meta_title_i18n": {
            "pt-BR": "Nelson Mandela - Mapa Astral",
            "en-US": "Nelson Mandela - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Nelson Mandela - Revolucionário anti-apartheid e presidente sul-africano",
            "en-US": "Nelson Mandela's natal chart - Anti-apartheid revolutionary and South African president",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "liberdade", "paz"],
            "en-US": ["leader", "historical", "freedom", "peace"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/PRINCESS_DIANA_flag_%285112486207%29.jpg/640px-PRINCESS_DIANA_flag_%285112486207%29.jpg",
        "short_bio_i18n": {
            "pt-BR": "Princesa de Gales. Conhecida como a 'Princesa do Povo', foi uma humanitária dedicada e ícone de moda",
            "en-US": "Princess of Wales. Known as the 'People's Princess', she was a dedicated humanitarian and fashion icon",
        },
        "meta_title_i18n": {
            "pt-BR": "Princesa Diana - Mapa Astral",
            "en-US": "Princess Diana - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal da Princesa Diana - Amada Princesa de Gales e humanitária",
            "en-US": "Princess Diana's natal chart - Beloved Princess of Wales and humanitarian",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["histórico", "líder", "realeza", "humanitária"],
            "en-US": ["historical", "leader", "royalty", "humanitarian"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Marilyn_Monroe_in_How_to_Marry_a_Millionaire.jpg/640px-Marilyn_Monroe_in_How_to_Marry_a_Millionaire.jpg",
        "short_bio_i18n": {
            "pt-BR": "Atriz e ícone cultural. Símbolo de beleza e glamour de Hollywood, uma das atrizes mais famosas da história",
            "en-US": "Actress and cultural icon. Symbol of Hollywood beauty and glamour, one of the most famous actresses in history",
        },
        "meta_title_i18n": {
            "pt-BR": "Marilyn Monroe - Mapa Astral",
            "en-US": "Marilyn Monroe - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Marilyn Monroe - Lendária atriz e ícone cultural",
            "en-US": "Marilyn Monroe's natal chart - Legendary actress and cultural icon",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["atriz", "histórico", "hollywood", "ícone"],
            "en-US": ["actress", "historical", "hollywood", "icon"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Física e química polonesa-francesa. Primeira mulher a ganhar um Prêmio Nobel e única pessoa a ganhar em duas ciências diferentes",
            "en-US": "Polish-French physicist and chemist. First woman to win a Nobel Prize and only person to win in two different sciences",
        },
        "meta_title_i18n": {
            "pt-BR": "Marie Curie - Mapa Astral",
            "en-US": "Marie Curie - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Marie Curie - Física e química, primeira mulher a ganhar um Prêmio Nobel",
            "en-US": "Marie Curie's natal chart - Physicist and chemist, first woman to win a Nobel Prize",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["cientista", "histórico", "física", "química", "nobel"],
            "en-US": ["scientist", "historical", "physics", "chemistry", "nobel"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Inventor e engenheiro sérvio-americano. Pioneiro da eletricidade moderna, conhecido pelo sistema de corrente alternada",
            "en-US": "Serbian-American inventor and engineer. Pioneer of modern electricity, known for the alternating current system",
        },
        "meta_title_i18n": {
            "pt-BR": "Nikola Tesla - Mapa Astral",
            "en-US": "Nikola Tesla - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Nikola Tesla - Inventor e engenheiro elétrico, pioneiro da eletricidade moderna",
            "en-US": "Nikola Tesla's natal chart - Inventor and electrical engineer, pioneer of modern electricity",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["cientista", "histórico", "inventor", "eletricidade"],
            "en-US": ["scientist", "historical", "inventor", "electricity"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Polímata italiano do Renascimento. Pintor, escultor, arquiteto, músico, matemático, engenheiro e inventor",
            "en-US": "Italian Renaissance polymath. Painter, sculptor, architect, musician, mathematician, engineer and inventor",
        },
        "meta_title_i18n": {
            "pt-BR": "Leonardo da Vinci - Mapa Astral",
            "en-US": "Leonardo da Vinci - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Leonardo da Vinci - Polímata do Renascimento, pintor da Mona Lisa",
            "en-US": "Leonardo da Vinci's natal chart - Renaissance polymath, painter of Mona Lisa",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["artista", "histórico", "renascimento", "inventor"],
            "en-US": ["artist", "historical", "renaissance", "inventor"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Pintora mexicana conhecida por seus autorretratos intensos e arte surrealista. Ícone feminista e cultural",
            "en-US": "Mexican painter known for intense self-portraits and surrealist art. Feminist and cultural icon",
        },
        "meta_title_i18n": {
            "pt-BR": "Frida Kahlo - Mapa Astral",
            "en-US": "Frida Kahlo - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Frida Kahlo - Pintora mexicana conhecida por autorretratos intensos",
            "en-US": "Frida Kahlo's natal chart - Mexican painter known for intense self-portraits",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["artista", "histórico", "pintura", "surrealismo"],
            "en-US": ["artist", "historical", "painting", "surrealism"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Pintor pós-impressionista holandês. Criou cerca de 2.100 obras em uma década, incluindo A Noite Estrelada",
            "en-US": "Dutch post-impressionist painter. Created around 2,100 works in a decade, including The Starry Night",
        },
        "meta_title_i18n": {
            "pt-BR": "Vincent van Gogh - Mapa Astral",
            "en-US": "Vincent van Gogh - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Vincent van Gogh - Pintor pós-impressionista, criador de A Noite Estrelada",
            "en-US": "Vincent van Gogh's natal chart - Post-impressionist painter, creator of Starry Night",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["artista", "histórico", "pintura", "pós-impressionismo"],
            "en-US": ["artist", "historical", "painting", "post-impressionism"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Considerado o maior jogador de futebol de todos os tempos. Tricampeão mundial com a Seleção Brasileira",
            "en-US": "Considered the greatest football player of all time. Three-time World Cup champion with Brazil",
        },
        "meta_title_i18n": {
            "pt-BR": "Pelé - Mapa Astral",
            "en-US": "Pelé - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Pelé - O maior jogador de futebol de todos os tempos, tricampeão mundial",
            "en-US": "Pelé's natal chart - Greatest football player of all time, three-time World Cup champion",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["atleta", "histórico", "futebol", "brasil"],
            "en-US": ["athlete", "historical", "football", "brazil"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/3/38/Ayrton_Senna_8_%28cropped%29.jpg",
        "short_bio_i18n": {
            "pt-BR": "Tricampeão mundial de Fórmula 1, considerado um dos maiores pilotos da história do automobilismo",
            "en-US": "Three-time Formula 1 World Champion, considered one of the greatest drivers in motorsport history",
        },
        "meta_title_i18n": {
            "pt-BR": "Ayrton Senna - Mapa Astral",
            "en-US": "Ayrton Senna - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Ayrton Senna - Tricampeão mundial de Fórmula 1",
            "en-US": "Ayrton Senna's natal chart - Three-time Formula 1 World Champion",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["atleta", "histórico", "fórmula 1", "automobilismo"],
            "en-US": ["athlete", "historical", "formula 1", "motorsport"],
        },
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
        "short_bio_i18n": {
            "pt-BR": "Dramaturgo e poeta inglês, considerado o maior escritor da língua inglesa. Autor de Hamlet e Romeu e Julieta",
            "en-US": "English playwright and poet, considered the greatest writer in the English language. Author of Hamlet and Romeo and Juliet",
        },
        "meta_title_i18n": {
            "pt-BR": "William Shakespeare - Mapa Astral",
            "en-US": "William Shakespeare - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de William Shakespeare - O maior escritor da língua inglesa, autor de Hamlet",
            "en-US": "William Shakespeare's natal chart - Greatest writer in English language, author of Hamlet",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["escritor", "histórico", "dramaturgo", "poeta"],
            "en-US": ["writer", "historical", "playwright", "poet"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Machado_de_Assis_aos_57_anos.jpg/640px-Machado_de_Assis_aos_57_anos.jpg",
        "short_bio_i18n": {
            "pt-BR": "Considerado o maior escritor brasileiro. Fundador e primeiro presidente da Academia Brasileira de Letras",
            "en-US": "Considered the greatest Brazilian writer. Founder and first president of the Brazilian Academy of Letters",
        },
        "meta_title_i18n": {
            "pt-BR": "Machado de Assis - Mapa Astral",
            "en-US": "Machado de Assis - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Machado de Assis - O maior escritor brasileiro, fundador da Academia Brasileira de Letras",
            "en-US": "Machado de Assis' natal chart - Greatest Brazilian writer, founder of Brazilian Academy of Letters",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["escritor", "histórico", "literatura", "brasil"],
            "en-US": ["writer", "historical", "literature", "brazil"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/John_Paul_II_Medal_of_Freedom_2004.jpg",
        "short_bio_i18n": {
            "pt-BR": "Papa João Paulo II (1978-2005), Santo. Um dos papas mais influentes da história, líder na queda do comunismo",
            "en-US": "Pope John Paul II (1978-2005), Saint. One of the most influential popes in history, leader in the fall of communism",
        },
        "meta_title_i18n": {
            "pt-BR": "Papa João Paulo II - Mapa Astral",
            "en-US": "Pope John Paul II - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal do Papa João Paulo II - Amado Papa e Santo da Igreja Católica",
            "en-US": "Pope John Paul II's natal chart - Beloved Pope and Saint of the Catholic Church",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "papa", "santo"],
            "en-US": ["leader", "historical", "pope", "saint"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Franciscus_in_2015.jpg",
        "short_bio_i18n": {
            "pt-BR": "Papa Francisco, atual líder da Igreja Católica (2013-presente). Primeiro papa latino-americano, conhecido por sua humildade",
            "en-US": "Pope Francis, current leader of the Catholic Church (2013-present). First Latin American pope, known for his humility",
        },
        "meta_title_i18n": {
            "pt-BR": "Papa Francisco - Mapa Astral",
            "en-US": "Pope Francis - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal do Papa Francisco - Atual Papa conhecido pela humildade e justiça social",
            "en-US": "Pope Francis' natal chart - Current Pope known for humility and social justice",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "papa", "igreja", "argentina"],
            "en-US": ["leader", "pope", "church", "argentina"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/d6/Mother_Teresa_1.jpg",
        "short_bio_i18n": {
            "pt-BR": "Missionária, Prêmio Nobel da Paz (1979), Santa. Fundadora das Missionárias da Caridade, dedicada aos mais pobres",
            "en-US": "Missionary, Nobel Peace Prize (1979), Saint. Founder of the Missionaries of Charity, devoted to the poorest",
        },
        "meta_title_i18n": {
            "pt-BR": "Madre Teresa - Mapa Astral",
            "en-US": "Mother Teresa - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de Madre Teresa - Ganhadora do Prêmio Nobel da Paz e Santa, dedicada a servir os pobres",
            "en-US": "Mother Teresa's natal chart - Nobel Peace Prize winner and Saint, devoted to serving the poor",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["líder", "histórico", "missionária", "santa", "nobel"],
            "en-US": ["leader", "historical", "missionary", "saint", "nobel"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Saint_Francis_of_Assisi_by_Jusepe_de_Ribera.jpg",
        "short_bio_i18n": {
            "pt-BR": "Fundador da Ordem Franciscana, Padroeiro dos Animais e da Ecologia. Um dos santos mais venerados do cristianismo",
            "en-US": "Founder of the Franciscan Order, Patron Saint of Animals and Ecology. One of the most venerated saints in Christianity",
        },
        "meta_title_i18n": {
            "pt-BR": "São Francisco de Assis - Mapa Astral",
            "en-US": "Saint Francis of Assisi - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de São Francisco de Assis - Fundador da Ordem Franciscana e amante da natureza",
            "en-US": "Saint Francis of Assisi's natal chart - Founder of Franciscan Order and lover of nature",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["histórico", "santo", "franciscano", "natureza"],
            "en-US": ["historical", "saint", "franciscan", "nature"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/e/e3/St-thomas-aquinas.jpg",
        "short_bio_i18n": {
            "pt-BR": "Frade dominicano, filósofo e teólogo. Doutor da Igreja, um dos maiores pensadores do cristianismo",
            "en-US": "Dominican friar, philosopher and theologian. Doctor of the Church, one of the greatest thinkers in Christianity",
        },
        "meta_title_i18n": {
            "pt-BR": "São Tomás de Aquino - Mapa Astral",
            "en-US": "Saint Thomas Aquinas - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal de São Tomás de Aquino - Filósofo dominicano e Doutor da Igreja",
            "en-US": "Saint Thomas Aquinas' natal chart - Dominican philosopher and Doctor of the Church",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["histórico", "santo", "filósofo", "teólogo"],
            "en-US": ["historical", "saint", "philosopher", "theologian"],
        },
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
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/d/df/Padre_Pio.jpg",
        "short_bio_i18n": {
            "pt-BR": "Frade capuchinho, místico e santo com estigmas. Conhecido por seus dons de cura e bilocação",
            "en-US": "Capuchin friar, mystic and saint with stigmata. Known for his gifts of healing and bilocation",
        },
        "meta_title_i18n": {
            "pt-BR": "Padre Pio - Mapa Astral",
            "en-US": "Saint Padre Pio - Birth Chart",
        },
        "meta_description_i18n": {
            "pt-BR": "Mapa natal do Padre Pio - Frade místico conhecido por estigmas e cura",
            "en-US": "Saint Padre Pio's natal chart - Mystic friar known for stigmata and healing",
        },
        "meta_keywords_i18n": {
            "pt-BR": ["histórico", "santo", "místico", "estigmas"],
            "en-US": ["historical", "saint", "mystic", "stigmata"],
        },
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
    """Generate astrological chart data for a personality in both languages.

    Returns a dict with language keys: {"en-US": {...}, "pt-BR": {...}}
    This allows the API to return the correct language based on the request.
    """
    # Generate chart data for both languages
    chart_data_en = calculate_birth_chart(
        birth_datetime=personality["birth_datetime"],
        timezone=personality["birth_timezone"],
        latitude=personality["latitude"],
        longitude=personality["longitude"],
        house_system="placidus",
        language="en-US",
    )

    chart_data_pt = calculate_birth_chart(
        birth_datetime=personality["birth_datetime"],
        timezone=personality["birth_timezone"],
        latitude=personality["latitude"],
        longitude=personality["longitude"],
        house_system="placidus",
        language="pt-BR",
    )

    return {
        "en-US": chart_data_en,
        "pt-BR": chart_data_pt,
    }


async def seed_personality(db: AsyncSession, personality: dict[str, Any]) -> None:
    """Seed a single personality with chart (interpretations generated on-demand)."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Processing: {personality['name']}")
    logger.info(f"{'=' * 60}")

    # Generate chart data (bilingual)
    logger.info("Calculating astrological chart (en-US and pt-BR)...")
    chart_data = generate_chart_data(personality)
    en_planets = len(chart_data.get("en-US", {}).get("planets", []))
    logger.success(f"✓ Chart calculated with {en_planets} planets in both languages")

    # Parse location into city and country
    location = personality["location_name"]
    if ", " in location:
        parts = location.split(", ")
        city = parts[0]
        country = parts[-1]
    else:
        city = location
        country = None

    # Create public chart using only i18n fields
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
        # i18n multilingual fields only (no legacy single-language fields)
        short_bio_i18n=personality.get("short_bio_i18n"),
        highlights_i18n=personality.get("highlights_i18n"),
        meta_title_i18n=personality.get("meta_title_i18n"),
        meta_description_i18n=personality.get("meta_description_i18n"),
        meta_keywords_i18n=personality.get("meta_keywords_i18n"),
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

    logger.info(f"\n{'=' * 60}")
    logger.info("PUBLIC CHARTS SEEDING SCRIPT")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total personalities to process: {len(PERSONALITIES)}")
    logger.info(f"Clear existing charts: {clear}")
    logger.info(f"{'=' * 60}\n")

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
            logger.info(f"\n{'=' * 60}")
            logger.info("SEEDING COMPLETE")
            logger.info(f"{'=' * 60}")
            logger.info(f"✓ Success: {success_count}/{len(PERSONALITIES)}")
            if fail_count > 0:
                logger.warning(f"✗ Failed: {fail_count}/{len(PERSONALITIES)}")
            logger.info(f"{'=' * 60}\n")

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
