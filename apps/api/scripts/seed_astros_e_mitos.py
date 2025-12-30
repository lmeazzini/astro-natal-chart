#!/usr/bin/env python3
"""
Seed script to populate the database with Astros e Mitos educational blog posts.

Creates 14 posts: 7 traditional planets in Portuguese and English.

Run from the api directory:
    uv run python scripts/seed_astros_e_mitos.py
"""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import asyncpg

# =============================================================================
# PORTUGUESE CONTENT
# =============================================================================

SATURNO_PT = {
    "title": "Saturno - Cronos: O Senhor do Tempo",
    "slug": "saturno-cronos",
    "subtitle": "O Grande Maléfico e as Lições da Limitação",
    "content": """# ♄ Saturno - Cronos

## O Senhor do Tempo

Saturno é o planeta mais distante visível a olho nu, marcando os limites do mundo conhecido pelos antigos. Seu movimento lento pelo zodíaco (cerca de **29 anos** para completar um ciclo) o associou ao tempo, à velhice e às limitações.

Os antigos observavam seu brilho pálido e amarelado, tão diferente do brilho vibrante de Júpiter ou da vermelhidão de Marte. Essa luz fria e distante inspirou associações com a melancolia, a contemplação profunda e a sabedoria que só vem com o tempo.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média do Sol | 9,5 UA (1,4 bilhões km) |
| Período Orbital | 29,5 anos terrestres |
| Período de Rotação | 10,7 horas |
| Diâmetro | 116.460 km (9x Terra) |
| Luas conhecidas | 146 |
| Temperatura média | -178°C |

**Curiosidade observacional:** Saturno é o único planeta cujos anéis são visíveis através de telescópios amadores. Os antigos não conheciam os anéis, mas notavam que o planeta parecia "diferente" - Galileu pensou que eram "orelhas"!

---

## Mitologia

### Cronos (Grego) / Saturno (Romano)

**Cronos** era o mais jovem dos Titãs, filho de **Urano** (Céu) e **Gaia** (Terra). Segundo o mito, Urano odiava seus filhos e os mantinha presos no ventre de Gaia. Ela, em agonia, forjou uma foice de adamanto e pediu ajuda aos filhos. Apenas Cronos teve coragem de agir.

Com a foice, Cronos castrou seu pai quando este descia para deitar-se com Gaia. Do sangue de Urano nasceram as Erínias (Fúrias), os Gigantes e as Melíades. Dos órgãos lançados ao mar, surgiu Afrodite.

Cronos então governou o cosmos durante a **Era de Ouro**, um período de paz e abundância. Porém, uma profecia dizia que ele seria destronado por um de seus filhos, assim como destronara seu pai. Para evitar isso, **Cronos devorava cada filho** que nascia de sua esposa **Reia**.

Reia, desesperada, escondeu o último filho, **Zeus**, na ilha de Creta, dando a Cronos uma pedra enrolada em panos para engolir. Zeus cresceu em segredo e retornou para libertar seus irmãos e liderar a **Titanomaquia**, a guerra contra os Titãs.

**Símbolos e Atributos:**
- **Metal:** Chumbo (pesado, escuro, resistente ao tempo)
- **Cor:** Preto, cinza escuro
- **Dia:** Sábado (Saturday em inglês, do latim *Saturni dies*)
- **Pedra:** Ônix, obsidiana
- **Planta:** Cipreste, mandrágora

**Relações Familiares:**
- **Pais:** Urano e Gaia
- **Esposa:** Reia (Ops em romano)
- **Filhos:** Zeus, Hera, Poseidon, Hades, Deméter, Héstia

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio Diurno** | Capricórnio |
| **Domicílio Noturno** | Aquário |
| **Exaltação** | Libra (21°) |
| **Detrimento** | Câncer, Leão |
| **Queda** | Áries |

### Qualidades Planetárias

- **Seita:** Diurno
- **Natureza:** **Maléfico Maior**
- **Temperamento:** Frio e Seco (Melancólico)
- **Gênero:** Masculino
- **Velocidade:** Lento (movimento médio ~2' por dia)

### O que Saturno Representa

Na carta natal, Saturno indica:

- **Limitações e restrições** que encontramos na vida
- **Responsabilidade e dever** - o que somos obrigados a fazer
- **Estrutura e disciplina** necessárias para realizações
- **Medo e ansiedade** - onde sentimos insegurança
- **Tempo e maturidade** - lições que vêm com a idade
- **Karma** - consequências de ações passadas
- **Pai ou figuras de autoridade**

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectado ou dignificado, Saturno concede:

- **Sabedoria** adquirida pela experiência
- **Paciência** e perseverança
- **Responsabilidade** e confiabilidade
- **Estrutura** e organização
- **Disciplina** para alcançar objetivos de longo prazo
- **Autoridade** merecida e respeitada
- **Longevidade** e estabilidade

### Manifestações Negativas

Quando afligido, Saturno pode indicar:

- **Pessimismo** e depressão
- **Rigidez** excessiva
- **Medo** paralisante
- **Avareza** e mesquinhez
- **Isolamento** e solidão
- **Crueldade** fria
- **Atrasos** e obstáculos

### Profissões Saturninas

- Engenheiros e arquitetos
- Advogados e juízes
- Agricultores e mineradores
- Coveiros e trabalhadores funerários
- Geólogos e arqueólogos
- Administradores e gestores
- Dentistas e ortopedistas
- Monges e eremitas

---

## Citações Clássicas

> "Saturno é frio e seco, melancólico, terrestre, masculino, o maior infortúnio, autor de solitariedade, malícia, lamentações..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Saturno, quando bem colocado, produz homens profundos no pensamento, constantes em seus propósitos, reservados e secretos..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Hesíodo. *Teogonia*.
""",
    "excerpt": "Descubra Saturno, o Senhor do Tempo: sua mitologia como Cronos, significados na astrologia tradicional, dignidades e o que representa na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "saturn", "mythology", "traditional"],
    "seo_title": "Saturno na Astrologia - Cronos, o Senhor do Tempo",
    "seo_description": "Conheça Saturno: mitologia de Cronos, dignidades astrológicas, simbolismo e significados. Guia completo do Grande Maléfico na astrologia tradicional.",
    "seo_keywords": ["saturno", "cronos", "astrologia", "maléfico", "mitologia grega"],
    "is_featured": True,
    "read_time_minutes": 12,
    "locale": "pt-BR",
    "translation_key": "saturn-mythology",
}

JUPITER_PT = {
    "title": "Júpiter - Zeus: O Grande Benéfico",
    "slug": "jupiter-zeus",
    "subtitle": "O Rei dos Deuses e a Expansão da Fortuna",
    "content": """# ♃ Júpiter - Zeus

## O Grande Benéfico

Júpiter é o maior planeta do Sistema Solar, brilhando intensamente no céu noturno. Para os antigos, seu brilho magnífico e constante simbolizava a generosidade divina, a proteção e a abundância. Era o **planeta da fortuna**, trazendo expansão onde quer que se encontrasse.

Com um período orbital de aproximadamente **12 anos**, Júpiter permanece cerca de um ano em cada signo, marcando fases de crescimento e oportunidade.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média do Sol | 5,2 UA (778 milhões km) |
| Período Orbital | 11,86 anos terrestres |
| Período de Rotação | 9,9 horas |
| Diâmetro | 139.820 km (11x Terra) |
| Luas conhecidas | 95 |
| Temperatura média | -110°C |

**Curiosidade observacional:** Júpiter é tão massivo que possui mais de duas vezes a massa de todos os outros planetas combinados. A Grande Mancha Vermelha, visível por telescópios amadores, é uma tempestade maior que a Terra que dura há séculos!

---

## Mitologia

### Zeus (Grego) / Júpiter (Romano)

**Zeus** é o rei dos deuses olímpicos, senhor do céu, dos raios e da justiça. Filho de Cronos e Reia, ele foi salvo do destino de ser devorado pelo pai quando Reia o escondeu em Creta e deu a Cronos uma pedra para engolir.

Crescendo em segredo, Zeus retornou para libertar seus irmãos engolidos por Cronos. Ele fez o pai vomitar os deuses, e juntos travaram a **Titanomaquia** - a grande guerra contra os Titãs. Vitorioso, Zeus dividiu o cosmos com seus irmãos:

- **Zeus:** Céu e Terra
- **Poseidon:** Mares
- **Hades:** Mundo Subterrâneo

Zeus é famoso por suas inúmeras aventuras amorosas, transformando-se em animais, chuva de ouro, e outras formas para conquistar mortais e deusas. Dessas uniões nasceram muitos heróis e divindades.

**Símbolos e Atributos:**
- **Metal:** Estanho
- **Cor:** Azul royal, púrpura
- **Dia:** Quinta-feira (Thursday = Thor's day, equivalente germânico)
- **Pedra:** Safira, ametista
- **Animal:** Águia
- **Planta:** Carvalho

**Relações Familiares:**
- **Pais:** Cronos e Reia
- **Esposa:** Hera (mas com muitas amantes)
- **Filhos notáveis:** Atena, Apolo, Ártemis, Hermes, Dioniso, Heracles, Perseu

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio Diurno** | Sagitário |
| **Domicílio Noturno** | Peixes |
| **Exaltação** | Câncer (15°) |
| **Detrimento** | Gêmeos, Virgem |
| **Queda** | Capricórnio |

### Qualidades Planetárias

- **Seita:** Diurno
- **Natureza:** **Benéfico Maior**
- **Temperamento:** Quente e Úmido (Sanguíneo)
- **Gênero:** Masculino
- **Velocidade:** Moderada (~5' por dia)

### O que Júpiter Representa

Na carta natal, Júpiter indica:

- **Expansão e crescimento** em todos os sentidos
- **Sabedoria e filosofia** - a busca por significado
- **Fé e religião** - crenças e espiritualidade
- **Sorte e fortuna** - oportunidades favoráveis
- **Generosidade** e magnanimidade
- **Viagens longas** - físicas e mentais
- **Ensino superior** e estudos avançados
- **Leis e justiça**

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectado ou dignificado:

- **Otimismo** e confiança
- **Generosidade** e benevolência
- **Sabedoria** e visão ampla
- **Sucesso** em empreendimentos
- **Popularidade** e carisma
- **Proteção** divina
- **Abundância** material e espiritual

### Manifestações Negativas

Quando afligido:

- **Excesso** em todas as formas
- **Arrogância** e presunção
- **Extravagância** e desperdício
- **Fanatismo** religioso
- **Promessas vazias**
- **Ganho de peso** e indulgência
- **Hipocrisia** moral

### Profissões Jupiterianas

- Juízes e advogados
- Professores universitários
- Filósofos e teólogos
- Embaixadores e diplomatas
- Banqueiros (de alto escalão)
- Editores e publicadores
- Clérigos e religiosos
- Viajantes e exploradores

---

## Citações Clássicas

> "Júpiter é quente e úmido, temperado, aéreo, sanguíneo, o Grande Benéfico, autor de temperança, modéstia, sobriedade, justiça..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Júpiter produz homens magnânimos, benevolentes, religiosos, justos, generosos e honrados..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Homero. *Ilíada* e *Odisseia*.
""",
    "excerpt": "Conheça Júpiter, o Grande Benéfico: mitologia de Zeus, rei dos deuses, significados na astrologia tradicional e como ele traz expansão e fortuna à carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "jupiter", "mythology", "traditional"],
    "locale": "pt-BR",
    "translation_key": "jupiter-mythology",
    "seo_title": "Júpiter na Astrologia - Zeus, o Grande Benéfico",
    "seo_description": "Descubra Júpiter: mitologia de Zeus, dignidades astrológicas, simbolismo e significados. Guia completo do Grande Benéfico na astrologia tradicional.",
    "seo_keywords": ["jupiter", "zeus", "astrologia", "benéfico", "mitologia grega"],
    "is_featured": True,
    "read_time_minutes": 11,
}

