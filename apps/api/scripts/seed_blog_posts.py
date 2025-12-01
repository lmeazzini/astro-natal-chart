#!/usr/bin/env python3
"""
Seed script to populate the database with sample blog posts.

Run from the api directory:
    uv run python scripts/seed_blog_posts.py
"""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import asyncpg


async def seed_blog_posts():
    """Create sample blog posts in the database."""
    # Connect directly to PostgreSQL
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="astro",
        password="dev_password",
        database="astro_dev",
    )

    try:
        # Sample blog posts about astrology
        posts = [
            {
                "title": "Introdução às Casas Astrológicas: O Que Elas Revelam Sobre Sua Vida",
                "slug": "introducao-casas-astrologicas",
                "content": """# Introdução às Casas Astrológicas

As 12 casas astrológicas são um dos pilares fundamentais da astrologia. Elas representam diferentes áreas da vida e fornecem um mapa detalhado de como os planetas influenciam nossa experiência cotidiana.

## O Que São as Casas?

As casas astrológicas são divisões do céu em 12 setores, cada um representando um aspecto específico da vida humana. Diferente dos signos zodiacais, que são baseados na posição do Sol ao longo do ano, as casas são calculadas com base no momento e local exatos do nascimento.

## As 12 Casas e Seus Significados

### Casa 1 - O Ascendente
A primeira casa representa o "eu", a personalidade, a aparência física e como nos apresentamos ao mundo. É o ponto mais pessoal do mapa.

### Casa 2 - Valores e Recursos
Relacionada com dinheiro, posses materiais, valores pessoais e autoestima.

### Casa 3 - Comunicação
Irmãos, vizinhança, comunicação, estudos básicos e viagens curtas.

### Casa 4 - Lar e Família
O lar, família, raízes, patrimônio e base emocional.

### Casa 5 - Criatividade
Romance, filhos, criatividade, hobbies e expressão pessoal.

### Casa 6 - Trabalho e Saúde
Rotina diária, trabalho, saúde, pets e serviço aos outros.

### Casa 7 - Parcerias
Relacionamentos, casamento, parcerias de negócios e contratos.

### Casa 8 - Transformação
Transformação profunda, sexualidade, recursos compartilhados e legados.

### Casa 9 - Expansão
Filosofia, ensino superior, viagens longas e espiritualidade.

### Casa 10 - Carreira
Carreira, reputação pública, autoridade e realizações.

### Casa 11 - Comunidade
Amigos, grupos, redes sociais e aspirações futuras.

### Casa 12 - Inconsciente
Subconsciente, espiritualidade, isolamento e processos internos.

## Como Interpretar as Casas

Para interpretar as casas em seu mapa natal:

1. **Identifique os planetas** em cada casa
2. **Observe os signos** que regem as cúspides das casas
3. **Analise os aspectos** que os planetas fazem com outras casas
4. **Considere as casas vazias** - elas não são "ruins", apenas mostram áreas onde há menos foco nesta vida

## Conclusão

As casas astrológicas são ferramentas poderosas para autoconhecimento. Ao compreender como elas funcionam em seu mapa natal, você ganha insights valiosos sobre diferentes aspectos de sua vida e pode trabalhar conscientemente com essas energias.

---

*Quer descobrir as casas do seu mapa natal? Crie seu mapa astrológico gratuitamente em nossa plataforma!*
""",
                "excerpt": "Descubra o significado das 12 casas astrológicas e como elas revelam diferentes áreas da sua vida, desde relacionamentos até carreira e espiritualidade.",
                "category": "Fundamentos",
                "tags": [
                    "casas astrológicas",
                    "mapa natal",
                    "astrologia básica",
                    "autoconhecimento",
                ],
                "featured_image_url": None,
                "seo_title": "Casas Astrológicas: Guia Completo para Iniciantes",
                "seo_description": "Aprenda sobre as 12 casas astrológicas e o que elas revelam sobre diferentes áreas da sua vida. Guia completo para iniciantes em astrologia.",
                "seo_keywords": [
                    "casas astrológicas",
                    "astrologia",
                    "mapa natal",
                    "significado casas",
                ],
                "published_at": datetime.now(UTC) - timedelta(days=7),
                "is_featured": True,
                "read_time_minutes": 8,
            },
            {
                "title": "Aspectos Planetários: Como os Planetas Se Comunicam no Seu Mapa",
                "slug": "aspectos-planetarios-guia-completo",
                "content": """# Aspectos Planetários: A Linguagem dos Planetas

Os aspectos são os ângulos formados entre os planetas no mapa natal. Eles revelam como diferentes áreas de nossa personalidade e vida se relacionam e interagem.

## O Que São Aspectos?

Aspectos são medidos em graus e representam a "conversa" entre os planetas. Alguns aspectos são harmoniosos, outros desafiadores, mas todos são importantes para o desenvolvimento pessoal.

## Aspectos Principais

### Conjunção (0°)
Quando dois planetas estão no mesmo grau, suas energias se fundem. É o aspecto mais poderoso e intenso.

### Oposição (180°)
Planetas em lados opostos do zodíaco criam tensão que busca equilíbrio. Desafio e crescimento.

### Trígono (120°)
Aspecto harmonioso que indica talentos naturais e facilidades. Energia flui suavemente.

### Quadratura (90°)
Tensão que gera ação. Obstáculos que nos forçam a crescer e desenvolver força interior.

### Sextil (60°)
Oportunidades que precisam ser aproveitadas ativamente. Potencial que requer esforço.

## Aspectos Menores

- **Semisextil (30°)**: Pequenos ajustes necessários
- **Semiquadratura (45°)**: Irritações menores que levam ao crescimento
- **Quincunx (150°)**: Necessidade de adaptação e ajuste
- **Sesquiquadrat (135°)**: Tensão que exige liberação criativa

## Como Interpretar os Aspectos

1. **Identifique os planetas envolvidos**: Que áreas da vida estão em diálogo?
2. **Analise o tipo de aspecto**: É harmonioso ou desafiador?
3. **Considere o orbe**: Quanto mais próximo do exato, mais forte o aspecto
4. **Observe se é aplicativo ou separativo**: O aspecto está se formando ou se desfazendo?

## Aspectos Desafiadores São Ruins?

**Não!** Aspectos desafiadores (quadraturas e oposições) são catalisadores de crescimento. Eles nos empurram para fora da zona de conforto e nos forçam a desenvolver novas habilidades.

## Dicas Práticas

- **Trabalhe conscientemente** com aspectos desafiadores
- **Aproveite os talentos** indicados por trígonos
- **Ative os potenciais** dos sextis
- **Busque equilíbrio** nas oposições

## Conclusão

Os aspectos planetários são a "sintaxe" da linguagem astrológica. Aprender a interpretá-los é fundamental para uma leitura profunda do mapa natal.

---

*Descubra os aspectos do seu mapa e entenda como os planetas conversam em sua carta!*
""",
                "excerpt": "Entenda os aspectos planetários e como eles revelam a dinâmica entre diferentes áreas da sua vida. Guia completo de conjunções, trígonos, quadraturas e muito mais.",
                "category": "Fundamentos",
                "tags": ["aspectos", "planetas", "interpretação", "astrologia avançada"],
                "featured_image_url": None,
                "seo_title": "Aspectos Planetários: Guia Completo de Interpretação",
                "seo_description": "Aprenda sobre conjunções, trígonos, quadraturas e outros aspectos planetários. Descubra como interpretar a comunicação entre os planetas no mapa natal.",
                "seo_keywords": [
                    "aspectos planetários",
                    "astrologia",
                    "interpretação",
                    "mapa natal",
                ],
                "published_at": datetime.now(UTC) - timedelta(days=5),
                "is_featured": False,
                "read_time_minutes": 7,
            },
            {
                "title": "Retrogradação de Mercúrio: Mito ou Realidade?",
                "slug": "retrogradacao-mercurio-mito-realidade",
                "content": """# Retrogradação de Mercúrio: Separando Fato de Ficção

A retrogradação de Mercúrio é um dos fenômenos astrológicos mais conhecidos e temidos. Mas será que todo o alvoroço é justificado?

## O Que É Retrogradação?

Retrogradação é quando um planeta aparenta mover-se para trás no céu, do ponto de vista da Terra. É uma ilusão ótica causada pelas diferentes velocidades orbitais.

## Mercúrio Retrógrado: Os Fatos

Mercúrio fica retrógrado cerca de 3 vezes por ano, por aproximadamente 3 semanas cada vez.

### Áreas Afetadas
- **Comunicação**: Mal-entendidos, falhas de comunicação
- **Tecnologia**: Problemas com eletrônicos, software
- **Viagens**: Atrasos, mudanças de planos
- **Contratos**: Revisão necessária antes de assinar
- **Informação**: Retrabalho, revisão de dados

## O Lado Positivo

Mercúrio retrógrado não é só problema! É um período excelente para:

- **Re**visão
- **Re**flexão
- **Re**organização
- **Re**conexão com o passado
- **Re**formulação de ideias

## Como Navegar

### Faça
✅ Revise e edite trabalhos antigos
✅ Faça backups de dados importantes
✅ Reconecte-se com velhos amigos
✅ Reflita sobre decisões importantes
✅ Termine projetos inacabados

### Evite
❌ Assinar contratos importantes sem revisar
❌ Comprar eletrônicos caros
❌ Começar projetos totalmente novos
❌ Tomar decisões impulsivas

## Mercúrio Retrógrado Natal

Se você nasceu durante Mercúrio retrógrado:
- Pensamento introspectivo e único
- Processamento de informação diferenciado
- Necessidade de tempo para digerir informações
- Perspectivas inovadoras

## A Verdade Sobre o "Caos"

Muitos problemas atribuídos a Mercúrio retrógrado são simplesmente:
- Falta de atenção aos detalhes
- Pressa desnecessária
- Não fazer backups regularmente

## Conclusão

Mercúrio retrógrado é um período de introspecção e revisão, não uma sentença de desastre. Use-o sabiamente e você pode se beneficiar muito desta energia.

---

*Quer saber quando Mercúrio ficará retrógrado? Confira nosso calendário astrológico!*
""",
                "excerpt": "Descubra a verdade sobre Mercúrio retrógrado: o que realmente acontece, como se preparar e como aproveitar esta energia para crescimento pessoal.",
                "category": "Planetas",
                "tags": [
                    "mercúrio",
                    "retrogradação",
                    "planetas retrógrados",
                    "calendário astrológico",
                ],
                "featured_image_url": None,
                "seo_title": "Mercúrio Retrógrado: O Que Fazer e O Que Evitar",
                "seo_description": "Entenda Mercúrio retrógrado além dos mitos. Aprenda a navegar este período com sabedoria e transforme desafios em oportunidades de crescimento.",
                "seo_keywords": ["mercúrio retrógrado", "retrogradação", "astrologia", "planetas"],
                "published_at": datetime.now(UTC) - timedelta(days=3),
                "is_featured": True,
                "read_time_minutes": 6,
            },
            {
                "title": "Lua em Cada Signo: Como Suas Emoções Se Expressam",
                "slug": "lua-em-cada-signo-emocoes",
                "content": """# Lua em Cada Signo: O Mapa das Suas Emoções

A Lua no mapa natal representa nossas emoções, necessidades emocionais e como buscamos conforto e segurança. Cada signo traz uma forma única de sentir e processar emoções.

## Por Que a Lua é Importante?

Enquanto o Sol representa quem você é conscientemente, a Lua mostra:
- Suas reações emocionais instintivas
- O que você precisa para se sentir seguro
- Seu mundo interior e privado
- Sua relação com a mãe e o feminino

## Lua nos Signos de Fogo

### Lua em Áries
Emoções intensas e imediatas. Precisa de ação e independência para se sentir bem.

### Lua em Leão
Necessidade de reconhecimento e expressão criativa. Emoções dramáticas e generosas.

### Lua em Sagitário
Otimismo emocional. Precisa de liberdade, aventura e significado para se sentir pleno.

## Lua nos Signos de Terra

### Lua em Touro
Busca estabilidade, conforto físico e sensorialidade. Emoções sólidas e duradouras.

### Lua em Virgem
Processa emoções através da análise e do serviço. Precisa se sentir útil.

### Lua em Capricórnio
Emoções controladas e responsáveis. Necessidade de estrutura e conquistas.

## Lua nos Signos de Ar

### Lua em Gêmeos
Precisa comunicar emoções. Curiosidade emocional e versatilidade de humor.

### Lua em Libra
Busca harmonia e equilíbrio. Emoções dependem do relacionamento com outros.

### Lua em Aquário
Processamento mental das emoções. Necessidade de liberdade emocional e amizade.

## Lua nos Signos de Água

### Lua em Câncer (Domicílio)
Emoções profundas e nutridoras. Forte conexão com lar e família.

### Lua em Escorpião
Intensidade emocional. Transformação através de crises e regeneração.

### Lua em Peixes
Empatia ilimitada. Conexão espiritual e artística com as emoções.

## Como Trabalhar com Sua Lua

1. **Identifique suas necessidades emocionais** pelo signo da Lua
2. **Honre essas necessidades** no dia a dia
3. **Observe seus padrões emocionais** e reações automáticas
4. **Desenvolva inteligência emocional** consciente

## Cuidando da Sua Lua

Cada signo lunar precisa de cuidados específicos:
- **Fogo**: Ação física e criatividade
- **Terra**: Rotina estável e conforto material
- **Ar**: Comunicação e estímulo mental
- **Água**: Expressão emocional e conexão espiritual

## Conclusão

Conhecer sua Lua natal é fundamental para o autoconhecimento emocional. Ao entender e honrar suas necessidades lunares, você vive com mais autenticidade e bem-estar.

---

*Descubra sua Lua natal e entenda melhor seu mundo emocional!*
""",
                "excerpt": "Explore como a Lua em cada signo influencia suas emoções e necessidades. Descubra o que você precisa para se sentir seguro e emocionalmente realizado.",
                "category": "Planetas",
                "tags": ["lua", "signos", "emoções", "autoconhecimento"],
                "featured_image_url": None,
                "seo_title": "Lua em Cada Signo: Guia Completo das Emoções",
                "seo_description": "Entenda como a Lua em cada signo do zodíaco influencia suas emoções, necessidades e formas de buscar segurança emocional. Guia completo e prático.",
                "seo_keywords": ["lua astrológica", "signos", "emoções", "mapa natal"],
                "published_at": datetime.now(UTC) - timedelta(days=1),
                "is_featured": False,
                "read_time_minutes": 10,
            },
            {
                "title": "Como Ler Seu Mapa Natal: Guia Passo a Passo para Iniciantes",
                "slug": "como-ler-mapa-natal-iniciantes",
                "content": """# Como Ler Seu Mapa Natal: Guia para Iniciantes

Seu mapa natal é como um manual de instruções da sua alma. Mas como começar a interpretá-lo? Este guia vai te ensinar o básico passo a passo.

## O Que é um Mapa Natal?

O mapa natal, ou carta astrológica, é uma fotografia do céu no momento exato do seu nascimento. Ele mostra a posição dos planetas, signos e casas naquele instante único.

## Passo 1: Os Três Pilares Principais

Comece identificando:

### Sol
- **Representa**: Sua essência, ego, vitalidade
- **Pergunta**: "Quem sou eu?"
- **Localização**: Olhe para o signo solar

### Lua
- **Representa**: Emoções, necessidades, mundo interior
- **Pergunta**: "O que eu preciso?"
- **Localização**: Verifique o signo lunar

### Ascendente
- **Representa**: Máscara social, primeira impressão
- **Pergunta**: "Como me apresento?"
- **Localização**: Primeira casa, borda esquerda

## Passo 2: Os Planetas Pessoais

### Mercúrio
Como você pensa e se comunica.

### Vênus
O que você valoriza, como ama.

### Marte
Como você age e expressa energia.

## Passo 3: Os Planetas Sociais

### Júpiter
Onde você expande e tem sorte.

### Saturno
Suas responsabilidades e lições.

## Passo 4: Os Planetas Geracionais

### Urano
Inovação e individualidade.

### Netuno
Espiritualidade e imaginação.

### Plutão
Transformação profunda.

## Passo 5: As Casas

As 12 casas mostram **onde** as energias planetárias se manifestam:

1. Casa 1: Personalidade
2. Casa 2: Valores e dinheiro
3. Casa 3: Comunicação
4. Casa 4: Lar e família
5. Casa 5: Criatividade e romance
6. Casa 6: Trabalho e saúde
7. Casa 7: Parcerias
8. Casa 8: Transformação
9. Casa 9: Filosofia e viagens
10. Casa 10: Carreira
11. Casa 11: Amizades
12. Casa 12: Espiritualidade

## Passo 6: Os Aspectos

Observe como os planetas "conversam":
- **Trígono (120°)**: Facilidade
- **Quadratura (90°)**: Desafio
- **Oposição (180°)**: Tensão/equilíbrio
- **Conjunção (0°)**: Fusão de energias

## Passo 7: Juntando Tudo

Para interpretar um planeta:
1. **Planeta**: QUE energia é essa?
2. **Signo**: COMO essa energia se expressa?
3. **Casa**: ONDE essa energia atua?
4. **Aspectos**: Como ela interage com outras energias?

### Exemplo Prático

**Marte em Gêmeos na Casa 3**
- **Marte** (ação, energia)
- **em Gêmeos** (comunicativa, versátil)
- **na Casa 3** (comunicação, estudos)
- **= Ação através da comunicação, energia mental ativa**

## Dicas para Iniciantes

1. **Comece devagar**: Foque nos pilares principais primeiro
2. **Use recursos**: Livros, sites confiáveis, profissionais
3. **Pratique**: Leia mapas de pessoas próximas
4. **Seja paciente**: Astrologia é uma arte complexa
5. **Mantenha a mente aberta**: Não há "bons" ou "maus" mapas

## Erros Comuns a Evitar

❌ Focar apenas no signo solar
❌ Interpretar um planeta isoladamente
❌ Temer planetas "difíceis"
❌ Usar astrologia como desculpa
❌ Ignorar o livre-arbítrio

## Recursos Recomendados

- Gere seu mapa natal gratuito aqui na plataforma
- Livros de astrologia para iniciantes
- Consultas com astrólogos profissionais
- Cursos básicos de astrologia

## Conclusão

Ler seu mapa natal é uma jornada de autoconhecimento que pode durar a vida toda. Comece com o básico e vá aprofundando aos poucos. Cada nova descoberta é uma oportunidade de crescer e se entender melhor.

---

*Pronto para começar sua jornada astrológica? Crie seu mapa natal gratuitamente!*
""",
                "excerpt": "Aprenda a interpretar seu mapa natal passo a passo. Guia completo para iniciantes com explicações claras sobre planetas, signos, casas e aspectos.",
                "category": "Tutoriais",
                "tags": ["mapa natal", "iniciantes", "tutorial", "interpretação"],
                "featured_image_url": None,
                "seo_title": "Como Ler Seu Mapa Natal: Guia Completo para Iniciantes",
                "seo_description": "Aprenda a interpretar seu mapa natal com este guia passo a passo. Descubra o significado de planetas, signos, casas e aspectos de forma simples e prática.",
                "seo_keywords": [
                    "como ler mapa natal",
                    "interpretar mapa natal",
                    "astrologia iniciantes",
                    "tutorial",
                ],
                "published_at": datetime.now(UTC),
                "is_featured": True,
                "read_time_minutes": 12,
            },
        ]

        # Insert posts into database
        for post_data in posts:
            post_id = uuid4()
            now = datetime.now(UTC)

            await conn.execute(
                """
                INSERT INTO blog_posts (
                    id, slug, title, subtitle, content, excerpt, category, tags,
                    featured_image_url, seo_title, seo_description, seo_keywords,
                    published_at, is_featured, read_time_minutes, views_count,
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
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
                post_data.get("featured_image_url"),
                post_data.get("seo_title"),
                post_data.get("seo_description"),
                post_data.get("seo_keywords"),
                post_data["published_at"],
                post_data["is_featured"],
                post_data["read_time_minutes"],
                0,  # views_count
                now,
                now,
            )
            print(f"✓ Created post: {post_data['title']}")

        print(f"\n✅ Successfully created {len(posts)} blog posts!")
        print("\nYou can now view them at:")
        print("  - Frontend: http://localhost:5173/blog")
        print("  - API: http://localhost:8000/api/v1/blog")

    finally:
        await conn.close()


if __name__ == "__main__":
    print("🌟 Seeding blog posts...\n")
    asyncio.run(seed_blog_posts())
