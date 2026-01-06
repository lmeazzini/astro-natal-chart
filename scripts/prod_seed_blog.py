#!/usr/bin/env python3
"""
Production seed script for blog posts.
Uses DATABASE_URL environment variable.

Run via ECS task or locally with DATABASE_URL set.
"""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import asyncpg


# =============================================================================
# GENERAL BLOG POSTS (Portuguese)
# =============================================================================

GENERAL_POSTS = [
    {
        "title": "Introducao as Casas Astrologicas: O Que Elas Revelam Sobre Sua Vida",
        "slug": "introducao-casas-astrologicas",
        "content": """# Introducao as Casas Astrologicas

As 12 casas astrologicas sao um dos pilares fundamentais da astrologia. Elas representam diferentes areas da vida e fornecem um mapa detalhado de como os planetas influenciam nossa experiencia cotidiana.

## O Que Sao as Casas?

As casas astrologicas sao divisoes do ceu em 12 setores, cada um representando um aspecto especifico da vida humana. Diferente dos signos zodiacais, que sao baseados na posicao do Sol ao longo do ano, as casas sao calculadas com base no momento e local exatos do nascimento.

## As 12 Casas e Seus Significados

### Casa 1 - O Ascendente
A primeira casa representa o "eu", a personalidade, a aparencia fisica e como nos apresentamos ao mundo.

### Casa 2 - Valores e Recursos
Relacionada com dinheiro, posses materiais, valores pessoais e autoestima.

### Casa 3 - Comunicacao
Irmaos, vizinhanca, comunicacao, estudos basicos e viagens curtas.

### Casa 4 - Lar e Familia
O lar, familia, raizes, patrimonio e base emocional.

### Casa 5 - Criatividade
Romance, filhos, criatividade, hobbies e expressao pessoal.

### Casa 6 - Trabalho e Saude
Rotina diaria, trabalho, saude, pets e servico aos outros.

### Casa 7 - Parcerias
Relacionamentos, casamento, parcerias de negocios e contratos.

### Casa 8 - Transformacao
Transformacao profunda, sexualidade, recursos compartilhados e legados.

### Casa 9 - Expansao
Filosofia, ensino superior, viagens longas e espiritualidade.

### Casa 10 - Carreira
Carreira, reputacao publica, autoridade e realizacoes.

### Casa 11 - Comunidade
Amigos, grupos, redes sociais e aspiracoes futuras.

### Casa 12 - Inconsciente
Subconsciente, espiritualidade, isolamento e processos internos.

---

*Quer descobrir as casas do seu mapa natal? Crie seu mapa astrologico gratuitamente em nossa plataforma!*
""",
        "excerpt": "Descubra o significado das 12 casas astrologicas e como elas revelam diferentes areas da sua vida.",
        "category": "Fundamentos",
        "tags": ["casas astrologicas", "mapa natal", "astrologia basica"],
        "is_featured": True,
        "read_time_minutes": 8,
        "language": "pt-BR",
    },
    {
        "title": "Aspectos Planetarios: Como os Planetas Se Comunicam",
        "slug": "aspectos-planetarios-guia",
        "content": """# Aspectos Planetarios: A Linguagem dos Planetas

Os aspectos sao os angulos formados entre os planetas no mapa natal. Eles revelam como diferentes areas de nossa personalidade e vida se relacionam.

## O Que Sao Aspectos?

Aspectos sao medidos em graus e representam a "conversa" entre os planetas.

## Aspectos Principais

### Conjuncao (0)
Quando dois planetas estao no mesmo grau, suas energias se fundem.

### Oposicao (180)
Planetas em lados opostos do zodiaco criam tensao que busca equilibrio.

### Trigono (120)
Aspecto harmonioso que indica talentos naturais e facilidades.

### Quadratura (90)
Tensao que gera acao. Obstaculos que nos forcam a crescer.

### Sextil (60)
Oportunidades que precisam ser aproveitadas ativamente.

---

*Descubra os aspectos do seu mapa e entenda como os planetas conversam em sua carta!*
""",
        "excerpt": "Entenda os aspectos planetarios e como eles revelam a dinamica entre diferentes areas da sua vida.",
        "category": "Fundamentos",
        "tags": ["aspectos", "planetas", "interpretacao"],
        "is_featured": False,
        "read_time_minutes": 7,
        "language": "pt-BR",
    },
    {
        "title": "Retrogradacao de Mercurio: Mito ou Realidade?",
        "slug": "retrogradacao-mercurio",
        "content": """# Retrogradacao de Mercurio: Separando Fato de Ficcao

A retrogradacao de Mercurio e um dos fenomenos astrologicos mais conhecidos. Mas sera que todo o alvoroco e justificado?

## O Que E Retrogradacao?

Retrogradacao e quando um planeta aparenta mover-se para tras no ceu, do ponto de vista da Terra. E uma ilusao otica.

## Mercurio Retrogrado: Os Fatos

Mercurio fica retrogrado cerca de 3 vezes por ano, por aproximadamente 3 semanas cada vez.

### Areas Afetadas
- Comunicacao: Mal-entendidos, falhas
- Tecnologia: Problemas com eletronicos
- Viagens: Atrasos, mudancas de planos
- Contratos: Revisao necessaria

## O Lado Positivo

Mercurio retrogrado e excelente para:
- Revisao
- Reflexao
- Reorganizacao
- Reconexao com o passado

---

*Quer saber quando Mercurio ficara retrogrado? Confira nosso calendario astrologico!*
""",
        "excerpt": "Descubra a verdade sobre Mercurio retrogrado: o que realmente acontece e como se preparar.",
        "category": "Planetas",
        "tags": ["mercurio", "retrogradacao", "planetas retrogrados"],
        "is_featured": True,
        "read_time_minutes": 6,
        "language": "pt-BR",
    },
    {
        "title": "Como Ler Seu Mapa Natal: Guia para Iniciantes",
        "slug": "como-ler-mapa-natal",
        "content": """# Como Ler Seu Mapa Natal: Guia para Iniciantes

Seu mapa natal e como um manual de instrucoes da sua alma. Este guia vai te ensinar o basico.

## O Que e um Mapa Natal?

O mapa natal e uma fotografia do ceu no momento exato do seu nascimento.

## Passo 1: Os Tres Pilares Principais

### Sol
Representa sua essencia, ego, vitalidade.

### Lua
Representa emocoes, necessidades, mundo interior.

### Ascendente
Representa mascara social, primeira impressao.

## Passo 2: Os Planetas

### Planetas Pessoais
- Mercurio: Como voce pensa e se comunica
- Venus: O que voce valoriza, como ama
- Marte: Como voce age e expressa energia

### Planetas Sociais
- Jupiter: Onde voce expande e tem sorte
- Saturno: Suas responsabilidades e licoes

## Passo 3: As Casas

As 12 casas mostram ONDE as energias se manifestam.

## Passo 4: Os Aspectos

Observe como os planetas "conversam".

---

*Pronto para comecar sua jornada astrologica? Crie seu mapa natal gratuitamente!*
""",
        "excerpt": "Aprenda a interpretar seu mapa natal passo a passo. Guia completo para iniciantes.",
        "category": "Tutoriais",
        "tags": ["mapa natal", "iniciantes", "tutorial"],
        "is_featured": True,
        "read_time_minutes": 12,
        "language": "pt-BR",
    },
]