MARTE_PT = {
    "title": "Marte - Ares: O Guerreiro Celestial",
    "slug": "marte-ares",
    "subtitle": "O Menor Maléfico e a Força da Ação",
    "content": """# ♂ Marte - Ares

## O Guerreiro Celestial

Marte, o Planeta Vermelho, sempre inspirou temor e fascínio. Sua cor sanguínea, visível a olho nu, levou todas as culturas antigas a associá-lo à guerra, ao sangue e à violência. Porém, Marte também representa a **coragem**, a **ação** e a **força vital** necessária para sobreviver.

Com um período orbital de aproximadamente **2 anos**, Marte alterna períodos de visibilidade e ocultação, como um guerreiro que entra e sai do campo de batalha.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média do Sol | 1,52 UA (228 milhões km) |
| Período Orbital | 1,88 anos terrestres |
| Período de Rotação | 24,6 horas |
| Diâmetro | 6.779 km (0,5x Terra) |
| Luas conhecidas | 2 (Fobos e Deimos) |
| Temperatura média | -63°C |

**Curiosidade observacional:** A cor vermelha de Marte vem do óxido de ferro (ferrugem) em sua superfície. Os antigos viam nessa cor o sangue derramado nas batalhas, confirmando sua natureza marcial.

---

## Mitologia

### Ares (Grego) / Marte (Romano)

**Ares** é o deus da guerra, filho de Zeus e Hera. Diferente de Atena, que representava a estratégia militar e a guerra justa, Ares encarnava a **violência bruta**, o **furor** do combate, o prazer pelo sangue e pela destruição.

Curiosamente, Ares era pouco amado pelos outros deuses. Até seu pai Zeus o desprezava. No entanto, ele era adorado em Esparta e em culturas que valorizavam a força militar acima de tudo.

Sua relação mais famosa foi o caso com **Afrodite**, esposa de Hefesto. O ferreiro divino descobriu o adultério e os aprisionou numa rede mágica, expondo-os ao ridículo perante os olímpicos.

**Símbolos e Atributos:**
- **Metal:** Ferro (também aço)
- **Cor:** Vermelho, escarlate
- **Dia:** Terça-feira (Mardi em francês, Martes em espanhol)
- **Pedra:** Rubi, jaspe vermelho
- **Animal:** Lobo, abutre
- **Planta:** Urtiga, pimenta

**Relações Familiares:**
- **Pais:** Zeus e Hera
- **Amante:** Afrodite
- **Filhos:** Fobos (Medo), Deimos (Terror), Eros (com Afrodite, em algumas versões)

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio Diurno** | Escorpião |
| **Domicílio Noturno** | Áries |
| **Exaltação** | Capricórnio (28°) |
| **Detrimento** | Touro, Libra |
| **Queda** | Câncer |

### Qualidades Planetárias

- **Seita:** Noturno
- **Natureza:** **Maléfico Menor**
- **Temperamento:** Quente e Seco (Colérico)
- **Gênero:** Masculino
- **Velocidade:** Rápida (~31' por dia)

### O que Marte Representa

Na carta natal, Marte indica:

- **Energia e vitalidade** - como agimos
- **Coragem e iniciativa** - capacidade de começar
- **Raiva e agressão** - como lidamos com conflitos
- **Desejo e paixão** - impulso sexual
- **Competição** - vontade de vencer
- **Cirurgias e ferimentos** - cortes e traumas
- **Ferramentas e armas** - instrumentos de ação

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectado ou dignificado:

- **Coragem** para enfrentar desafios
- **Energia** e vitalidade abundante
- **Determinação** inabalável
- **Liderança** em situações de crise
- **Honestidade** direta
- **Proteção** ativa dos mais fracos
- **Atletas** e campeões

### Manifestações Negativas

Quando afligido:

- **Violência** e brutalidade
- **Impaciência** destrutiva
- **Raiva** descontrolada
- **Imprudência** e acidentes
- **Conflitos** e inimizades
- **Crueldade** e sadismo
- **Febres** e inflamações

### Profissões Marcianas

- Militares e policiais
- Cirurgiões
- Açougueiros
- Ferreiros e metalúrgicos
- Bombeiros
- Atletas e lutadores
- Mecânicos
- Chefs de cozinha

---

## Citações Clássicas

> "Marte é masculino, noturno, quente e seco, colérico, o Menor Infortúnio, autor de querelas, contendas, guerra..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Marte produz homens audazes, desprezadores do perigo, impetuosos, belicosos, tirânicos..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Homero. *Ilíada*.
""",
    "excerpt": "Descubra Marte, o Guerreiro Celestial: mitologia de Ares, deus da guerra, dignidades astrológicas e como ele representa coragem e ação na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "mars", "mythology", "traditional"],
    "seo_title": "Marte na Astrologia - Ares, o Guerreiro Celestial",
    "seo_description": "Conheça Marte: mitologia de Ares, dignidades astrológicas, simbolismo e significados. Guia completo do Menor Maléfico na astrologia tradicional.",
    "seo_keywords": ["marte", "ares", "astrologia", "guerra", "mitologia grega"],
    "is_featured": False,
    "read_time_minutes": 10,
    "locale": "pt-BR",
    "translation_key": "mars-mythology",
}

SOL_PT = {
    "title": "Sol - Apolo e Hélio: O Luminar Diurno",
    "slug": "sol-apolo-helio",
    "subtitle": "O Centro da Carta e a Essência do Ser",
    "content": """# ☉ Sol - Apolo e Hélio

## O Luminar Diurno

O Sol é o centro do nosso sistema solar e o centro do mapa astrológico. Para os antigos, ele representava a fonte de toda vida, luz e calor. Na astrologia, o Sol simboliza nossa **essência**, nosso **ego** e nossa **vitalidade fundamental**.

Diferente dos outros "planetas" que vagueiam pelo zodíaco, o Sol define o próprio ciclo - o **ano solar** - que é a base do nosso calendário e das estações.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média da Terra | 1 UA (150 milhões km) |
| Período pelo Zodíaco | 1 ano (365,25 dias) |
| Diâmetro | 1.392.700 km (109x Terra) |
| Temperatura superficial | 5.500°C |
| Tipo | Estrela (anã amarela G2V) |

**Curiosidade observacional:** O Sol é tão brilhante que nunca deve ser observado diretamente. Os antigos o viam nascer e se pôr, marcando o ritmo da vida - ativo durante o dia, dormindo à noite.

---

## Mitologia

### Hélio (Titã do Sol) e Apolo (Deus Solar)

Na mitologia grega, havia dois deuses solares:

**Hélio** era o próprio Sol personificado, um Titã que conduzia sua carruagem dourada através do céu, de leste a oeste, todos os dias. Ele tudo via e testemunhava, servindo como testemunha em juramentos.

**Apolo**, filho de Zeus e Leto, era o deus da luz, música, poesia, medicina, profecia e razão. Com o tempo, ele foi identificado com o Sol, especialmente em Roma, onde era chamado **Phoebus Apollo** (Apolo, o Brilhante).

Apolo era considerado o mais belo dos deuses, representando a perfeição masculina. Seu templo em Delfos abrigava o famoso Oráculo, onde a Pítia profetizava em seu nome.

**Símbolos e Atributos:**
- **Metal:** Ouro
- **Cor:** Dourado, amarelo
- **Dia:** Domingo (Sun-day)
- **Pedra:** Rubi, diamante
- **Animal:** Leão, águia
- **Planta:** Louro, girassol

**Relações Familiares (Apolo):**
- **Pais:** Zeus e Leto
- **Irmã gêmea:** Ártemis
- **Filhos notáveis:** Asclépio (deus da medicina), Orfeu

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio** | Leão |
| **Exaltação** | Áries (19°) |
| **Detrimento** | Aquário |
| **Queda** | Libra |

### Qualidades Planetárias

- **Seita:** Luminar Diurno (líder da seita diurna)
- **Natureza:** Moderadamente Benéfico
- **Temperamento:** Quente e Seco (ligeiramente)
- **Gênero:** Masculino
- **Velocidade:** Constante (~59' por dia)

### O que o Sol Representa

Na carta natal, o Sol indica:

- **Identidade e ego** - quem você é essencialmente
- **Vitalidade e saúde** - força de vida
- **Propósito de vida** - o que você veio fazer
- **O pai** ou figura paterna
- **Autoridade e liderança** - capacidade de comandar
- **Fama e reconhecimento** - brilhar perante os outros
- **O coração** - físico e metafórico

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectado ou dignificado:

- **Confiança** e autoestima saudável
- **Generosidade** de espírito
- **Liderança** natural
- **Vitalidade** forte
- **Criatividade** e expressão pessoal
- **Nobreza** de caráter
- **Sucesso** e reconhecimento

### Manifestações Negativas

Quando afligido:

- **Arrogância** e orgulho excessivo
- **Egocentrismo** e narcisismo
- **Tirania** e dominação
- **Fraqueza vital** e problemas cardíacos
- **Necessidade** excessiva de aprovação
- **Cegueira** para próprios defeitos

### Profissões Solares

- Reis e governantes
- Atores e celebridades
- Joalheiros (especialmente ouro)
- Cardiologistas
- Líderes empresariais (CEOs)
- Artistas e criadores
- Políticos de destaque

---

## Citações Clássicas

> "O Sol é a fonte de luz e vida, o coração do céu, o olho do mundo..."
> — Tradição Hermética

> "O Sol é quente, seco, masculino, diurno, autor de honra, glória, dignidade..."
> — **William Lilly**, *Christian Astrology*, 1647

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Ovídio. *Metamorfoses*.
""",
    "excerpt": "Conheça o Sol na astrologia: mitologia de Apolo e Hélio, significado como luminar diurno e como ele representa sua essência e vitalidade na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "sun", "mythology", "traditional"],
    "seo_title": "O Sol na Astrologia - Apolo e Hélio, o Luminar Diurno",
    "seo_description": "Descubra o Sol: mitologia de Apolo, dignidades astrológicas, simbolismo e significados. Guia completo do Luminar Diurno na astrologia tradicional.",
    "seo_keywords": ["sol", "apolo", "helio", "astrologia", "luminar", "mitologia grega"],
    "is_featured": True,
    "read_time_minutes": 10,
    "locale": "pt-BR",
    "translation_key": "sun-mythology",
}

VENUS_PT = {
    "title": "Vênus - Afrodite: A Estrela da Beleza",
    "slug": "venus-afrodite",
    "subtitle": "O Menor Benéfico e os Prazeres da Vida",
    "content": """# ♀ Vênus - Afrodite

## A Estrela da Beleza

Vênus é o planeta mais brilhante no céu noturno, tão luminoso que pode ser visto até durante o dia em condições favoráveis. Os antigos o chamavam de **Estrela da Manhã** (Fósforo/Lúcifer) quando aparecia antes do amanhecer, e **Estrela da Tarde** (Héspero) quando brilhava após o pôr do sol.

Sua beleza e brilho inspiraram associações com o amor, a beleza e todos os prazeres da vida.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média do Sol | 0,72 UA (108 milhões km) |
| Período Orbital | 225 dias terrestres |
| Período Sinódico | 584 dias |
| Diâmetro | 12.104 km (0,95x Terra) |
| Luas | Nenhuma |
| Temperatura média | 464°C (efeito estufa!) |

**Curiosidade observacional:** Vênus passa por fases como a Lua, visíveis por telescópio. Os antigos não sabiam disso, mas notavam suas duas "identidades" - estrela da manhã e da tarde - que por muito tempo acreditaram ser dois astros diferentes.

---

## Mitologia

### Afrodite (Grega) / Vênus (Romana)

**Afrodite** nasceu de forma extraordinária: quando Cronos castrou Urano e lançou seus órgãos ao mar, a espuma (aphros) que se formou deu origem à deusa da beleza e do amor. Ela emergiu das ondas numa concha, já adulta e perfeitamente bela, na ilha de Chipre.

Afrodite era casada com **Hefesto**, o deus ferreiro, coxo e feio. Mas seu coração pertencia a **Ares**, com quem teve um famoso caso amoroso. Além dele, teve muitos amantes, mortais e imortais.

Ela era irresistível - até os deuses não conseguiam resistir ao seu encanto. Possuía um cinto mágico que tornava qualquer pessoa irresistível quando o vestia.

**Símbolos e Atributos:**
- **Metal:** Cobre
- **Cor:** Verde, rosa
- **Dia:** Sexta-feira (Vendredi em francês)
- **Pedra:** Esmeralda, turquesa
- **Animal:** Pomba, cisne
- **Planta:** Rosa, murta

**Relações Familiares:**
- **Nascimento:** Da espuma do mar (ou filha de Zeus e Dione)
- **Esposo:** Hefesto
- **Amantes:** Ares, Adônis, Anquises
- **Filhos:** Eros (com Ares), Eneias (com Anquises)

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio Diurno** | Libra |
| **Domicílio Noturno** | Touro |
| **Exaltação** | Peixes (27°) |
| **Detrimento** | Áries, Escorpião |
| **Queda** | Virgem |

### Qualidades Planetárias

- **Seita:** Noturno
- **Natureza:** **Benéfico Menor**
- **Temperamento:** Fria e Úmida (Fleumática)
- **Gênero:** Feminino
- **Velocidade:** Rápida (similar ao Sol, ~1° por dia)

### O que Vênus Representa

Na carta natal, Vênus indica:

- **Amor e relacionamentos** - como amamos e somos amados
- **Beleza e estética** - senso artístico
- **Prazer e conforto** - o que nos dá alegria
- **Valores** - o que valorizamos
- **Dinheiro** (especialmente ganho por prazer)
- **Harmonia e diplomacia**
- **A mulher amada** ou ideal feminino

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectada ou dignificada:

- **Charme** e magnetismo pessoal
- **Arte** e sensibilidade estética
- **Diplomacia** e tato social
- **Amor** e capacidade de amar
- **Beleza** física e interior
- **Prazer** saudável
- **Prosperidade** e conforto

### Manifestações Negativas

Quando afligida:

- **Vaidade** e superficialidade
- **Preguiça** e indolência
- **Luxúria** e promiscuidade
- **Ciúme** possessivo
- **Extravagância** financeira
- **Dependência** emocional
- **Manipulação** através do charme

### Profissões Venusianas

- Artistas e músicos
- Designers e decoradores
- Esteticistas e cosmetólogos
- Joalheiros
- Diplomatas e mediadores
- Floristas e jardineiros
- Confeiteiros e chocolateiros
- Anfitriões e eventos

---

## Citações Clássicas

> "Vênus é um planeta feminino, temperado, noturno, o Menor Benéfico, autor de alegria, festividade, música, amor..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Vênus produz pessoas amorosas, elegantes, amantes do belo, agradáveis, sociáveis..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Hesíodo. *Teogonia*.
""",
    "excerpt": "Descubra Vênus, a Estrela da Beleza: mitologia de Afrodite, deusa do amor, dignidades astrológicas e como ela representa amor e prazer na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "venus", "mythology", "traditional"],
    "seo_title": "Vênus na Astrologia - Afrodite, a Deusa do Amor",
    "seo_description": "Conheça Vênus: mitologia de Afrodite, dignidades astrológicas, simbolismo e significados. Guia completo do Menor Benéfico na astrologia tradicional.",
    "seo_keywords": ["venus", "afrodite", "astrologia", "amor", "mitologia grega"],
    "is_featured": False,
    "read_time_minutes": 10,
    "locale": "pt-BR",
    "translation_key": "venus-mythology",
}