# =============================================================================
# ASTROS E MITOS POSTS
# =============================================================================

ASTROS_E_MITOS = [
    {
        "title": "Saturno - Cronos: O Senhor do Tempo",
        "slug": "saturno-cronos",
        "subtitle": "O Grande Malefico e as Licoes da Limitacao",
        "content": """# Saturno - Cronos

## O Senhor do Tempo

Saturno e o planeta mais distante visivel a olho nu, marcando os limites do mundo conhecido pelos antigos. Seu movimento lento pelo zodiaco (cerca de 29 anos para completar um ciclo) o associou ao tempo, a velhice e as limitacoes.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media do Sol | 9,5 UA |
| Periodo Orbital | 29,5 anos terrestres |
| Periodo de Rotacao | 10,7 horas |
| Diametro | 116.460 km |

## Mitologia

Cronos (Saturno para os romanos) era o mais jovem dos Titas, filho de Urano (Ceu) e Gaia (Terra). Ele destronou seu pai e governou durante a "Era de Ouro".

### A Profecia e a Queda

Cronos recebeu uma profecia de que seria destronado por um de seus filhos. Para evitar isso, ele devorava cada filho ao nascer. Sua esposa Reia conseguiu salvar Zeus, que eventualmente cumpriu a profecia.

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Capricornio e Aquario
- **Exaltacao**: Libra
- **Detrimento**: Cancer e Leao
- **Queda**: Aries

### Natureza
Saturno e frio e seco por natureza, considerado o "Grande Malefico" na tradicao. Representa restricao, disciplina, tempo, estrutura e maturidade.

### Temas Saturnianos
- Tempo e envelhecimento
- Limites e restricoes
- Disciplina e responsabilidade
- Estrutura e ordem
- Licoes dificeis

---

*Descubra onde Saturno esta no seu mapa natal e quais licoes ele traz para sua vida.*
""",
        "excerpt": "Explore a mitologia de Cronos e o significado astrologico de Saturno, o Senhor do Tempo.",
        "category": "Astros e Mitos",
        "tags": ["saturno", "cronos", "mitologia", "planetas"],
        "is_featured": True,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Jupiter - Zeus: O Rei dos Deuses",
        "slug": "jupiter-zeus",
        "subtitle": "O Grande Benefico e a Expansao da Consciencia",
        "content": """# Jupiter - Zeus

## O Rei dos Deuses

Jupiter e o maior planeta do Sistema Solar, um gigante gasoso cuja massa e maior que todos os outros planetas combinados. Os antigos observavam seu brilho magnifico e o associavam a realeza, abundancia e bencaos divinas.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media do Sol | 5,2 UA |
| Periodo Orbital | 11,86 anos terrestres |
| Periodo de Rotacao | 9,9 horas |
| Diametro | 139.820 km |

## Mitologia

Zeus era o rei dos deuses olimpicos, senhor do ceu e do trovao. Filho de Cronos e Reia, ele liderou a revolta contra os Titas.

### Atributos de Zeus
- Raio e trovao
- Aguia
- Cetro real
- Justica divina

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Sagitario e Peixes
- **Exaltacao**: Cancer
- **Detrimento**: Gemeos e Virgem
- **Queda**: Capricornio

### Natureza
Jupiter e quente e umido, o "Grande Benefico". Representa expansao, abundancia, sabedoria, fe e crescimento.

### Temas Jupiterianos
- Expansao e crescimento
- Sorte e oportunidades
- Sabedoria e filosofia
- Fe e espiritualidade
- Viagens e educacao superior

---

*Descubra onde Jupiter esta no seu mapa e onde a vida quer te expandir.*
""",
        "excerpt": "Explore a mitologia de Zeus e o significado astrologico de Jupiter, o Grande Benefico.",
        "category": "Astros e Mitos",
        "tags": ["jupiter", "zeus", "mitologia", "planetas"],
        "is_featured": False,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Marte - Ares: O Deus da Guerra",
        "slug": "marte-ares",
        "subtitle": "O Pequeno Malefico e a Forca da Acao",
        "content": """# Marte - Ares

## O Planeta Vermelho

Marte e o quarto planeta do Sistema Solar, conhecido por sua coloracao avermelhada distintiva causada pelo oxido de ferro em sua superficie. Os antigos associavam essa cor ao sangue e a guerra.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media do Sol | 1,5 UA |
| Periodo Orbital | 687 dias |
| Periodo de Rotacao | 24,6 horas |
| Diametro | 6.779 km |

## Mitologia

Ares (Marte para os romanos) era o deus olimpico da guerra. Filho de Zeus e Hera, era conhecido por sua natureza violenta e impulsiva.

### Ares vs Marte
- Ares grego: temido, associado a violencia
- Marte romano: honrado, protetor de Roma

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Aries e Escorpiao
- **Exaltacao**: Capricornio
- **Detrimento**: Libra e Touro
- **Queda**: Cancer

### Natureza
Marte e quente e seco, o "Pequeno Malefico". Representa acao, energia, coragem, agressividade e desejo.

### Temas Marcianos
- Acao e iniciativa
- Coragem e assertividade
- Competicao e conflito
- Energia fisica e sexual
- Impulso e impaciencia

---

*Descubra onde Marte esta no seu mapa e como voce expressa sua energia vital.*
""",
        "excerpt": "Explore a mitologia de Ares e o significado astrologico de Marte, o Deus da Guerra.",
        "category": "Astros e Mitos",
        "tags": ["marte", "ares", "mitologia", "planetas"],
        "is_featured": False,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Venus - Afrodite: A Deusa do Amor",
        "slug": "venus-afrodite",
        "subtitle": "O Pequeno Benefico e a Beleza da Harmonia",
        "content": """# Venus - Afrodite

## A Estrela da Manha e da Tarde

Venus e o segundo planeta do Sistema Solar e o mais brilhante objeto no ceu apos o Sol e a Lua. Os antigos a conheciam como a "Estrela da Manha" (Lucifer) e "Estrela da Tarde" (Hesperus).

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media do Sol | 0,72 UA |
| Periodo Orbital | 225 dias |
| Periodo de Rotacao | 243 dias |
| Diametro | 12.104 km |

## Mitologia

Afrodite (Venus para os romanos) era a deusa do amor, beleza e fertilidade. Seu nascimento da espuma do mar e uma das imagens mais iconicas da mitologia grega.

### Atributos de Afrodite
- Concha e espuma do mar
- Rosas e mirto
- Pombas e pardais
- Cinto magico

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Touro e Libra
- **Exaltacao**: Peixes
- **Detrimento**: Escorpiao e Aries
- **Queda**: Virgem

### Natureza
Venus e fria e umida, o "Pequeno Benefico". Representa amor, beleza, harmonia, valores e prazer.

### Temas Venusianos
- Amor e relacionamentos
- Beleza e estetica
- Valores e dinheiro
- Prazer e conforto
- Arte e diplomacia

---

*Descubra onde Venus esta no seu mapa e como voce expressa amor e beleza.*
""",
        "excerpt": "Explore a mitologia de Afrodite e o significado astrologico de Venus, a Deusa do Amor.",
        "category": "Astros e Mitos",
        "tags": ["venus", "afrodite", "mitologia", "planetas"],
        "is_featured": True,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Mercurio - Hermes: O Mensageiro dos Deuses",
        "slug": "mercurio-hermes",
        "subtitle": "O Planeta da Comunicacao e do Intelecto",
        "content": """# Mercurio - Hermes

## O Planeta Veloz

Mercurio e o planeta mais proximo do Sol e o mais rapido do Sistema Solar. Seu movimento celere o associou ao mensageiro dos deuses.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media do Sol | 0,39 UA |
| Periodo Orbital | 88 dias |
| Periodo de Rotacao | 59 dias |
| Diametro | 4.879 km |

## Mitologia

Hermes (Mercurio para os romanos) era o mensageiro dos deuses, patrono dos viajantes, comerciantes e ladroes. Nasceu em uma caverna no Monte Cilene.

### Atributos de Hermes
- Caduceu (bastao alado com serpentes)
- Sandalias aladas
- Petaso (chapeu de viajante)
- Bolsa de comerciante

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Gemeos e Virgem
- **Exaltacao**: Virgem
- **Detrimento**: Sagitario e Peixes
- **Queda**: Peixes

### Natureza
Mercurio e neutro, adaptando-se aos planetas com que se associa. Representa comunicacao, intelecto, comercio e movimento.

### Temas Mercuriais
- Comunicacao e linguagem
- Pensamento e raciocinio
- Comercio e negocios
- Viagens curtas
- Aprendizado e curiosidade

---

*Descubra onde Mercurio esta no seu mapa e como voce pensa e se comunica.*
""",
        "excerpt": "Explore a mitologia de Hermes e o significado astrologico de Mercurio, o Mensageiro.",
        "category": "Astros e Mitos",
        "tags": ["mercurio", "hermes", "mitologia", "planetas"],
        "is_featured": False,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Sol - Helios e Apolo: O Centro do Sistema",
        "slug": "sol-helios-apolo",
        "subtitle": "O Luminar Diurno e a Essencia do Ser",
        "content": """# Sol - Helios e Apolo

## O Centro do Nosso Sistema

O Sol e a estrela no centro do nosso sistema planetario, responsavel pela luz e calor que sustentam a vida na Terra. Na astrologia, representa o centro do ser.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Tipo | Estrela ana amarela |
| Diametro | 1.392.700 km |
| Temperatura superficie | 5.500C |
| Idade | 4,6 bilhoes de anos |

## Mitologia

### Helios
Helios era o titan do Sol, que conduzia sua carruagem de fogo atraves do ceu todos os dias.

### Apolo
Apolo, filho de Zeus, tornou-se associado ao Sol. Era o deus da luz, musica, poesia, profecia e cura.

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Leao
- **Exaltacao**: Aries
- **Detrimento**: Aquario
- **Queda**: Libra

### Natureza
O Sol e quente e seco, o luminar diurno. Representa a essencia, o ego, a vitalidade e a identidade consciente.

### Temas Solares
- Identidade e ego
- Vitalidade e saude
- Proposito de vida
- Autoridade e lideranca
- Pai e figuras masculinas

---

*Descubra o signo solar no seu mapa e entenda sua essencia mais profunda.*
""",
        "excerpt": "Explore a mitologia de Helios e Apolo e o significado astrologico do Sol.",
        "category": "Astros e Mitos",
        "tags": ["sol", "helios", "apolo", "mitologia"],
        "is_featured": True,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
    {
        "title": "Lua - Selene e Artemis: A Senhora da Noite",
        "slug": "lua-selene-artemis",
        "subtitle": "O Luminar Noturno e o Mundo das Emocoes",
        "content": """# Lua - Selene e Artemis

## A Senhora da Noite

A Lua e o unico satelite natural da Terra e o objeto mais brilhante do ceu noturno. Suas fases e ciclos influenciaram calendarios e rituais desde tempos imemoriais.

## Dados Astronomicos

| Caracteristica | Valor |
|----------------|-------|
| Distancia media da Terra | 384.400 km |
| Periodo Orbital | 27,3 dias |
| Periodo Sinodico | 29,5 dias |
| Diametro | 3.474 km |

## Mitologia

### Selene
Selene era a tita da Lua, irma de Helios (Sol) e Eos (Aurora). Ela conduzia sua carruagem de prata atraves do ceu noturno.

### Artemis
Artemis, deusa da caca e da Lua crescente, era irma gemea de Apolo. Representava a natureza selvagem e a independencia feminina.

## Significado Astrologico

### Dignidades Essenciais
- **Domicilio**: Cancer
- **Exaltacao**: Touro
- **Detrimento**: Capricornio
- **Queda**: Escorpiao

### Natureza
A Lua e fria e umida, o luminar noturno. Representa as emocoes, instintos, memoria e o inconsciente.

### Temas Lunares
- Emocoes e sentimentos
- Necessidades de seguranca
- Mae e nutricao
- Habitos e instintos
- Memoria e passado

---

*Descubra a Lua no seu mapa e entenda suas necessidades emocionais.*
""",
        "excerpt": "Explore a mitologia de Selene e Artemis e o significado astrologico da Lua.",
        "category": "Astros e Mitos",
        "tags": ["lua", "selene", "artemis", "mitologia"],
        "is_featured": False,
        "read_time_minutes": 10,
        "language": "pt-BR",
    },
]


async def seed_posts():
    """Seed blog posts to production database."""
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return

    # Convert SQLAlchemy URL to asyncpg format
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Check existing posts
        existing = await conn.fetch("SELECT slug FROM blog_posts")
        existing_slugs = {row["slug"] for row in existing}
        print(f"Found {len(existing_slugs)} existing posts")

        all_posts = GENERAL_POSTS + ASTROS_E_MITOS
        created = 0

        for post_data in all_posts:
            if post_data["slug"] in existing_slugs:
                print(f"  Skipping (exists): {post_data['slug']}")
                continue

            post_id = uuid4()
            now = datetime.now(UTC)
            published = now - timedelta(days=created)  # Stagger publish dates

            await conn.execute(
                """
                INSERT INTO blog_posts (
                    id, slug, title, subtitle, content, excerpt, category, tags,
                    featured_image_url, seo_title, seo_description, seo_keywords,
                    published_at, is_featured, read_time_minutes, views_count,
                    locale, translation_key, created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                )
                """,
                post_id,
                post_data["slug"],
                post_data["title"],
                post_data.get("subtitle"),
                post_data["content"],
                post_data["excerpt"],
                post_data["category"],
                post_data["tags"],
                None,  # featured_image_url
                post_data["title"],  # seo_title
                post_data["excerpt"],  # seo_description
                post_data["tags"],  # seo_keywords
                published,
                post_data["is_featured"],
                post_data["read_time_minutes"],
                0,  # views_count
                post_data.get("language", "pt-BR"),  # locale
                post_data["slug"],  # translation_key (same as slug for base posts)
                now,
                now,
            )
            print(f"  Created: {post_data['title']}")
            created += 1

        print(f"\nDone! Created {created} new posts.")

    finally:
        await conn.close()


if __name__ == "__main__":
    print("Seeding blog posts to production...\n")
    asyncio.run(seed_posts())