MERCURIO_PT = {
    "title": "Mercúrio - Hermes: O Mensageiro dos Deuses",
    "slug": "mercurio-hermes",
    "subtitle": "O Planeta Neutro e a Versatilidade da Mente",
    "content": """# ☿ Mercúrio - Hermes

## O Mensageiro dos Deuses

Mercúrio é o planeta mais próximo do Sol e o mais rápido do sistema solar. Para os antigos, seu movimento veloz pelo céu, sempre perto do Sol, fez dele o perfeito **mensageiro** - rápido, ágil e difícil de capturar.

Nunca se afasta mais de 28° do Sol, estando sempre próximo ao luminar diurno, como um secretário leal que transmite ordens e informações.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média do Sol | 0,39 UA (58 milhões km) |
| Período Orbital | 88 dias terrestres |
| Elongação máxima | 28° do Sol |
| Diâmetro | 4.879 km (0,38x Terra) |
| Luas | Nenhuma |
| Temperatura | -180°C a 430°C |

**Curiosidade observacional:** Mercúrio é difícil de observar por estar sempre perto do Sol. Os antigos às vezes pensavam que eram dois planetas diferentes - um da manhã e outro da tarde - até perceberem que era o mesmo astro veloz.

---

## Mitologia

### Hermes (Grego) / Mercúrio (Romano)

**Hermes** era o mensageiro dos deuses, guia das almas para o mundo inferior, e patrono dos viajantes, comerciantes, ladrões e oradores. Filho de **Zeus** e da ninfa **Maia**, ele nasceu numa caverna do Monte Cilene.

Hermes era um deus precoce: ainda bebê, saiu do berço e roubou o gado de seu irmão Apolo. Para se reconciliar, inventou a **lira** a partir de um casco de tartaruga e a deu a Apolo, que ficou encantado. Em troca, recebeu o cajado de pastor - o **caduceu**.

Hermes transitava livremente entre o mundo dos vivos e dos mortos, entre deuses e humanos. Era o único que podia entrar e sair do Hades livremente, guiando as almas (por isso chamado **Psicopompo**).

**Símbolos e Atributos:**
- **Metal:** Mercúrio (azougue)
- **Cor:** Variadas, multicolorido
- **Dia:** Quarta-feira (Mercredi em francês)
- **Pedra:** Ágata, opala
- **Animal:** Galo, tartaruga
- **Objeto:** Caduceu (bastão com duas serpentes)

**Relações Familiares:**
- **Pais:** Zeus e Maia
- **Filhos:** Pã, Hermafrodito

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio Diurno** | Gêmeos |
| **Domicílio Noturno** | Virgem |
| **Exaltação** | Virgem (15°) |
| **Detrimento** | Sagitário, Peixes |
| **Queda** | Peixes |

### Qualidades Planetárias

- **Seita:** **Neutro** (adapta-se à seita do planeta com quem está)
- **Natureza:** **Neutro** (benéfico com benéficos, maléfico com maléficos)
- **Temperamento:** Frio e Seco (quando sozinho)
- **Gênero:** Neutro/Andrógino
- **Velocidade:** Muito rápida (até 2° por dia)

### O que Mercúrio Representa

Na carta natal, Mercúrio indica:

- **Mente e intelecto** - como pensamos
- **Comunicação** - como nos expressamos
- **Escrita e fala** - habilidades verbais
- **Aprendizado** - capacidade de absorver informação
- **Comércio e negócios** - transações
- **Viagens curtas** - deslocamentos locais
- **Irmãos e vizinhos**
- **Habilidade manual** e destreza

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectado ou dignificado:

- **Inteligência** ágil e versátil
- **Eloquência** e comunicação clara
- **Curiosidade** saudável
- **Habilidade** para negócios
- **Destreza** manual
- **Adaptabilidade** a situações
- **Humor** e sagacidade

### Manifestações Negativas

Quando afligido:

- **Mentira** e desonestidade
- **Superficialidade** intelectual
- **Nervosismo** e ansiedade
- **Trapaça** e roubo
- **Fofoca** e maledicência
- **Inconstância** e dispersão
- **Manipulação** verbal

### Profissões Mercurianas

- Escritores e jornalistas
- Professores (ensino básico)
- Comerciantes
- Tradutores e intérpretes
- Secretários e assistentes
- Carteiros e mensageiros
- Astrólogos e magos
- Contadores e matemáticos

---

## Citações Clássicas

> "Mercúrio é o autor de sutileza, truques, invenção, eloquência... é um planeta mutável, participando da natureza de qualquer planeta ao qual esteja configurado."
> — **William Lilly**, *Christian Astrology*, 1647

> "Mercúrio por sua natureza produz homens engenhosos, prudentes, aptos para qualquer conhecimento..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Hinos Homéricos.
""",
    "excerpt": "Conheça Mercúrio, o Mensageiro dos Deuses: mitologia de Hermes, significado como planeta neutro e como ele representa mente e comunicação na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "mercury", "mythology", "traditional"],
    "seo_title": "Mercúrio na Astrologia - Hermes, o Mensageiro",
    "seo_description": "Descubra Mercúrio: mitologia de Hermes, dignidades astrológicas, simbolismo e significados. Guia completo do planeta da mente e comunicação.",
    "seo_keywords": ["mercurio", "hermes", "astrologia", "comunicacao", "mitologia grega"],
    "is_featured": False,
    "read_time_minutes": 10,
    "locale": "pt-BR",
    "translation_key": "mercury-mythology",
}

LUA_PT = {
    "title": "Lua - Ártemis e Selene: O Luminar Noturno",
    "slug": "lua-artemis-selene",
    "subtitle": "A Senhora da Noite e o Mundo Emocional",
    "content": """# ☽ Lua - Ártemis e Selene

## O Luminar Noturno

A Lua é o astro mais próximo da Terra e o único que orbita nosso planeta. Seu ciclo de fases, de nova a cheia e de volta à nova em aproximadamente **29,5 dias**, é a base dos calendários mais antigos e permanece fundamental na astrologia.

Para os antigos, a Lua governava a noite assim como o Sol governava o dia. Ela representava o mundo das emoções, dos sonhos, da fertilidade e dos ciclos naturais da vida.

---

## Dados Astronômicos

| Característica | Valor |
|----------------|-------|
| Distância média da Terra | 384.400 km |
| Período Sinódico (fases) | 29,5 dias |
| Período Sideral | 27,3 dias |
| Diâmetro | 3.474 km (0,27x Terra) |
| Temperatura | -173°C a 127°C |
| Rotação | Síncrona (sempre mostra a mesma face) |

**Curiosidade observacional:** A Lua é o único corpo celeste cujos detalhes são visíveis a olho nu. Os antigos viam os "mares" (planícies escuras) e as "terras" (regiões claras), criando histórias sobre a "face da Lua".

---

## Mitologia

### Selene (Titânide Lunar) e Ártemis (Deusa Lunar)

Na mitologia grega, assim como havia dois deuses solares, havia divindades lunares distintas:

**Selene** era a própria Lua personificada, uma Titânide que conduzia sua carruagem prateada pelo céu noturno. Seu mito mais famoso é seu amor pelo pastor **Endimião**, tão belo que ela pediu a Zeus que o colocasse em sono eterno para preservar sua juventude e visitá-lo toda noite.

**Ártemis**, filha de Zeus e Leto e irmã gêmea de Apolo, era a deusa da caça, da natureza selvagem e das donzelas. Virgem eterna, ela vagava pelas florestas com seu arco prateado, acompanhada de ninfas. Com o tempo, foi identificada com a Lua, especialmente seu aspecto de crescente.

**Hécate** era uma terceira divindade lunar, associada à Lua nova, à magia e aos cruzamentos.

**Símbolos e Atributos:**
- **Metal:** Prata
- **Cor:** Branco, prata, azul pálido
- **Dia:** Segunda-feira (Monday = Moon-day)
- **Pedra:** Pérola, pedra da lua
- **Animal:** Coruja, lebre
- **Planta:** Lírio branco, salgueiro

**Relações Familiares (Ártemis):**
- **Pais:** Zeus e Leto
- **Irmão gêmeo:** Apolo

---

## Na Astrologia Tradicional

### Dignidades Essenciais

| Dignidade | Signo(s) |
|-----------|----------|
| **Domicílio** | Câncer |
| **Exaltação** | Touro (3°) |
| **Detrimento** | Capricórnio |
| **Queda** | Escorpião |

### Qualidades Planetárias

- **Seita:** Luminar Noturno (líder da seita noturna)
- **Natureza:** Moderadamente Benéfica (mutável)
- **Temperamento:** Fria e Úmida (Fleumática)
- **Gênero:** Feminino
- **Velocidade:** A mais rápida (~13° por dia)

### O que a Lua Representa

Na carta natal, a Lua indica:

- **Emoções e sentimentos** - o mundo interior
- **Necessidades básicas** - o que precisamos para nos sentir seguros
- **A mãe** e figuras maternas
- **Memória e passado** - condicionamentos
- **Hábitos** - padrões automáticos
- **O corpo físico** e sua nutrição
- **O povo** e a população em geral
- **Fertilidade** e ciclos naturais

---

## Simbolismo e Arquétipos

### Manifestações Positivas

Quando bem aspectada ou dignificada:

- **Intuição** aguçada
- **Sensibilidade** e empatia
- **Memória** excelente
- **Nutrição** e cuidado
- **Imaginação** rica
- **Receptividade** e acolhimento
- **Fertilidade** (física e criativa)

### Manifestações Negativas

Quando afligida:

- **Instabilidade** emocional
- **Dependência** e carência
- **Melancolia** e depressão
- **Passividade** excessiva
- **Medo** e insegurança
- **Apego** ao passado
- **Hipersensibilidade** paralisante

### Profissões Lunares

- Enfermeiros e cuidadores
- Nutricionistas e chefs
- Parteiras e obstetras
- Historiadores e arquivistas
- Hoteleiros e anfitriões
- Pescadores e marinheiros
- Psicólogos e terapeutas
- Jardineiros e agricultores

---

## As Fases Lunares

| Fase | Significado |
|------|-------------|
| **Lua Nova** | Início, plantio, novos começos |
| **Crescente** | Expansão, crescimento, ação |
| **Cheia** | Culminação, plenitude, colheita |
| **Minguante** | Reflexão, encerramento, limpeza |

---

## Citações Clássicas

> "A Lua é feminina, noturna, fria e úmida, fleumática... ela governa as massas, os viajantes, as mulheres, os pescadores..."
> — **William Lilly**, *Christian Astrology*, 1647

> "A Lua representa a alma, o corpo, a mãe, as viagens, a popularidade..."
> — **Claudius Ptolomeu**, *Tetrabiblos*, séc. II

---

## Referências

- Ptolomeu. *Tetrabiblos*. Século II d.C.
- Lilly, William. *Christian Astrology*. Londres, 1647.
- Carvalho, Olavo de. *Astros e Símbolos*.
- Brandão, Junito. *Mitologia Grega*. Editora Vozes.
- Hinos Homéricos.
""",
    "excerpt": "Descubra a Lua na astrologia: mitologia de Ártemis e Selene, significado como luminar noturno e como ela representa emoções e o mundo interior na carta natal.",
    "category": "stars_and_myths",
    "tags": ["planets", "moon", "mythology", "traditional"],
    "seo_title": "A Lua na Astrologia - Ártemis e Selene, o Luminar Noturno",
    "seo_description": "Conheça a Lua: mitologia de Ártemis e Selene, dignidades astrológicas, fases lunares e significados. Guia completo do Luminar Noturno na astrologia.",
    "seo_keywords": ["lua", "artemis", "selene", "astrologia", "luminar", "mitologia grega"],
    "is_featured": True,
    "read_time_minutes": 11,
    "locale": "pt-BR",
    "translation_key": "moon-mythology",
}

# =============================================================================
# ENGLISH CONTENT
# =============================================================================

SATURN_EN = {
    "title": "Saturn - Cronus: The Lord of Time",
    "slug": "saturn-cronus",
    "subtitle": "The Greater Malefic and the Lessons of Limitation",
    "content": """# ♄ Saturn - Cronus

## The Lord of Time

Saturn is the farthest planet visible to the naked eye, marking the boundaries of the world known to the ancients. Its slow movement through the zodiac (about **29 years** to complete a cycle) associated it with time, old age, and limitations.

The ancients observed its pale, yellowish glow, so different from Jupiter's vibrant brightness or Mars' redness. This cold, distant light inspired associations with melancholy, deep contemplation, and wisdom that only comes with time.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Sun | 9.5 AU (1.4 billion km) |
| Orbital Period | 29.5 Earth years |
| Rotation Period | 10.7 hours |
| Diameter | 116,460 km (9x Earth) |
| Known moons | 146 |
| Average temperature | -178°C |

**Observational curiosity:** Saturn is the only planet whose rings are visible through amateur telescopes. The ancients didn't know about the rings, but noticed the planet looked "different" - Galileo thought they were "ears"!

---

## Mythology

### Cronus (Greek) / Saturn (Roman)

**Cronus** was the youngest of the Titans, son of **Uranus** (Sky) and **Gaia** (Earth). According to myth, Uranus hated his children and kept them imprisoned in Gaia's womb. She, in agony, forged a sickle of adamant and asked her sons for help. Only Cronus had the courage to act.

With the sickle, Cronus castrated his father as he descended to lie with Gaia. From Uranus' blood were born the Erinyes (Furies), the Giants, and the Meliae. From the organs cast into the sea, Aphrodite arose.

Cronus then ruled the cosmos during the **Golden Age**, a period of peace and abundance. However, a prophecy said he would be overthrown by one of his children, just as he had overthrown his father. To prevent this, **Cronus devoured each child** born to his wife **Rhea**.

Rhea, desperate, hid her last child, **Zeus**, on the island of Crete, giving Cronus a stone wrapped in cloth to swallow. Zeus grew in secret and returned to free his siblings and lead the **Titanomachy**, the war against the Titans.

**Symbols and Attributes:**
- **Metal:** Lead (heavy, dark, resistant to time)
- **Color:** Black, dark gray
- **Day:** Saturday (from Latin *Saturni dies*)
- **Stone:** Onyx, obsidian
- **Plant:** Cypress, mandrake

**Family Relations:**
- **Parents:** Uranus and Gaia
- **Wife:** Rhea (Ops in Roman)
- **Children:** Zeus, Hera, Poseidon, Hades, Demeter, Hestia

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Diurnal Domicile** | Capricorn |
| **Nocturnal Domicile** | Aquarius |
| **Exaltation** | Libra (21°) |
| **Detriment** | Cancer, Leo |
| **Fall** | Aries |

### Planetary Qualities

- **Sect:** Diurnal
- **Nature:** **Greater Malefic**
- **Temperament:** Cold and Dry (Melancholic)
- **Gender:** Masculine
- **Speed:** Slow (average motion ~2' per day)

### What Saturn Represents

In the natal chart, Saturn indicates:

- **Limitations and restrictions** we encounter in life
- **Responsibility and duty** - what we are obliged to do
- **Structure and discipline** needed for accomplishments
- **Fear and anxiety** - where we feel insecure
- **Time and maturity** - lessons that come with age
- **Karma** - consequences of past actions
- **Father or authority figures**

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified, Saturn grants:

- **Wisdom** acquired through experience
- **Patience** and perseverance
- **Responsibility** and reliability
- **Structure** and organization
- **Discipline** to achieve long-term goals
- **Authority** earned and respected
- **Longevity** and stability

### Negative Manifestations

When afflicted, Saturn can indicate:

- **Pessimism** and depression
- **Excessive rigidity**
- **Paralyzing fear**
- **Avarice** and stinginess
- **Isolation** and loneliness
- **Cold cruelty**
- **Delays** and obstacles

### Saturnian Professions

- Engineers and architects
- Lawyers and judges
- Farmers and miners
- Undertakers and funeral workers
- Geologists and archaeologists
- Administrators and managers
- Dentists and orthopedists
- Monks and hermits

---

## Classical Quotes

> "Saturn is cold and dry, melancholic, earthly, masculine, the greater infortune, author of solitariness, malice, lamentations..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Saturn, when well placed, produces men profound in thought, constant in their purposes, reserved and secret..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Hesiod. *Theogony*.
- Greek Mythology compilations.
""",
    "excerpt": "Discover Saturn, the Lord of Time: its mythology as Cronus, meanings in traditional astrology, dignities, and what it represents in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "saturn", "mythology", "traditional"],
    "seo_title": "Saturn in Astrology - Cronus, the Lord of Time",
    "seo_description": "Learn about Saturn: Cronus mythology, astrological dignities, symbolism and meanings. Complete guide to the Greater Malefic in traditional astrology.",
    "seo_keywords": ["saturn", "cronus", "astrology", "malefic", "greek mythology"],
    "is_featured": True,
    "read_time_minutes": 12,
    "locale": "en-US",
    "translation_key": "saturn-mythology",
}

JUPITER_EN = {
    "title": "Jupiter - Zeus: The Greater Benefic",
    "slug": "jupiter-zeus-en",
    "subtitle": "The King of Gods and the Expansion of Fortune",
    "content": """# ♃ Jupiter - Zeus

## The Greater Benefic

Jupiter is the largest planet in the Solar System, shining brightly in the night sky. For the ancients, its magnificent and constant brightness symbolized divine generosity, protection, and abundance. It was the **planet of fortune**, bringing expansion wherever it was found.

With an orbital period of approximately **12 years**, Jupiter stays about one year in each sign, marking phases of growth and opportunity.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Sun | 5.2 AU (778 million km) |
| Orbital Period | 11.86 Earth years |
| Rotation Period | 9.9 hours |
| Diameter | 139,820 km (11x Earth) |
| Known moons | 95 |
| Average temperature | -110°C |

**Observational curiosity:** Jupiter is so massive it has more than twice the mass of all other planets combined. The Great Red Spot, visible through amateur telescopes, is a storm larger than Earth that has lasted for centuries!

---

## Mythology

### Zeus (Greek) / Jupiter (Roman)

**Zeus** is the king of the Olympian gods, lord of the sky, thunder, and justice. Son of Cronus and Rhea, he was saved from being devoured by his father when Rhea hid him in Crete and gave Cronus a stone to swallow.

Growing up in secret, Zeus returned to free his swallowed siblings. He made his father vomit up the gods, and together they fought the **Titanomachy** - the great war against the Titans. Victorious, Zeus divided the cosmos with his brothers:

- **Zeus:** Sky and Earth
- **Poseidon:** Seas
- **Hades:** Underworld

Zeus is famous for his numerous love affairs, transforming into animals, golden rain, and other forms to win mortals and goddesses. From these unions were born many heroes and deities.

**Symbols and Attributes:**
- **Metal:** Tin
- **Color:** Royal blue, purple
- **Day:** Thursday (from Germanic Thor, Jupiter's equivalent)
- **Stone:** Sapphire, amethyst
- **Animal:** Eagle
- **Plant:** Oak

**Family Relations:**
- **Parents:** Cronus and Rhea
- **Wife:** Hera (but with many lovers)
- **Notable children:** Athena, Apollo, Artemis, Hermes, Dionysus, Heracles, Perseus

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Diurnal Domicile** | Sagittarius |
| **Nocturnal Domicile** | Pisces |
| **Exaltation** | Cancer (15°) |
| **Detriment** | Gemini, Virgo |
| **Fall** | Capricorn |

### Planetary Qualities

- **Sect:** Diurnal
- **Nature:** **Greater Benefic**
- **Temperament:** Hot and Moist (Sanguine)
- **Gender:** Masculine
- **Speed:** Moderate (~5' per day)

### What Jupiter Represents

In the natal chart, Jupiter indicates:

- **Expansion and growth** in all senses
- **Wisdom and philosophy** - the search for meaning
- **Faith and religion** - beliefs and spirituality
- **Luck and fortune** - favorable opportunities
- **Generosity** and magnanimity
- **Long journeys** - physical and mental
- **Higher education** and advanced studies
- **Laws and justice**

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Optimism** and confidence
- **Generosity** and benevolence
- **Wisdom** and broad vision
- **Success** in endeavors
- **Popularity** and charisma
- **Divine protection**
- **Material and spiritual abundance**

### Negative Manifestations

When afflicted:

- **Excess** in all forms
- **Arrogance** and presumption
- **Extravagance** and waste
- **Religious fanaticism**
- **Empty promises**
- **Weight gain** and indulgence
- **Moral hypocrisy**

### Jupiterian Professions

- Judges and lawyers
- University professors
- Philosophers and theologians
- Ambassadors and diplomats
- Bankers (high-level)
- Editors and publishers
- Clergy and religious leaders
- Travelers and explorers

---

## Classical Quotes

> "Jupiter is hot and moist, temperate, airy, sanguine, the Great Benefic, author of temperance, modesty, sobriety, justice..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Jupiter produces magnanimous, benevolent, religious, just, generous and honored men..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Homer. *Iliad* and *Odyssey*.
- Greek Mythology compilations.
""",
    "excerpt": "Learn about Jupiter, the Greater Benefic: Zeus mythology, king of gods, traditional astrology meanings, and how it brings expansion and fortune to the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "jupiter", "mythology", "traditional"],
    "seo_title": "Jupiter in Astrology - Zeus, the Greater Benefic",
    "seo_description": "Discover Jupiter: Zeus mythology, astrological dignities, symbolism and meanings. Complete guide to the Greater Benefic in traditional astrology.",
    "seo_keywords": ["jupiter", "zeus", "astrology", "benefic", "greek mythology"],
    "is_featured": True,
    "read_time_minutes": 11,
    "locale": "en-US",
    "translation_key": "jupiter-mythology",
}

MARS_EN = {
    "title": "Mars - Ares: The Celestial Warrior",
    "slug": "mars-ares",
    "subtitle": "The Lesser Malefic and the Force of Action",
    "content": """# ♂ Mars - Ares

## The Celestial Warrior

Mars, the Red Planet, has always inspired fear and fascination. Its blood-red color, visible to the naked eye, led all ancient cultures to associate it with war, blood, and violence. However, Mars also represents **courage**, **action**, and the **vital force** necessary to survive.

With an orbital period of approximately **2 years**, Mars alternates periods of visibility and occultation, like a warrior who enters and leaves the battlefield.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Sun | 1.52 AU (228 million km) |
| Orbital Period | 1.88 Earth years |
| Rotation Period | 24.6 hours |
| Diameter | 6,779 km (0.5x Earth) |
| Known moons | 2 (Phobos and Deimos) |
| Average temperature | -63°C |

**Observational curiosity:** Mars' red color comes from iron oxide (rust) on its surface. The ancients saw in this color the blood spilled in battles, confirming its martial nature.

---

## Mythology

### Ares (Greek) / Mars (Roman)

**Ares** is the god of war, son of Zeus and Hera. Unlike Athena, who represented military strategy and just war, Ares embodied **raw violence**, the **fury** of combat, the pleasure of blood and destruction.

Curiously, Ares was not beloved by the other gods. Even his father Zeus despised him. However, he was worshiped in Sparta and in cultures that valued military strength above all.

His most famous relationship was his affair with **Aphrodite**, wife of Hephaestus. The divine blacksmith discovered the adultery and imprisoned them in a magical net, exposing them to ridicule before the Olympians.

**Symbols and Attributes:**
- **Metal:** Iron (also steel)
- **Color:** Red, scarlet
- **Day:** Tuesday (Mardi in French, Martes in Spanish)
- **Stone:** Ruby, red jasper
- **Animal:** Wolf, vulture
- **Plant:** Nettle, pepper

**Family Relations:**
- **Parents:** Zeus and Hera
- **Lover:** Aphrodite
- **Children:** Phobos (Fear), Deimos (Terror), Eros (with Aphrodite, in some versions)

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Diurnal Domicile** | Scorpio |
| **Nocturnal Domicile** | Aries |
| **Exaltation** | Capricorn (28°) |
| **Detriment** | Taurus, Libra |
| **Fall** | Cancer |

### Planetary Qualities

- **Sect:** Nocturnal
- **Nature:** **Lesser Malefic**
- **Temperament:** Hot and Dry (Choleric)
- **Gender:** Masculine
- **Speed:** Fast (~31' per day)

### What Mars Represents

In the natal chart, Mars indicates:

- **Energy and vitality** - how we act
- **Courage and initiative** - ability to begin
- **Anger and aggression** - how we deal with conflicts
- **Desire and passion** - sexual drive
- **Competition** - will to win
- **Surgery and wounds** - cuts and trauma
- **Tools and weapons** - instruments of action

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Courage** to face challenges
- **Abundant energy** and vitality
- **Unwavering determination**
- **Leadership** in crisis situations
- **Direct honesty**
- **Active protection** of the weak
- **Athletes** and champions

### Negative Manifestations

When afflicted:

- **Violence** and brutality
- **Destructive impatience**
- **Uncontrolled anger**
- **Recklessness** and accidents
- **Conflicts** and enmities
- **Cruelty** and sadism
- **Fevers** and inflammation

### Martial Professions

- Military and police
- Surgeons
- Butchers
- Blacksmiths and metalworkers
- Firefighters
- Athletes and fighters
- Mechanics
- Chefs

---

## Classical Quotes

> "Mars is masculine, nocturnal, hot and dry, choleric, the Lesser Infortune, author of quarrels, contentions, war..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Mars produces bold men, despisers of danger, impetuous, warlike, tyrannical..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Homer. *Iliad*.
- Greek Mythology compilations.
""",
    "excerpt": "Discover Mars, the Celestial Warrior: Ares mythology, god of war, astrological dignities and how it represents courage and action in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "mars", "mythology", "traditional"],
    "seo_title": "Mars in Astrology - Ares, the Celestial Warrior",
    "seo_description": "Learn about Mars: Ares mythology, astrological dignities, symbolism and meanings. Complete guide to the Lesser Malefic in traditional astrology.",
    "seo_keywords": ["mars", "ares", "astrology", "war", "greek mythology"],
    "locale": "en-US",
    "translation_key": "mars-mythology",
    "is_featured": False,
    "read_time_minutes": 10,
}

SUN_EN = {
    "title": "The Sun - Apollo and Helios: The Diurnal Luminary",
    "slug": "sun-apollo-helios",
    "subtitle": "The Center of the Chart and the Essence of Being",
    "content": """# ☉ The Sun - Apollo and Helios

## The Diurnal Luminary

The Sun is the center of our solar system and the center of the astrological chart. For the ancients, it represented the source of all life, light, and heat. In astrology, the Sun symbolizes our **essence**, our **ego**, and our **fundamental vitality**.

Unlike the other "planets" that wander through the zodiac, the Sun defines the cycle itself - the **solar year** - which is the basis of our calendar and seasons.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Earth | 1 AU (150 million km) |
| Period through Zodiac | 1 year (365.25 days) |
| Diameter | 1,392,700 km (109x Earth) |
| Surface temperature | 5,500°C |
| Type | Star (G2V yellow dwarf) |

**Observational curiosity:** The Sun is so bright it should never be observed directly. The ancients watched it rise and set, marking the rhythm of life - active during the day, sleeping at night.

---

## Mythology

### Helios (Titan of the Sun) and Apollo (Solar God)

In Greek mythology, there were two solar gods:

**Helios** was the Sun personified, a Titan who drove his golden chariot across the sky from east to west every day. He saw and witnessed everything, serving as witness to oaths.

**Apollo**, son of Zeus and Leto, was the god of light, music, poetry, medicine, prophecy, and reason. Over time, he was identified with the Sun, especially in Rome, where he was called **Phoebus Apollo** (Apollo the Shining).

Apollo was considered the most beautiful of the gods, representing masculine perfection. His temple at Delphi housed the famous Oracle, where the Pythia prophesied in his name.

**Symbols and Attributes:**
- **Metal:** Gold
- **Color:** Golden, yellow
- **Day:** Sunday
- **Stone:** Ruby, diamond
- **Animal:** Lion, eagle
- **Plant:** Laurel, sunflower

**Family Relations (Apollo):**
- **Parents:** Zeus and Leto
- **Twin sister:** Artemis
- **Notable children:** Asclepius (god of medicine), Orpheus

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Domicile** | Leo |
| **Exaltation** | Aries (19°) |
| **Detriment** | Aquarius |
| **Fall** | Libra |

### Planetary Qualities

- **Sect:** Diurnal Luminary (leader of the diurnal sect)
- **Nature:** Moderately Benefic
- **Temperament:** Hot and Dry (slightly)
- **Gender:** Masculine
- **Speed:** Constant (~59' per day)

### What the Sun Represents

In the natal chart, the Sun indicates:

- **Identity and ego** - who you essentially are
- **Vitality and health** - life force
- **Life purpose** - what you came to do
- **The father** or father figure
- **Authority and leadership** - ability to command
- **Fame and recognition** - shining before others
- **The heart** - physical and metaphorical

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Confidence** and healthy self-esteem
- **Generosity** of spirit
- **Natural leadership**
- **Strong vitality**
- **Creativity** and personal expression
- **Nobility** of character
- **Success** and recognition

### Negative Manifestations

When afflicted:

- **Arrogance** and excessive pride
- **Egocentrism** and narcissism
- **Tyranny** and domination
- **Vital weakness** and heart problems
- **Excessive need** for approval
- **Blindness** to own faults

### Solar Professions

- Kings and rulers
- Actors and celebrities
- Jewelers (especially gold)
- Cardiologists
- Business leaders (CEOs)
- Artists and creators
- Prominent politicians

---

## Classical Quotes

> "The Sun is the source of light and life, the heart of heaven, the eye of the world..."
> — Hermetic Tradition

> "The Sun is hot, dry, masculine, diurnal, author of honor, glory, dignity..."
> — **William Lilly**, *Christian Astrology*, 1647

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Ovid. *Metamorphoses*.
- Greek Mythology compilations.
""",
    "excerpt": "Learn about the Sun in astrology: Apollo and Helios mythology, meaning as the diurnal luminary and how it represents your essence and vitality in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "sun", "mythology", "traditional"],
    "seo_title": "The Sun in Astrology - Apollo and Helios, the Diurnal Luminary",
    "seo_description": "Discover the Sun: Apollo mythology, astrological dignities, symbolism and meanings. Complete guide to the Diurnal Luminary in traditional astrology.",
    "seo_keywords": ["sun", "apollo", "helios", "astrology", "luminary", "greek mythology"],
    "is_featured": True,
    "read_time_minutes": 10,
    "locale": "en-US",
    "translation_key": "sun-mythology",
}

VENUS_EN = {
    "title": "Venus - Aphrodite: The Star of Beauty",
    "slug": "venus-aphrodite",
    "subtitle": "The Lesser Benefic and Life's Pleasures",
    "content": """# ♀ Venus - Aphrodite

## The Star of Beauty

Venus is the brightest planet in the night sky, so luminous it can be seen even during the day under favorable conditions. The ancients called it the **Morning Star** (Phosphorus/Lucifer) when it appeared before dawn, and the **Evening Star** (Hesperus) when it shone after sunset.

Its beauty and brightness inspired associations with love, beauty, and all of life's pleasures.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Sun | 0.72 AU (108 million km) |
| Orbital Period | 225 Earth days |
| Synodic Period | 584 days |
| Diameter | 12,104 km (0.95x Earth) |
| Moons | None |
| Average temperature | 464°C (greenhouse effect!) |

**Observational curiosity:** Venus goes through phases like the Moon, visible through a telescope. The ancients didn't know this, but noticed its two "identities" - morning and evening star - which they long believed were two different celestial bodies.

---

## Mythology

### Aphrodite (Greek) / Venus (Roman)

**Aphrodite** was born in an extraordinary way: when Cronus castrated Uranus and threw his organs into the sea, the foam (aphros) that formed gave rise to the goddess of beauty and love. She emerged from the waves on a shell, already adult and perfectly beautiful, on the island of Cyprus.

Aphrodite was married to **Hephaestus**, the lame and ugly blacksmith god. But her heart belonged to **Ares**, with whom she had a famous love affair. Besides him, she had many lovers, both mortal and immortal.

She was irresistible - even the gods couldn't resist her charm. She possessed a magical belt that made anyone irresistible when worn.

**Symbols and Attributes:**
- **Metal:** Copper
- **Color:** Green, pink
- **Day:** Friday (Vendredi in French)
- **Stone:** Emerald, turquoise
- **Animal:** Dove, swan
- **Plant:** Rose, myrtle

**Family Relations:**
- **Birth:** From sea foam (or daughter of Zeus and Dione)
- **Husband:** Hephaestus
- **Lovers:** Ares, Adonis, Anchises
- **Children:** Eros (with Ares), Aeneas (with Anchises)

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Diurnal Domicile** | Libra |
| **Nocturnal Domicile** | Taurus |
| **Exaltation** | Pisces (27°) |
| **Detriment** | Aries, Scorpio |
| **Fall** | Virgo |

### Planetary Qualities

- **Sect:** Nocturnal
- **Nature:** **Lesser Benefic**
- **Temperament:** Cold and Moist (Phlegmatic)
- **Gender:** Feminine
- **Speed:** Fast (similar to Sun, ~1° per day)

### What Venus Represents

In the natal chart, Venus indicates:

- **Love and relationships** - how we love and are loved
- **Beauty and aesthetics** - artistic sense
- **Pleasure and comfort** - what brings us joy
- **Values** - what we value
- **Money** (especially earned through pleasure)
- **Harmony and diplomacy**
- **The beloved woman** or feminine ideal

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Charm** and personal magnetism
- **Art** and aesthetic sensitivity
- **Diplomacy** and social tact
- **Love** and capacity for love
- **Beauty** physical and inner
- **Healthy pleasure**
- **Prosperity** and comfort

### Negative Manifestations

When afflicted:

- **Vanity** and superficiality
- **Laziness** and indolence
- **Lust** and promiscuity
- **Possessive jealousy**
- **Financial extravagance**
- **Emotional dependence**
- **Manipulation** through charm

### Venusian Professions

- Artists and musicians
- Designers and decorators
- Beauticians and cosmetologists
- Jewelers
- Diplomats and mediators
- Florists and gardeners
- Confectioners and chocolatiers
- Hosts and event planners

---

## Classical Quotes

> "Venus is a feminine planet, temperate, nocturnal, the Lesser Benefic, author of joy, festivity, music, love..."
> — **William Lilly**, *Christian Astrology*, 1647

> "Venus produces loving, elegant, beauty-loving, pleasant, sociable people..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Hesiod. *Theogony*.
- Greek Mythology compilations.
""",
    "excerpt": "Discover Venus, the Star of Beauty: Aphrodite mythology, goddess of love, astrological dignities and how it represents love and pleasure in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "venus", "mythology", "traditional"],
    "seo_title": "Venus in Astrology - Aphrodite, the Goddess of Love",
    "seo_description": "Learn about Venus: Aphrodite mythology, astrological dignities, symbolism and meanings. Complete guide to the Lesser Benefic in traditional astrology.",
    "seo_keywords": ["venus", "aphrodite", "astrology", "love", "greek mythology"],
    "locale": "en-US",
    "translation_key": "venus-mythology",
    "is_featured": False,
    "read_time_minutes": 10,
}

MERCURY_EN = {
    "title": "Mercury - Hermes: The Messenger of the Gods",
    "slug": "mercury-hermes",
    "subtitle": "The Neutral Planet and the Versatility of Mind",
    "content": """# ☿ Mercury - Hermes

## The Messenger of the Gods

Mercury is the planet closest to the Sun and the fastest in the solar system. For the ancients, its swift movement across the sky, always near the Sun, made it the perfect **messenger** - fast, agile, and difficult to capture.

It never strays more than 28° from the Sun, always remaining close to the diurnal luminary, like a loyal secretary transmitting orders and information.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Sun | 0.39 AU (58 million km) |
| Orbital Period | 88 Earth days |
| Maximum elongation | 28° from Sun |
| Diameter | 4,879 km (0.38x Earth) |
| Moons | None |
| Temperature | -180°C to 430°C |

**Observational curiosity:** Mercury is difficult to observe because it's always near the Sun. The ancients sometimes thought there were two different planets - one of morning and one of evening - until they realized it was the same swift celestial body.

---

## Mythology

### Hermes (Greek) / Mercury (Roman)

**Hermes** was the messenger of the gods, guide of souls to the underworld, and patron of travelers, merchants, thieves, and orators. Son of **Zeus** and the nymph **Maia**, he was born in a cave on Mount Cyllene.

Hermes was a precocious god: while still a baby, he left his cradle and stole his brother Apollo's cattle. To reconcile, he invented the **lyre** from a tortoise shell and gave it to Apollo, who was enchanted. In exchange, he received the shepherd's staff - the **caduceus**.

Hermes moved freely between the world of the living and the dead, between gods and humans. He was the only one who could enter and leave Hades freely, guiding souls (hence called **Psychopomp**).

**Symbols and Attributes:**
- **Metal:** Mercury (quicksilver)
- **Color:** Various, multicolored
- **Day:** Wednesday (Mercredi in French)
- **Stone:** Agate, opal
- **Animal:** Rooster, tortoise
- **Object:** Caduceus (staff with two serpents)

**Family Relations:**
- **Parents:** Zeus and Maia
- **Children:** Pan, Hermaphroditus

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Diurnal Domicile** | Gemini |
| **Nocturnal Domicile** | Virgo |
| **Exaltation** | Virgo (15°) |
| **Detriment** | Sagittarius, Pisces |
| **Fall** | Pisces |

### Planetary Qualities

- **Sect:** **Neutral** (adapts to the sect of the planet it's with)
- **Nature:** **Neutral** (benefic with benefics, malefic with malefics)
- **Temperament:** Cold and Dry (when alone)
- **Gender:** Neutral/Androgynous
- **Speed:** Very fast (up to 2° per day)

### What Mercury Represents

In the natal chart, Mercury indicates:

- **Mind and intellect** - how we think
- **Communication** - how we express ourselves
- **Writing and speech** - verbal abilities
- **Learning** - ability to absorb information
- **Commerce and business** - transactions
- **Short journeys** - local travel
- **Siblings and neighbors**
- **Manual skill** and dexterity

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Agile and versatile intelligence**
- **Eloquence** and clear communication
- **Healthy curiosity**
- **Business skill**
- **Manual dexterity**
- **Adaptability** to situations
- **Humor** and wit

### Negative Manifestations

When afflicted:

- **Lying** and dishonesty
- **Intellectual superficiality**
- **Nervousness** and anxiety
- **Trickery** and theft
- **Gossip** and slander
- **Inconstancy** and dispersion
- **Verbal manipulation**

### Mercurial Professions

- Writers and journalists
- Teachers (primary education)
- Merchants
- Translators and interpreters
- Secretaries and assistants
- Mail carriers and messengers
- Astrologers and magicians
- Accountants and mathematicians

---

## Classical Quotes

> "Mercury is the author of subtlety, tricks, invention, eloquence... he is a changeable planet, participating in the nature of whatever planet he is configured with."
> — **William Lilly**, *Christian Astrology*, 1647

> "Mercury by his nature produces ingenious, prudent men, apt for any knowledge..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Homeric Hymns.
- Greek Mythology compilations.
""",
    "excerpt": "Learn about Mercury, the Messenger of the Gods: Hermes mythology, meaning as a neutral planet and how it represents mind and communication in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "mercury", "mythology", "traditional"],
    "seo_title": "Mercury in Astrology - Hermes, the Messenger",
    "seo_description": "Discover Mercury: Hermes mythology, astrological dignities, symbolism and meanings. Complete guide to the planet of mind and communication.",
    "seo_keywords": ["mercury", "hermes", "astrology", "communication", "greek mythology"],
    "locale": "en-US",
    "translation_key": "mercury-mythology",
    "is_featured": False,
    "read_time_minutes": 10,
}

MOON_EN = {
    "title": "The Moon - Artemis and Selene: The Nocturnal Luminary",
    "slug": "moon-artemis-selene",
    "subtitle": "The Lady of the Night and the Emotional World",
    "content": """# ☽ The Moon - Artemis and Selene

## The Nocturnal Luminary

The Moon is the celestial body closest to Earth and the only one that orbits our planet. Its cycle of phases, from new to full and back to new in approximately **29.5 days**, is the basis of the oldest calendars and remains fundamental in astrology.

For the ancients, the Moon ruled the night just as the Sun ruled the day. It represented the world of emotions, dreams, fertility, and the natural cycles of life.

---

## Astronomical Data

| Characteristic | Value |
|----------------|-------|
| Average distance from Earth | 384,400 km |
| Synodic Period (phases) | 29.5 days |
| Sidereal Period | 27.3 days |
| Diameter | 3,474 km (0.27x Earth) |
| Temperature | -173°C to 127°C |
| Rotation | Synchronous (always shows same face) |

**Observational curiosity:** The Moon is the only celestial body whose details are visible to the naked eye. The ancients saw the "seas" (dark plains) and "lands" (light regions), creating stories about the "face of the Moon."

---

## Mythology

### Selene (Lunar Titaness) and Artemis (Lunar Goddess)

In Greek mythology, just as there were two solar gods, there were distinct lunar deities:

**Selene** was the Moon personified, a Titaness who drove her silver chariot through the night sky. Her most famous myth is her love for the shepherd **Endymion**, so handsome that she asked Zeus to put him in eternal sleep to preserve his youth and visit him every night.

**Artemis**, daughter of Zeus and Leto and twin sister of Apollo, was the goddess of hunting, the wild, and maidens. An eternal virgin, she roamed the forests with her silver bow, accompanied by nymphs. Over time, she was identified with the Moon, especially its crescent aspect.

**Hecate** was a third lunar deity, associated with the new Moon, magic, and crossroads.

**Symbols and Attributes:**
- **Metal:** Silver
- **Color:** White, silver, pale blue
- **Day:** Monday (Moon-day)
- **Stone:** Pearl, moonstone
- **Animal:** Owl, hare
- **Plant:** White lily, willow

**Family Relations (Artemis):**
- **Parents:** Zeus and Leto
- **Twin brother:** Apollo

---

## In Traditional Astrology

### Essential Dignities

| Dignity | Sign(s) |
|---------|---------|
| **Domicile** | Cancer |
| **Exaltation** | Taurus (3°) |
| **Detriment** | Capricorn |
| **Fall** | Scorpio |

### Planetary Qualities

- **Sect:** Nocturnal Luminary (leader of the nocturnal sect)
- **Nature:** Moderately Benefic (mutable)
- **Temperament:** Cold and Moist (Phlegmatic)
- **Gender:** Feminine
- **Speed:** The fastest (~13° per day)

### What the Moon Represents

In the natal chart, the Moon indicates:

- **Emotions and feelings** - the inner world
- **Basic needs** - what we need to feel secure
- **The mother** and maternal figures
- **Memory and past** - conditioning
- **Habits** - automatic patterns
- **The physical body** and its nourishment
- **The people** and general population
- **Fertility** and natural cycles

---

## Symbolism and Archetypes

### Positive Manifestations

When well-aspected or dignified:

- **Sharp intuition**
- **Sensitivity** and empathy
- **Excellent memory**
- **Nurturing** and care
- **Rich imagination**
- **Receptivity** and welcoming
- **Fertility** (physical and creative)

### Negative Manifestations

When afflicted:

- **Emotional instability**
- **Dependence** and neediness
- **Melancholy** and depression
- **Excessive passivity**
- **Fear** and insecurity
- **Attachment** to the past
- **Paralyzing hypersensitivity**

### Lunar Professions

- Nurses and caregivers
- Nutritionists and chefs
- Midwives and obstetricians
- Historians and archivists
- Hoteliers and hosts
- Fishermen and sailors
- Psychologists and therapists
- Gardeners and farmers

---

## The Lunar Phases

| Phase | Meaning |
|-------|---------|
| **New Moon** | Beginning, planting, new starts |
| **Waxing** | Expansion, growth, action |
| **Full** | Culmination, fullness, harvest |
| **Waning** | Reflection, closure, cleansing |

---

## Classical Quotes

> "The Moon is feminine, nocturnal, cold and moist, phlegmatic... she governs the masses, travelers, women, fishermen..."
> — **William Lilly**, *Christian Astrology*, 1647

> "The Moon represents the soul, the body, the mother, journeys, popularity..."
> — **Claudius Ptolemy**, *Tetrabiblos*, 2nd century

---

## References

- Ptolemy. *Tetrabiblos*. 2nd century AD.
- Lilly, William. *Christian Astrology*. London, 1647.
- Homeric Hymns.
- Greek Mythology compilations.
""",
    "excerpt": "Discover the Moon in astrology: Artemis and Selene mythology, meaning as the nocturnal luminary and how it represents emotions and the inner world in the natal chart.",
    "category": "stars_and_myths",
    "tags": ["planets", "moon", "mythology", "traditional"],
    "seo_title": "The Moon in Astrology - Artemis and Selene, the Nocturnal Luminary",
    "seo_description": "Learn about the Moon: Artemis and Selene mythology, astrological dignities, lunar phases and meanings. Complete guide to the Nocturnal Luminary in astrology.",
    "seo_keywords": ["moon", "artemis", "selene", "astrology", "luminary", "greek mythology"],
    "is_featured": True,
    "read_time_minutes": 11,
    "locale": "en-US",
    "translation_key": "moon-mythology",
}

# =============================================================================
# ALL POSTS
# =============================================================================

ALL_POSTS = [
    # Portuguese
    SATURNO_PT,
    JUPITER_PT,
    MARTE_PT,
    SOL_PT,
    VENUS_PT,
    MERCURIO_PT,
    LUA_PT,
    # English
    SATURN_EN,
    JUPITER_EN,
    MARS_EN,
    SUN_EN,
    VENUS_EN,
    MERCURY_EN,
    MOON_EN,
]


async def seed_astros_e_mitos():
    """Create Astros e Mitos educational blog posts."""
    import os

    db_host = os.environ.get("DB_HOST", "db")
    conn = await asyncpg.connect(
        host=db_host,
        port=5432,
        user="astro",
        password="dev_password",
        database="astro_dev",
    )

    try:
        now = datetime.now(UTC)
        created_count = 0

        for post_data in ALL_POSTS:
            locale = post_data.get("locale", "pt-BR")
            # Check if post already exists for this locale
            existing = await conn.fetchrow(
                "SELECT id FROM blog_posts WHERE slug = $1 AND locale = $2",
                post_data["slug"],
                locale,
            )

            if existing:
                print(f"  Skipping (already exists): {post_data['slug']} ({locale})")
                continue

            post_id = uuid4()

            await conn.execute(
                """
                INSERT INTO blog_posts (
                    id, slug, locale, translation_key, title, subtitle, content, excerpt,
                    category, tags, featured_image_url, seo_title, seo_description, seo_keywords,
                    published_at, is_featured, read_time_minutes, views_count,
                    created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                )
                """,
                post_id,
                post_data["slug"],
                locale,
                post_data.get("translation_key"),
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
                now,  # published_at
                post_data["is_featured"],
                post_data["read_time_minutes"],
                0,  # views_count
                now,
                now,
            )
            print(f"  Created: {post_data['title']} ({locale})")
            created_count += 1

        print(f"\nSuccessfully created {created_count} blog posts!")
        print(f"Skipped {len(ALL_POSTS) - created_count} existing posts.")
        print("\nView posts at:")
        print("  - Portuguese: http://localhost:5173/blog?locale=pt-BR")
        print("  - English: http://localhost:5173/blog?locale=en-US")

    finally:
        await conn.close()


if __name__ == "__main__":
    print("Seeding Astros e Mitos educational content...\n")
    asyncio.run(seed_astros_e_mitos())
