# Sistema de Mapas Natais - Especificação Técnica Completa

## Versão 1.0 | Data: 2025-01-14

---

## 1. Visão Geral do Projeto

### 1.1 Descrição
Sistema web completo para geração, armazenamento e análise de mapas natais astrológicos utilizando princípios da astrologia tradicional. A aplicação oferece cálculos astronômicos de alta precisão, visualização gráfica interativa e análises interpretativas detalhadas.

### 1.2 Objetivos Principais
- Fornecer cálculos astrológicos precisos baseados em Swiss Ephemeris
- Gerar mapas natais visuais profissionais
- Oferecer análises interpretativas baseadas em astrologia tradicional
- Permitir gestão completa de múltiplos mapas por usuário
- Exportar relatórios profissionais em PDF com LaTeX
- Garantir segurança e privacidade de dados pessoais sensíveis

### 1.3 Público-Alvo
- Astrólogos profissionais
- Estudantes de astrologia
- Entusiastas de autoconhecimento
- Consultores holísticos

---

## 2. Requisitos Funcionais (RF)

### 2.1 Gestão de Usuários e Autenticação

#### RF-001: Registro de Usuários
**Descrição**: Sistema deve permitir registro de novos usuários
**Entradas**:
- Nome completo (min: 3 chars, max: 100 chars)
- Email (validação RFC 5322)
- Senha (min: 8 chars, 1 maiúscula, 1 minúscula, 1 número, 1 especial)
- Confirmação de senha

**Regras**:
- Email único no sistema
- Senha hasheada com bcrypt (cost factor: 12)
- Envio de email de verificação obrigatório
- Conta ativa apenas após verificação

**Saídas**:
- Conta criada (status: pending_verification)
- Email de confirmação enviado
- Token JWT temporário (validade: 24h para verificação)

#### RF-002: Login Tradicional (JWT)
**Descrição**: Autenticação com email e senha
**Entradas**:
- Email
- Senha

**Regras**:
- Verificar email confirmado
- Validar credenciais
- Limite de tentativas: 5 falhas = bloqueio temporário (15 min)
- Refresh token válido por 30 dias
- Access token válido por 15 minutos

**Saídas**:
- Access token (JWT)
- Refresh token (HTTP-only cookie)
- Dados básicos do usuário (id, nome, email)

#### RF-003: Login Social (OAuth2)
**Descrição**: Autenticação via providers externos
**Providers suportados**:
- Google OAuth2
- Facebook OAuth2
- GitHub OAuth2

**Fluxo**:
1. Usuário seleciona provider
2. Redirect para página de autorização
3. Callback com authorization code
4. Backend troca code por access token
5. Busca perfil do usuário
6. Cria ou atualiza conta local
7. Emite JWT próprio

**Regras**:
- Associar conta social a conta existente (mesmo email)
- Permitir múltiplos providers por conta
- Armazenar apenas ID do provider (não access tokens externos)

#### RF-004: Recuperação de Senha
**Descrição**: Reset de senha via email
**Fluxo**:
1. Usuário fornece email
2. Sistema envia link com token (validade: 1h)
3. Usuário define nova senha
4. Invalida todos tokens JWT existentes

#### RF-005: Gestão de Perfil
**Descrição**: Atualização de dados pessoais
**Campos editáveis**:
- Nome completo
- Email (requer re-verificação)
- Senha (requer senha atual)
- Foto de perfil (upload, max: 2MB, formatos: jpg, png, webp)
- Fuso horário preferido
- Idioma (pt-BR, en-US, es-ES)

**Campos não editáveis**:
- ID do usuário
- Data de criação
- Data de última atualização

### 2.2 Gestão de Mapas Natais

#### RF-006: Criação de Mapa Natal
**Descrição**: Gerar novo mapa natal com dados de nascimento

**Entradas obrigatórias**:
- Nome da pessoa (min: 2 chars, max: 100 chars)
- Data de nascimento (1900-01-01 até data atual)
- Hora de nascimento (formato: HH:MM, precisão: minuto)
- Local de nascimento:
  - Cidade (autocomplete)
  - País
  - OU Latitude/Longitude (decimal degrees, precisão: 0.0001°)

**Entradas opcionais**:
- Sexo/Gênero (masculino, feminino, não-binário, prefiro não informar, outro)
- Notas pessoais (max: 1000 chars)
- Tags/categorias (para organização)
- Visibilidade (privado, compartilhado)

**Configurações de cálculo**:
- Sistema de casas (padrão: Placidus)
  - Placidus
  - Whole Sign
  - Koch
  - Regiomontanus
  - Campanus
  - Equal House
- Zodíaco (padrão: Tropical)
  - Tropical
  - Sidereal (especificar Ayanamsa: Lahiri, Fagan-Bradley, etc.)
- Nodo Lunar (padrão: True Node)
  - True Node
  - Mean Node

**Processamento**:
1. Validar dados de entrada
2. Geocodificar localização (obter lat/long se não fornecido)
3. Determinar timezone histórico correto
4. Converter para UTC
5. Calcular posições planetárias (PySwisseph)
6. Calcular cúspides das casas
7. Calcular aspectos entre planetas
8. Calcular dignidades essenciais
9. Determinar sect (dia/noite)
10. Calcular Lot of Fortune
11. Identificar estrelas fixas próximas (orb: 1°)
12. Gerar dados de visualização

**Saídas**:
- ID do mapa natal
- Dados completos do mapa (JSON estruturado)
- Timestamp de criação
- Confirmação de salvamento

#### RF-007: Visualização de Mapa Natal
**Descrição**: Exibir representação gráfica do mapa

**Elementos visuais**:
- Círculo exterior: Signos zodiacais (30° cada)
- Círculo das casas: Cúspides calculadas
- Planetas posicionados:
  - Sol, Lua, Mercúrio, Vênus, Marte
  - Júpiter, Saturno, Urano, Netuno, Plutão
  - Nodo Norte, Nodo Sul
  - Chiron, Lilith (Black Moon)
- Aspectos:
  - Conjunção (0°, orb: 8°)
  - Sextil (60°, orb: 6°)
  - Quadratura (90°, orb: 8°)
  - Trígono (120°, orb: 8°)
  - Oposição (180°, orb: 8°)
  - Cores diferenciadas (harmônicos: azul, tensos: vermelho)
- Ascendente (AC) e Meio do Céu (MC) destacados

**Interatividade**:
- Hover sobre planetas: tooltip com dados (signo, grau, casa, dignidades)
- Click em aspecto: detalhes do aspecto (orb exato, tipo, aplicativo/separativo)
- Zoom in/out
- Download como SVG ou PNG (alta resolução, 300 DPI)

**Responsividade**:
- Desktop: 800x800px
- Tablet: 600x600px
- Mobile: 100% width (min: 320px)

#### RF-008: Listagem de Mapas
**Descrição**: Visualizar todos os mapas do usuário

**Funcionalidades**:
- Ordenação:
  - Data de criação (mais recente, mais antigo)
  - Nome alfabético (A-Z, Z-A)
  - Data de nascimento
- Filtros:
  - Por tag/categoria
  - Por período de criação
  - Por signo solar
- Busca textual (nome da pessoa, notas)
- Paginação (20 itens por página)

**Exibição por item**:
- Nome da pessoa
- Data/hora de nascimento
- Local
- Miniatura do mapa (thumbnail 200x200px)
- Data de criação
- Última edição
- Ações: Ver, Editar, Duplicar, Excluir

#### RF-009: Edição de Mapa Natal
**Descrição**: Atualizar dados de mapa existente

**Campos editáveis**:
- Nome da pessoa
- Sexo/gênero
- Notas pessoais
- Tags/categorias
- Configurações de cálculo (recalcula mapa)

**Campos não editáveis** (requer novo mapa):
- Data de nascimento
- Hora de nascimento
- Local de nascimento

**Regras**:
- Manter histórico de alterações (audit log)
- Recalcular apenas se configurações mudarem
- Atualizar timestamp de última edição

#### RF-010: Exclusão de Mapa Natal
**Descrição**: Remover mapa do sistema

**Regras**:
- Soft delete (não remover fisicamente)
- Manter no banco por 30 dias (recuperação possível)
- Após 30 dias: hard delete permanente
- Confirmação obrigatória via modal
- Não permitir exclusão se mapa compartilhado ativo

#### RF-011: Duplicação de Mapa
**Descrição**: Criar cópia de mapa existente

**Uso**:
- Testar diferentes sistemas de casas
- Comparar Tropical vs Sidereal
- Criar variação com dados similares

**Comportamento**:
- Copiar todos os dados
- Adicionar sufixo " (cópia)" ao nome
- Recalcular mapa completo
- Novo ID único

### 2.3 Cálculos Astrológicos

#### RF-012: Posições Planetárias
**Descrição**: Calcular coordenadas eclípticas precisas

**Corpos celestes**:
- Planetas principais: Sol, Lua, Mercúrio, Vênus, Marte, Júpiter, Saturno
- Planetas exteriores: Urano, Netuno, Plutão
- Pontos: Nodo Lunar (True/Mean), Lilith (Black Moon)
- Asteroides (opcional): Chiron, Ceres, Pallas, Juno, Vesta

**Dados calculados por corpo**:
- Longitude eclíptica (0-360°, precisão: 0.0001°)
- Latitude eclíptica
- Distância da Terra (AU)
- Velocidade diária (motion)
- Retrógrado (R) ou Direto (D)
- Signo zodiacal (tropical ou sidereal)
- Grau dentro do signo (0-30°)
- Minutos e segundos de arco
- Casa ocupada

**Precisão**:
- Erro máximo: 1 arcsecond (0.0003°)
- Fonte: Swiss Ephemeris (JPL DE431)

#### RF-013: Sistemas de Casas
**Descrição**: Calcular cúspides das 12 casas

**Sistemas suportados**:
1. **Placidus** (padrão): Divisão temporal
2. **Whole Sign**: Cada casa = 30° a partir do AC
3. **Koch**: Sistema de birthplace
4. **Regiomontanus**: Divisão do equador celeste
5. **Campanus**: Divisão do primeiro vertical
6. **Equal House**: 12 casas iguais a partir do AC

**Pontos calculados**:
- Ascendente (AC): Cúspide da Casa 1
- Fundo do Céu (IC): Cúspide da Casa 4
- Descendente (DC): Cúspide da Casa 7
- Meio do Céu (MC): Cúspide da Casa 10
- Cúspides das demais casas (2, 3, 5, 6, 8, 9, 11, 12)

**Tratamento de latitudes extremas**:
- Acima de 66.5°N/S: alguns sistemas falham
- Fallback automático para Whole Sign ou Equal House

#### RF-014: Cálculo de Aspectos
**Descrição**: Identificar aspectos ptolemaicos entre planetas

**Aspectos principais**:
- Conjunção (0°): Orb padrão 8°
- Sextil (60°): Orb padrão 6°
- Quadratura (90°): Orb padrão 8°
- Trígono (120°): Orb padrão 8°
- Oposição (180°): Orb padrão 8°

**Aspectos secundários** (opcional):
- Semi-sextil (30°): Orb 2°
- Quincunx (150°): Orb 2°

**Dados de cada aspecto**:
- Planeta 1 e Planeta 2
- Tipo de aspecto
- Orb exato (diferença do ângulo perfeito)
- Aplicativo (applying) vs Separativo (separating)
  - Aplicativo: planetas se aproximando do aspecto exato
  - Separativo: planetas se afastando
- Natureza: Harmônico (sextil, trígono) ou Tenso (quadratura, oposição)

**Orbs ajustáveis**:
- Sistema de orbs por tipo de planeta:
  - Sol/Lua: +2° (orbs maiores)
  - Planetas exteriores: -1° (orbs menores)
- Configurável por usuário (avançado)

#### RF-015: Dignidades Essenciais
**Descrição**: Calcular força essencial de cada planeta

**Sistema tradicional de pontuação**:

1. **Domicílio/Rulership** (+5 pontos):
   - Sol: Leão
   - Lua: Câncer
   - Mercúrio: Gêmeos, Virgem
   - Vênus: Touro, Libra
   - Marte: Áries, Escorpião
   - Júpiter: Sagitário, Peixes
   - Saturno: Capricórnio, Aquário

2. **Exaltação** (+4 pontos):
   - Sol: Áries (19°)
   - Lua: Touro (3°)
   - Mercúrio: Virgem (15°)
   - Vênus: Peixes (27°)
   - Marte: Capricórnio (28°)
   - Júpiter: Câncer (15°)
   - Saturno: Libra (21°)

3. **Triplicidade** (+3 pontos):
   - Fogo (Áries, Leão, Sagitário):
     - Dia: Sol | Noite: Júpiter | Participante: Saturno
   - Terra (Touro, Virgem, Capricórnio):
     - Dia: Vênus | Noite: Lua | Participante: Marte
   - Ar (Gêmeos, Libra, Aquário):
     - Dia: Saturno | Noite: Mercúrio | Participante: Júpiter
   - Água (Câncer, Escorpião, Peixes):
     - Dia: Vênus | Noite: Marte | Participante: Lua

4. **Termo/Bound** (+2 pontos):
   - Divisões de cada signo por grau (sistema egípcio)

5. **Face/Decan** (+1 ponto):
   - Divisões de 10° em cada signo

**Debilidades**:
- **Detrimento** (-5 pontos): Signo oposto ao domicílio
- **Queda** (-4 pontos): Signo oposto à exaltação

**Saída**:
- Score total por planeta (-5 a +15)
- Classificação: Dignificado, Peregrino, Debilitado
- Detalhamento de cada dignidade aplicável

#### RF-016: Determinação de Sect
**Descrição**: Identificar se mapa é diurno ou noturno

**Regra**:
- **Diurno (Day Chart)**: Sol acima do horizonte (Casas 7-12)
- **Noturno (Night Chart)**: Sol abaixo do horizonte (Casas 1-6)

**Implicações**:
- Sect dos planetas:
  - Diurnos: Sol, Júpiter, Saturno
  - Noturnos: Lua, Vênus, Marte
- Planetas em sect (concordância) = benefício
- Planetas fora de sect = desafio

**Benefícios e Maléficos por Sect**:
- Diurno:
  - Benéfico em sect: Júpiter
  - Maléfico em sect: Saturno
  - Maléfico fora de sect: Marte (pior)
- Noturno:
  - Benéfico em sect: Vênus
  - Maléfico em sect: Marte
  - Maléfico fora de sect: Saturno (pior)

#### RF-017: Cálculo de Partes Arábicas
**Descrição**: Calcular pontos matemáticos sensíveis

**Parte de Fortuna** (Lot of Fortune):
- Fórmula diurna: AC + Lua - Sol
- Fórmula noturna: AC + Sol - Lua
- Resultado: Grau eclíptico (0-360°)
- Conversão: Signo + grau

**Outras partes** (expansão futura):
- Parte do Espírito: AC + Sol - Lua
- Parte do Eros
- Parte da Necessidade

#### RF-018: Estrelas Fixas
**Descrição**: Identificar estrelas fixas conjuntas a planetas/pontos

**Estrelas principais** (magnitude < 2.0):
- Regulus (Alpha Leonis): ~0° Virgem
- Spica (Alpha Virginis): ~24° Libra
- Aldebaran (Alpha Tauri): ~10° Gêmeos
- Antares (Alpha Scorpii): ~10° Sagitário
- Fomalhaut (Alpha Piscis Austrini): ~4° Peixes
- Algol (Beta Persei): ~26° Touro
- Sirius (Alpha Canis Majoris): ~14° Câncer
- Vega (Alpha Lyrae): ~15° Capricórnio

**Critério de conjunção**:
- Orb máximo: 1° (padrão)
- Configurável: 0.5° a 2°

**Dados fornecidos**:
- Nome da estrela
- Magnitude
- Longitude atual (com precessão)
- Natureza tradicional (Marte+Júpiter, Vênus+Mercúrio, etc.)
- Planeta/ponto em conjunção

### 2.4 Análise e Interpretação

#### RF-019: Geração de Interpretação Textual
**Descrição**: Produzir análise escrita do mapa natal

**Estrutura da análise**:

1. **Resumo Executivo** (200-300 palavras):
   - Destaques principais do mapa
   - Tema central de vida
   - Maiores fortalezas
   - Principais desafios

2. **Análise Solar** (Sol):
   - Signo, casa, grau
   - Dignidades essenciais
   - Aspectos principais
   - Interpretação de personalidade central

3. **Análise Lunar** (Lua):
   - Signo, casa, grau
   - Dignidades essenciais
   - Aspectos principais
   - Mundo emocional e necessidades

4. **Análise do Ascendente**:
   - Signo ascendente
   - Regente do ascendente (posição, dignidades)
   - Aparência e primeira impressão
   - Abordagem à vida

5. **Planetas Pessoais** (Mercúrio, Vênus, Marte):
   - Análise individual de cada um
   - Comunicação, amor, ação

6. **Planetas Sociais** (Júpiter, Saturno):
   - Crescimento e expansão
   - Estrutura e limitações

7. **Planetas Geracionais** (Urano, Netuno, Plutão):
   - Influências coletivas
   - Áreas de transformação pessoal

8. **Análise das Casas**:
   - Planetas em cada casa
   - Áreas de vida ativadas
   - Casas vazias (regente da cúspide)

9. **Configurações Especiais**:
   - T-Square (se presente)
   - Grande Trígono (se presente)
   - Grand Cross (se presente)
   - Stellium (3+ planetas em mesmo signo/casa)
   - Yod (dedo de Deus)

10. **Síntese e Recomendações**:
    - Integração dos elementos
    - Caminhos de desenvolvimento
    - Potenciais a explorar

**Fonte de conteúdo**:
- Templates textuais parametrizados
- Base de conhecimento astrológico
- Lógica condicional (if planeta X em signo Y então...)
- Expansão futura: IA generativa (GPT-4) para texto mais fluido

#### RF-020: Sistema de Templates de Interpretação
**Descrição**: Gerenciar templates textuais de interpretação

**Estrutura de templates**:
```json
{
  "planet": "Sun",
  "sign": "Aries",
  "house": 10,
  "interpretation": "Sol em Áries na Casa 10 indica uma personalidade assertiva com forte ambição profissional. Líder natural que brilha em posições de autoridade..."
}
```

**Combinações**:
- Planeta em Signo (120 combinações: 10 planetas × 12 signos)
- Planeta em Casa (120 combinações: 10 planetas × 12 casas)
- Aspectos (500+ combinações)
- Dignidades (textos específicos)

**Gerenciamento**:
- CRUD de templates (admin)
- Versionamento de textos
- Suporte multi-idioma (i18n)

### 2.5 Geolocalização e Timezone

#### RF-021: Busca de Local de Nascimento
**Descrição**: Autocomplete de cidades para seleção

**Implementação**:
- API de geocoding: Nominatim (dev) + OpenCage (prod)
- Mínimo 3 caracteres para busca
- Debounce de 300ms
- Retorna top 10 resultados

**Dados retornados por local**:
- Nome da cidade
- Estado/província
- País
- Latitude (decimal degrees)
- Longitude (decimal degrees)
- População (para ranking)
- Nomes alternativos (em português)

**Seleção**:
- Usuário escolhe da lista
- Sistema preenche automaticamente lat/long
- Opção de inserção manual de coordenadas (avançado)

#### RF-022: Determinação Automática de Timezone
**Descrição**: Calcular timezone correto para data/hora/local

**Desafios**:
- Timezones mudam ao longo da história
- Horário de verão (DST) varia por país/ano
- Alguns países mudaram de timezone múltiplas vezes

**Solução**:
- Biblioteca: `timezonefinder` (Python) - lat/long → timezone name
- Biblioteca: `pytz` ou `zoneinfo` - conversões e histórico
- Database: IANA Time Zone Database (tzdata)

**Fluxo**:
1. Receber: data, hora local, lat, long
2. Determinar timezone IANA name (ex: "America/Sao_Paulo")
3. Localizar datetime no timezone encontrado
4. Converter para UTC
5. Usar UTC para cálculos astrológicos

**Validações**:
- Alertar se DST estava em vigor
- Alertar se timezone mudou para aquela região
- Permitir override manual se necessário

#### RF-023: Cache de Localizações Frequentes
**Descrição**: Armazenar locais populares para reduzir chamadas API

**Estratégia**:
- Banco local: top 1000 cidades mundiais
- Incluir: capitais, grandes cidades, cidades brasileiras (500+)
- Atualizar mensalmente

**Dados em cache**:
- Nome (pt-BR, en)
- Lat/Long
- Timezone IANA
- País, estado
- População

**Benefícios**:
- Reduzir custo de API
- Resposta instantânea
- Funcionar offline (parcialmente)

### 2.6 Exportação de Relatórios

#### RF-024: Geração de PDF com LaTeX
**Descrição**: Criar relatório profissional em PDF

**Tecnologias**:
- LaTeX (distribution: TeX Live)
- Jinja2 para templating
- jtex para renderização

**Estrutura do PDF**:

1. **Capa**:
   - Nome da pessoa
   - Data/hora/local de nascimento
   - Imagem do mapa natal (SVG → PDF)
   - Logo/marca do sistema
   - Data de geração

2. **Dados de Nascimento**:
   - Informações completas
   - Coordenadas
   - Timezone
   - Configurações usadas (sistema de casas, etc.)

3. **Mapa Natal** (página inteira):
   - Gráfico em alta resolução
   - Legenda de símbolos

4. **Tabela de Posições Planetárias**:
   - Planeta | Signo | Grau | Casa | Dignidades | Retrógrado

5. **Tabela de Aspectos**:
   - Planeta 1 | Aspecto | Planeta 2 | Orb | Tipo

6. **Análise Interpretativa** (seções anteriores):
   - Texto completo formatado
   - Subtítulos, parágrafos
   - Quebras de página apropriadas

7. **Apêndice**:
   - Glossário de termos
   - Metodologia
   - Referências

**Recursos tipográficos**:
- Fonte serifada (corpo de texto): Libertinus Serif ou TeX Gyre Pagella
- Fonte sans-serif (títulos): Libertinus Sans
- Símbolos astrológicos: fontes especiais (AstroGadget, Kerykeion symbols)
- Margens: 2.5cm
- Numeração de páginas
- Cabeçalho/rodapé

**Template Jinja2**:
- Usuário pode fornecer template customizado
- Variáveis disponíveis: `{{ chart.name }}`, `{{ planets }}`, `{{ aspects }}`, etc.
- Blocos condicionais: `{% if planet.retrograde %}R{% endif %}`

**Performance**:
- Geração assíncrona (não bloquear UI)
- Tempo estimado: 10-30s
- Notificação ao usuário quando pronto
- Download direto ou email

#### RF-025: Download de Dados Brutos
**Descrição**: Exportar dados do mapa em formatos estruturados

**Formatos disponíveis**:

1. **JSON**:
   - Estrutura completa do mapa
   - Todos os cálculos
   - Metadados
   - Uso: integração com outros sistemas

2. **CSV**:
   - Tabela de planetas (colunas: planeta, long, lat, signo, casa, etc.)
   - Tabela de aspectos
   - Uso: análise em planilhas

3. **TXT** (formato tradicional):
   - Formato legível
   - Compatível com softwares antigos

**Uso**:
- Download direto via botão
- Nome do arquivo: `nome-pessoa_data-nascimento_formato.ext`

### 2.7 Compartilhamento e Colaboração

#### RF-026: Compartilhamento de Mapas (Futuro)
**Descrição**: Permitir compartilhar mapa com outros usuários ou publicamente

**Níveis de visibilidade**:
- Privado: Apenas o criador
- Compartilhado: Link privado (UUID único)
- Público: Listado em galeria pública (opcional)

**Permissões**:
- Visualizar apenas
- Comentar (futura integração)

**Link de compartilhamento**:
- URL: `https://app.com/chart/share/{uuid}`
- Sem necessidade de login para visualizar
- Marca d'água: "Compartilhado via [Nome do App]"

---

## 3. Requisitos Não Funcionais (RNF)

### 3.1 Performance

#### RNF-001: Tempo de Cálculo de Mapa Natal
- **Requisito**: Cálculo completo em < 2 segundos (p95)
- **Medição**: Desde submit do formulário até dados salvos no BD
- **Otimizações**:
  - Cache de efemérides em memória
  - Cálculos paralelos onde possível
  - Indexação adequada no BD

#### RNF-002: Tempo de Carregamento de Página
- **Requisito**: First Contentful Paint < 1.5s (3G)
- **Requisito**: Largest Contentful Paint < 2.5s (3G)
- **Estratégias**:
  - Code splitting no React
  - Lazy loading de componentes pesados (mapa, análise)
  - CDN para assets estáticos
  - Compressão gzip/brotli
  - Imagens otimizadas (WebP)

#### RNF-003: Tempo de Geração de PDF
- **Requisito**: < 30 segundos para PDF completo
- **Estratégia**:
  - Fila de processamento assíncrono (Celery + Redis)
  - Notificação ao usuário quando concluído
  - Download via link temporário (S3 presigned URL)

#### RNF-004: API Response Time
- **Requisito**: p50 < 200ms, p95 < 500ms, p99 < 1s
- **Endpoints críticos**: GET /api/charts, POST /api/charts, GET /api/charts/{id}
- **Monitoramento**: APM (Application Performance Monitoring)

### 3.2 Precisão Astronômica

#### RNF-005: Precisão de Posições Planetárias
- **Requisito**: Erro máximo de 1 arcsecond (0.0003°)
- **Fonte**: Swiss Ephemeris (JPL DE431 ephemeris)
- **Validação**:
  - Testes comparativos com astro.com
  - Testes com casos conhecidos (eclipses históricos)
  - Margem de tolerância: ± 0.001°

#### RNF-006: Precisão de Cálculo de Casas
- **Requisito**: Erro máximo de 0.01° nas cúspides
- **Sistemas validados**: Placidus, Koch, Whole Sign
- **Casos extremos**: Latitudes > 60° (ártico/antártico)

#### RNF-007: Precisão Temporal
- **Requisito**: Considerar timezone histórico correto
- **Fonte**: IANA Time Zone Database
- **Validação**: Testar com datas antes/depois de mudanças de DST

### 3.3 Escalabilidade

#### RNF-008: Usuários Simultâneos
- **Requisito**: Suportar 1.000 usuários simultâneos (fase 1)
- **Escalabilidade horizontal**: Arquitetura stateless (múltiplos containers)
- **Load balancer**: Nginx ou cloud-native (AWS ALB)

#### RNF-009: Armazenamento de Mapas
- **Requisito**: Suportar 100.000 mapas (fase 1)
- **Estimativa de tamanho**: ~10 KB por mapa (JSON)
- **Armazenamento total**: ~1 GB de dados de mapas
- **Crescimento**: Planejamento para 1M mapas (10 GB)

#### RNF-010: Backup e Recuperação
- **Backup do BD**: Diário (automatizado)
- **Retenção**: 30 dias de backups
- **Recovery Time Objective (RTO)**: < 4 horas
- **Recovery Point Objective (RPO)**: < 24 horas

### 3.4 Segurança

#### RNF-011: Autenticação e Autorização
- **Senhas**: Hash com bcrypt (cost factor ≥ 12)
- **JWT**: Algoritmo HS256 ou RS256
- **Access token**: 15 minutos de validade
- **Refresh token**: 30 dias, HTTP-only cookie, SameSite=Strict
- **HTTPS**: Obrigatório em produção (TLS 1.3)

#### RNF-012: Proteção contra Ataques Comuns
- **OWASP Top 10**: Mitigação de todas as vulnerabilidades
  - SQL Injection: ORM (SQLAlchemy) + prepared statements
  - XSS: Sanitização de inputs, CSP headers
  - CSRF: Tokens CSRF, SameSite cookies
  - Broken Authentication: Rate limiting, 2FA (futuro)
- **Rate Limiting**:
  - Login: 5 tentativas / 15 minutos / IP
  - API geral: 100 requests / minuto / usuário
  - Criação de mapas: 10 / hora / usuário
- **DDoS**: Cloudflare ou AWS Shield

#### RNF-013: Proteção de Dados Pessoais (LGPD/GDPR)
- **Dados sensíveis**: Data/hora/local de nascimento
- **Consentimento**: Aceite de termos obrigatório
- **Direitos dos titulares**:
  - Acesso: Download de todos os dados (RF-025)
  - Retificação: Edição de perfil e mapas
  - Exclusão: Delete account (hard delete após 30 dias)
  - Portabilidade: Export JSON completo
- **Retenção**: Dados excluídos após 30 dias de soft delete
- **Anonimização**: Logs sem dados pessoais identificáveis

#### RNF-014: Auditoria e Logging
- **Eventos auditados**:
  - Login/logout
  - Criação/edição/exclusão de mapas
  - Alteração de senha
  - Download de PDFs
  - Acesso a dados de outros usuários (admin)
- **Dados de log**:
  - Timestamp, user ID, ação, IP, user agent
  - NÃO logar: senhas, tokens, dados de mapa completos
- **Retenção de logs**: 90 dias
- **Acesso a logs**: Apenas admins autorizados

### 3.5 Usabilidade e Acessibilidade

#### RNF-015: Responsividade
- **Requisito**: Funcionar perfeitamente em:
  - Desktop: ≥ 1280px
  - Tablet: 768px - 1279px
  - Mobile: 320px - 767px
- **Abordagem**: Mobile-first design
- **Testes**: Chrome DevTools, BrowserStack

#### RNF-016: Acessibilidade (WCAG 2.1 - Nível AA)
- **Contraste**: Mínimo 4.5:1 para texto normal, 3:1 para texto grande
- **Navegação por teclado**: Todos os elementos interativos acessíveis via Tab
- **Screen readers**: Semântica HTML5, ARIA labels
- **Formulários**: Labels claros, mensagens de erro descritivas
- **Foco visível**: Indicador claro do elemento focado
- **Alternativas textuais**: Alt text para imagens, descrições para gráficos

#### RNF-017: Internacionalização (i18n)
- **Idiomas suportados (fase 1)**: Português (pt-BR)
- **Planejamento futuro**: Inglês (en-US), Espanhol (es-ES)
- **Elementos traduzíveis**:
  - Interface (botões, labels, mensagens)
  - Interpretações astrológicas
  - Emails transacionais
- **Formato de datas**: Conforme locale (DD/MM/YYYY para pt-BR)
- **Fuso horário**: Display no timezone do usuário

#### RNF-018: UX - Feedback ao Usuário
- **Loading states**: Skeleton screens, spinners
- **Confirmações**: Modal para ações destrutivas (deletar mapa)
- **Notificações**: Toast messages (sucesso, erro, info)
- **Validação de formulários**: Inline, em tempo real
- **Mensagens de erro**: Claras, acionáveis ("Email já cadastrado. Esqueceu a senha?")

### 3.6 Disponibilidade e Confiabilidade

#### RNF-019: Uptime
- **Requisito**: 99.5% uptime (SLA)
- **Downtime permitido**: ~3.65 horas/mês
- **Manutenção programada**: Janela de 2h, domingo 2-4 AM BRT
- **Notificação**: Aviso prévio de 48h para manutenções

#### RNF-020: Monitoramento
- **Healthchecks**: Endpoint `/health` (HTTP 200)
- **Métricas**:
  - Uptime, response time
  - Taxa de erro (4xx, 5xx)
  - CPU, memória, disco
  - Fila de jobs (Celery)
- **Alertas**:
  - Downtime > 1 minuto
  - Error rate > 5%
  - Response time p95 > 1s
- **Ferramentas**: Prometheus + Grafana, ou Datadog

#### RNF-021: Tratamento de Erros
- **Erros de usuário**: Mensagens claras, sugestões de correção
- **Erros de sistema**: Log detalhado, mensagem genérica ao usuário
- **Fallbacks**:
  - API de geocoding indisponível → Permitir input manual de lat/long
  - Geração de PDF falha → Notificar usuário, permitir retry
- **Retry logic**: Exponential backoff para chamadas externas

### 3.7 Manutenibilidade

#### RNF-022: Qualidade de Código
- **Linting**:
  - Backend: Ruff (Python)
  - Frontend: ESLint + Prettier
- **Type checking**:
  - Backend: mypy (Python type hints)
  - Frontend: TypeScript strict mode
- **Code coverage**: Mínimo 70% (testes unitários)
- **Code review**: Obrigatório para merge em main

#### RNF-023: Documentação
- **README**: Setup, instalação, arquitetura
- **API Docs**: OpenAPI/Swagger (auto-gerado pelo FastAPI)
- **Código**: Docstrings (Python), JSDoc (TypeScript)
- **ADRs** (Architecture Decision Records): Decisões importantes documentadas

#### RNF-024: Versionamento
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Changelog**: CHANGELOG.md atualizado a cada release
- **Git flow**: Feature branches, PR para main
- **Tags**: Cada release taggeada (v1.0.0, v1.1.0, etc.)

---

## 4. Stack Tecnológica Detalhada

### 4.1 Backend

#### Linguagem e Framework
- **Python 3.13+**: Moderna, forte ecossistema científico
- **FastAPI 0.108+**:
  - Alta performance (baseado em Starlette + Pydantic)
  - Validação automática de dados (Pydantic)
  - Documentação automática (OpenAPI)
  - Async/await nativo
  - Type hints obrigatórios

#### Bibliotecas Principais

**Cálculos Astrológicos:**
- `pyswisseph 2.10.3+`: Cálculos ephemeris (Swiss Ephemeris)
- Instalação: `pip install pyswisseph`
- Download de arquivos efemeris: https://www.astro.com/ftp/swisseph/ephe/

**Banco de Dados:**
- `sqlalchemy 2.0+`: ORM assíncrono
- `alembic 1.13+`: Migrations
- `psycopg[binary] 3.1+`: Driver PostgreSQL (async)

**Autenticação:**
- `python-jose[cryptography]`: JWT handling
- `passlib[bcrypt]`: Password hashing
- `python-multipart`: Form data
- `authlib`: OAuth2 clients (Google, Facebook, GitHub)

**Geolocalização:**
- `timezonefinder 6.4+`: Lat/long → timezone
- `httpx 0.25+`: HTTP client async (para APIs externas)

**PDF Generation:**
- `Jinja2 3.1+`: Templating
- `jtex`: Jinja + LaTeX rendering
- Sistema: TeX Live (texlive-full)

**Tasks Assíncronas:**
- `celery[redis] 5.3+`: Task queue
- `redis 5.0+`: Message broker + cache

**Utilidades:**
- `pydantic 2.5+`: Data validation
- `pydantic-settings`: Config management
- `python-dotenv`: .env files

#### Estrutura de Diretórios (Backend)

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, startup/shutdown events
│   ├── config.py               # Settings (Pydantic BaseSettings)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy async engine, session
│   │   ├── security.py         # JWT, password hashing, OAuth2
│   │   ├── dependencies.py     # FastAPI dependencies (get_db, get_current_user)
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── chart.py            # BirthChart model
│   │   └── audit.py            # AuditLog model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # UserCreate, UserRead, UserUpdate
│   │   ├── chart.py            # ChartCreate, ChartRead, ChartData
│   │   ├── auth.py             # Token, LoginRequest
│   │   └── geo.py              # Location, Coordinates
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # /auth/login, /auth/register, /auth/oauth
│   │   │   ├── users.py        # /users/me, /users/{id}
│   │   │   ├── charts.py       # /charts (CRUD)
│   │   │   ├── geo.py          # /geo/search, /geo/timezone
│   │   │   └── export.py       # /export/pdf, /export/json
│   │   └── router.py           # Main API router
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Login logic, OAuth2 handling
│   │   ├── user_service.py     # User CRUD
│   │   ├── chart_service.py    # Chart CRUD, orchestration
│   │   ├── geo_service.py      # Geocoding, timezone lookup
│   │   └── export_service.py   # PDF, JSON generation
│   ├── astro/
│   │   ├── __init__.py
│   │   ├── calculator.py       # Main calculation engine
│   │   ├── planets.py          # Planetary positions
│   │   ├── houses.py           # House calculation
│   │   ├── aspects.py          # Aspect calculation
│   │   ├── dignities.py        # Essential dignities
│   │   ├── interpretations.py  # Text generation
│   │   └── constants.py        # Astrological constants, tables
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── pdf_generation.py   # Celery tasks for PDF
│   └── templates/
│       └── report.tex.j2       # LaTeX template (Jinja2)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_api/
│   ├── test_services/
│   └── test_astro/
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── requirements.txt
├── pyproject.toml              # Poetry ou setuptools
└── Dockerfile
```

### 4.2 Frontend

#### Framework e Bibliotecas
- **React 18+**: UI library
- **TypeScript 5+**: Type safety
- **Vite 5+**: Build tool (rápido, HMR)

**Roteamento:**
- `react-router-dom 6+`: Client-side routing

**Estado:**
- `zustand 4+` OU `@tanstack/react-query 5+`: Estado global leve
- React Query para cache de API

**Formulários:**
- `react-hook-form 7+`: Performance, validação
- `zod 3+`: Schema validation (integra com react-hook-form)

**UI Components:**
- `@radix-ui/*`: Primitivos acessíveis (unstyled)
- `tailwindcss 3+`: Utility-first CSS
- `lucide-react`: Ícones modernos

**Visualização de Mapas:**
- `astrochart` (Kibo): Gráficos astrológicos SVG
- `d3.js` (se necessário customização extra)

**HTTP Client:**
- `axios 1+` OU `@tanstack/react-query` (com fetch)

**Autenticação:**
- `react-oauth/google`: Google login
- Custom hooks para JWT handling

**Utilidades:**
- `date-fns 3+`: Manipulação de datas
- `clsx` + `tailwind-merge`: Conditional classes

#### Estrutura de Diretórios (Frontend)

```
apps/web/
├── src/
│   ├── main.tsx                # Entry point
│   ├── App.tsx                 # Root component, Router
│   ├── components/
│   │   ├── ui/                 # Base components (Button, Input, Modal, etc.)
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── OAuthButtons.tsx
│   │   ├── chart/
│   │   │   ├── ChartForm.tsx
│   │   │   ├── ChartVisualization.tsx
│   │   │   ├── ChartList.tsx
│   │   │   ├── ChartCard.tsx
│   │   │   └── PlanetTable.tsx
│   │   └── geo/
│   │       └── LocationSearch.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ChartCreatePage.tsx
│   │   ├── ChartViewPage.tsx
│   │   └── ProfilePage.tsx
│   ├── hooks/
│   │   ├── useAuth.ts          # Auth context/hook
│   │   ├── useCharts.ts        # React Query hooks
│   │   └── useLocation.ts      # Geo hooks
│   ├── services/
│   │   ├── api.ts              # Axios instance, interceptors
│   │   ├── authService.ts      # Login, register, refresh token
│   │   ├── chartService.ts     # Chart CRUD
│   │   └── geoService.ts       # Geocoding, timezone
│   ├── store/
│   │   └── authStore.ts        # Zustand store (se usar)
│   ├── types/
│   │   ├── chart.ts            # Chart, Planet, Aspect types
│   │   ├── user.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── cn.ts               # clsx + tailwind-merge
│   │   ├── formatters.ts       # Date, number formatters
│   │   └── validators.ts       # Zod schemas
│   └── styles/
│       └── globals.css         # Tailwind imports, custom styles
├── public/
│   ├── favicon.ico
│   └── images/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile
```

### 4.3 Banco de Dados

#### PostgreSQL 16+

**Escolha justificada**:
- ACID compliance (dados pessoais sensíveis)
- JSONB para flexibilidade (dados de mapas)
- Excelente performance para leitura/escrita
- Suporte robusto a índices
- Row-level security (futuro: multi-tenant)

**Schema Principal**:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL se apenas OAuth
    full_name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    locale VARCHAR(10) DEFAULT 'pt-BR',
    timezone VARCHAR(50),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- OAuth Accounts (para social login)
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,  -- 'google', 'facebook', 'github'
    provider_user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_user_id ON oauth_accounts(user_id);

-- Birth Charts table
CREATE TABLE birth_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    person_name VARCHAR(100) NOT NULL,
    gender VARCHAR(50),  -- opcional
    birth_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    birth_timezone VARCHAR(50) NOT NULL,  -- IANA timezone
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    notes TEXT,
    tags VARCHAR(50)[],  -- Array de tags

    -- Configurações de cálculo
    house_system VARCHAR(20) DEFAULT 'placidus',
    zodiac_type VARCHAR(20) DEFAULT 'tropical',
    node_type VARCHAR(20) DEFAULT 'true',

    -- Dados calculados (JSONB para flexibilidade)
    chart_data JSONB NOT NULL,

    -- Metadados
    visibility VARCHAR(20) DEFAULT 'private',  -- 'private', 'shared', 'public'
    share_uuid UUID UNIQUE,  -- Para compartilhamento
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

CREATE INDEX idx_charts_user_id ON birth_charts(user_id);
CREATE INDEX idx_charts_created_at ON birth_charts(created_at);
CREATE INDEX idx_charts_share_uuid ON birth_charts(share_uuid);
CREATE INDEX idx_charts_deleted_at ON birth_charts(deleted_at);  -- Soft delete queries

-- Estrutura do chart_data JSONB:
{
  "planets": [
    {
      "name": "Sun",
      "longitude": 45.123,
      "latitude": 0.002,
      "speed": 0.985,
      "retrograde": false,
      "sign": "Taurus",
      "degree": 15.123,
      "house": 10,
      "dignities": {
        "ruler": false,
        "exaltation": false,
        "detriment": false,
        "fall": false,
        "triplicity_score": 3,
        "term_score": 0,
        "face_score": 1,
        "total_score": 4
      }
    },
    // ... outros planetas
  ],
  "houses": [
    {"number": 1, "cusp": 123.456, "sign": "Leo"},
    // ... 12 casas
  ],
  "aspects": [
    {
      "planet1": "Sun",
      "planet2": "Moon",
      "aspect": "trine",
      "orb": 2.3,
      "applying": true
    },
    // ... outros aspectos
  ],
  "chart_info": {
    "ascendant": 123.456,
    "mc": 234.567,
    "sect": "diurnal",
    "lot_of_fortune": 198.765
  },
  "fixed_stars": [
    {"name": "Regulus", "longitude": 150.0, "conjunct_planet": "Sun"}
  ]
}

-- Audit Log (para compliance LGPD)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- 'login', 'create_chart', 'delete_chart', etc.
    resource_type VARCHAR(50),  -- 'user', 'chart'
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_action ON audit_logs(action);

-- Cached Locations (para otimização)
CREATE TABLE cached_locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    country VARCHAR(100),
    state VARCHAR(100),
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    timezone VARCHAR(50),
    population INTEGER,
    search_rank INTEGER DEFAULT 0,  -- Para ordenação nos resultados
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_locations_name ON cached_locations USING gin(to_tsvector('portuguese', name));
CREATE INDEX idx_locations_coords ON cached_locations(latitude, longitude);
```

**Migrations**: Alembic para versionamento de schema

### 4.4 Infraestrutura

#### Desenvolvimento

**Docker Compose**:
```yaml
version: '3.9'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: astro_dev
      POSTGRES_USER: astro
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./apps/api
    command: uvicorn app.main:app --host 0.0.0.0 --reload
    volumes:
      - ./apps/api:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://astro:dev_password@db:5432/astro_dev
      REDIS_URL: redis://redis:6379/0

  celery_worker:
    build: ./apps/api
    command: celery -A app.tasks worker --loglevel=info
    volumes:
      - ./apps/api:/app
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://astro:dev_password@db:5432/astro_dev
      REDIS_URL: redis://redis:6379/0

  web:
    build: ./apps/web
    command: npm run dev
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

#### Produção

**Opções de deployment**:

1. **VPS (DigitalOcean, Linode, Hetzner)**:
   - Docker Compose (production mode)
   - Nginx como reverse proxy
   - Certbot para SSL/TLS
   - Custo baixo (~$20-40/mês)

2. **Cloud (AWS, GCP)**:
   - ECS/Fargate (containers)
   - RDS PostgreSQL (managed)
   - ElastiCache Redis (managed)
   - S3 para PDFs gerados
   - CloudFront CDN
   - Custo médio (~$100-200/mês)

3. **Platform-as-a-Service**:
   - Render.com, Railway.app
   - Managed PostgreSQL e Redis
   - Deployment automático via Git
   - Custo baixo/médio (~$30-80/mês)

**Recomendação inicial**: VPS (DigitalOcean) para MVP, migrar para cloud quando escalar.

### 4.5 Monorepo

#### Turborepo

**turbo.json**:
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

**package.json (root)**:
```json
{
  "name": "astro-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint"
  },
  "devDependencies": {
    "turbo": "^1.11.0"
  }
}
```

---

## 5. Arquitetura do Sistema

### 5.1 Visão Geral

```
┌─────────────┐
│   Cliente   │  (Browser)
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│    Nginx    │  (Reverse Proxy, SSL Termination)
└──────┬──────┘
       │
       ├──────────────┬─────────────────┐
       │              │                 │
       ▼              ▼                 ▼
┌──────────┐   ┌──────────┐     ┌───────────┐
│  React   │   │ FastAPI  │     │  Static   │
│   SPA    │   │   API    │     │  Assets   │
└──────────┘   └────┬─────┘     └───────────┘
                    │
         ┌──────────┼──────────┬──────────┐
         │          │          │          │
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Postgres│ │ Redis  │ │Geocode │ │ Celery │
    │   DB   │ │ Cache  │ │  API   │ │ Worker │
    └────────┘ └────────┘ └────────┘ └────┬───┘
                                          │
                                          ▼
                                     ┌────────┐
                                     │  PDF   │
                                     │ Output │
                                     └────────┘
```

### 5.2 Fluxo de Criação de Mapa Natal

```
1. Usuário preenche formulário no React
   ↓
2. Frontend valida dados (Zod schema)
   ↓
3. POST /api/v1/charts (JSON com dados de nascimento)
   ↓
4. FastAPI endpoint recebe requisição
   ↓
5. Valida JWT, identifica usuário
   ↓
6. Valida dados (Pydantic schema)
   ↓
7. ChartService.create_chart()
   ├─ GeoService.get_coordinates(city, country)
   │  └─ Chama API externa ou consulta cache
   ├─ GeoService.get_timezone(lat, lon, datetime)
   │  └─ timezonefinder + pytz
   ├─ AstroCalculator.calculate_chart()
   │  ├─ swisseph.calc_ut() para cada planeta
   │  ├─ swisseph.houses() para cúspides
   │  ├─ AspectCalculator.find_aspects()
   │  ├─ DignityCalculator.calculate_dignities()
   │  └─ Monta chart_data JSON
   └─ Salva no PostgreSQL (birth_charts table)
   ↓
8. Retorna HTTP 201 Created com chart data
   ↓
9. Frontend redireciona para /charts/{id}
   ↓
10. ChartVisualization renderiza mapa com AstroChart
```

### 5.3 Fluxo de Geração de PDF

```
1. Usuário clica "Exportar PDF" no chart view
   ↓
2. POST /api/v1/export/pdf/{chart_id}
   ↓
3. FastAPI enfileira task no Celery
   ├─ generate_pdf_task.delay(chart_id, user_id)
   └─ Retorna HTTP 202 Accepted com job_id
   ↓
4. Frontend mostra "Gerando PDF..." (polling ou WebSocket)
   ↓
5. Celery Worker processa task:
   ├─ Busca chart data do BD
   ├─ Gera SVG do mapa (AstroChart ou backend rendering)
   ├─ Renderiza template LaTeX (Jinja2)
   │  └─ Substitui variáveis: {{ chart.name }}, {{ planets }}, etc.
   ├─ Executa pdflatex (2 passes para ToC/refs)
   ├─ Upload PDF para S3 ou filesystem
   └─ Atualiza status da task
   ↓
6. Frontend detecta conclusão (polling endpoint /tasks/{job_id})
   ↓
7. GET /api/v1/export/pdf/{chart_id}/download
   ↓
8. FastAPI retorna presigned URL (S3) ou streaming file
   ↓
9. Browser baixa PDF
```

### 5.4 Padrões Arquiteturais

#### Camadas (Layered Architecture)

1. **Presentation Layer** (React): UI, user interactions
2. **API Layer** (FastAPI routes): HTTP handling, request/response
3. **Service Layer** (services/): Business logic, orchestration
4. **Domain Layer** (astro/): Core astrological logic
5. **Data Layer** (models/, PostgreSQL): Persistence

#### Repository Pattern
- `UserRepository`, `ChartRepository` para abstrair acesso ao BD
- Permite trocar BD sem mudar services

#### Dependency Injection
- FastAPI `Depends()` para injeção de dependências
- Exemplo: `get_db()`, `get_current_user()`

#### CQRS (parcial)
- Separação de leitura (queries) e escrita (commands)
- Queries podem usar índices otimizados
- Commands passam por validação completa

---

## 6. Segurança e Compliance

### 6.1 Segurança da Aplicação

#### Autenticação
- Senhas hasheadas com bcrypt (cost factor 12)
- JWT com expiração curta (15 min access, 30 dias refresh)
- Refresh tokens em HTTP-only cookies (SameSite=Strict)
- OAuth2 para social login (PKCE flow)

#### Autorização
- Role-Based Access Control (RBAC): user, admin
- Row-level security: usuário só acessa próprios mapas
- API endpoints protegidos com `Depends(get_current_user)`

#### Proteção de APIs
- Rate limiting (SlowAPI ou Redis)
- CORS configurado (whitelist de origins)
- CSRF protection para state-changing operations
- Input validation (Pydantic, Zod)
- SQL Injection: ORM (SQLAlchemy) previne
- XSS: React escapa automaticamente, sanitização extra se necessário

#### Comunicação
- HTTPS obrigatório em produção (TLS 1.3)
- HSTS headers
- Secure cookies (Secure, HttpOnly, SameSite)

#### Secrets Management
- Variáveis de ambiente (.env files, nunca commitados)
- Produção: Secrets manager (AWS Secrets Manager, Vault)
- Rotação de secrets (DB passwords, API keys)

### 6.2 LGPD / GDPR Compliance

#### Dados Coletados
- **Identificação**: Nome, email
- **Dados sensíveis**: Data/hora/local de nascimento (dados pessoais)
- **Técnicos**: IP, user agent (logs)

#### Princípios

**Consentimento**:
- Aceite explícito dos Termos de Uso e Política de Privacidade
- Checkbox obrigatório no registro

**Finalidade**:
- Dados usados apenas para geração de mapas natais
- Não compartilhamos com terceiros (exceto providers necessários: OAuth, geocoding)

**Minimização**:
- Coletamos apenas dados necessários
- Campos opcionais claramente marcados

**Acesso**:
- Usuário pode visualizar todos os dados: perfil + mapas
- Download completo em JSON (portabilidade)

**Retificação**:
- Usuário pode editar perfil e notas de mapas
- Dados de nascimento não editáveis (criar novo mapa)

**Exclusão**:
- Delete account: soft delete (30 dias para recuperação)
- Após 30 dias: hard delete permanente (irreversível)
- Direito ao esquecimento: email para suporte

**Segurança**:
- Criptografia em trânsito (HTTPS) e repouso (PostgreSQL encrypted volumes)
- Backups criptografados
- Acesso restrito ao BD (credenciais seguras)

**Auditoria**:
- Logs de ações críticas (login, criação, exclusão)
- Retenção de logs: 90 dias
- Logs sem dados sensíveis

#### Documentação Legal
- **Termos de Uso**: Regras de uso do serviço
- **Política de Privacidade**: Como coletamos, usamos, protegemos dados
- **DPO/Encarregado**: Email de contato para questões de privacidade

---

## 7. Testes

### 7.1 Backend

#### Testes Unitários (Pytest)
- **Services**: Testar lógica de negócio isoladamente (mocks do BD)
- **Astro calculations**: Validar cálculos contra casos conhecidos
- **Utilities**: Formatters, validators

**Exemplo**:
```python
def test_calculate_sun_position():
    """Testa posição do Sol para data conhecida"""
    result = calculator.calculate_planet_position(
        planet='Sun',
        jd=2451545.0  # 2000-01-01 12:00 UTC
    )
    assert abs(result.longitude - 280.46) < 0.01  # Tolerância de 0.01°
```

#### Testes de Integração
- **API endpoints**: TestClient do FastAPI
- **Database**: Usar BD de teste (transações rollback)
- **Services + Repository**: Fluxo completo sem mocks

**Exemplo**:
```python
def test_create_chart(client, auth_headers):
    response = client.post(
        "/api/v1/charts",
        json={
            "person_name": "Test Person",
            "birth_datetime": "1990-05-15T14:30:00",
            "city": "São Paulo",
            "country": "Brazil"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["person_name"] == "Test Person"
    assert "chart_data" in data
```

#### Testes de Performance
- Benchmarking de cálculos: tempo < 2s
- Load testing: Locust ou K6

**Coverage**: Mínimo 70% (pytest-cov)

### 7.2 Frontend

#### Testes Unitários (Vitest)
- **Componentes**: Renderização, props
- **Hooks**: Lógica customizada
- **Utils**: Formatters, validators

**Testing Library**: @testing-library/react

**Exemplo**:
```typescript
test('renders login form', () => {
  render(<LoginForm />);
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
});
```

#### Testes de Integração
- **Fluxos completos**: Login → Dashboard → Criar Mapa
- **MSW** (Mock Service Worker) para mockar API

#### Testes E2E (Playwright)
- **Cenários críticos**:
  - Registro → Verificação email → Login
  - Login → Criar mapa → Visualizar → Exportar PDF
  - Editar perfil → Logout

**Exemplo**:
```typescript
test('create birth chart flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.goto('/charts/new');
  await page.fill('input[name="person_name"]', 'John Doe');
  // ... preencher formulário
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/charts\/[a-f0-9-]+/);
  await expect(page.locator('svg.astro-chart')).toBeVisible();
});
```

### 7.3 Validação de Cálculos Astrológicos

#### Casos de Teste Conhecidos
- **Comparar com astro.com**: 20+ mapas de referência
- **Eclipses históricos**: Validar posições exatas
- **Datas especiais**: Equinócios, solstícios

#### Tolerâncias
- Posições planetárias: ± 0.001°
- Cúspides de casas: ± 0.01°
- Aspectos: orb calculado preciso

---

## 8. Performance e Otimizações

### 8.1 Backend

#### Cálculos
- **Cache de efemérides**: Carregar arquivos Swiss Ephemeris uma vez
- **Processamento paralelo**: Calcular planetas simultaneamente (asyncio)
- **Memoization**: Cache de cálculos repetidos (Redis, 1h TTL)

#### Banco de Dados
- **Índices**: Em colunas frequentemente consultadas (user_id, created_at)
- **Connection pooling**: SQLAlchemy pool (min: 5, max: 20)
- **Queries otimizadas**: Evitar N+1, usar joins quando apropriado
- **JSONB indexing**: GIN index em `chart_data` para queries específicas

#### API
- **Paginação**: Limitar resultados (20-50 por página)
- **Campos selecionáveis**: GraphQL ou field filtering (`?fields=id,name`)
- **Compressão**: Gzip/Brotli para respostas
- **ETags**: Cache HTTP para recursos estáticos

### 8.2 Frontend

#### Bundle Size
- **Code splitting**: Lazy load de rotas e componentes pesados
- **Tree shaking**: Remover código não usado
- **Minification**: Vite automático em produção

#### Carregamento
- **Preload crítico**: Fontes, CSS essencial
- **Lazy images**: Carregar imagens sob demanda
- **CDN**: Servir assets estáticos via CDN

#### Renderização
- **Virtualization**: react-window para listas longas
- **Debouncing**: Inputs de busca (300ms)
- **Throttling**: Scroll handlers

#### Cache
- **React Query**: Cache automático de dados da API (5 min default)
- **Service Worker**: Cache de assets (futuro: PWA)

---

## 9. Monitoramento e Observabilidade

### 9.1 Métricas

#### Aplicação (APM)
- **Ferramentas**: Sentry (errors), Datadog ou Prometheus+Grafana
- **Métricas**:
  - Request rate, error rate, latency (p50, p95, p99)
  - CPU, memória por container
  - Tamanho da fila do Celery

#### Negócio
- **Eventos**:
  - Registros de usuários
  - Mapas criados
  - PDFs gerados
  - Logins (total, sucesso, falhas)
- **Dashboards**: Grafana ou Metabase

### 9.2 Logs

#### Estruturados (JSON)
```json
{
  "timestamp": "2025-01-14T10:30:00Z",
  "level": "INFO",
  "service": "api",
  "user_id": "uuid",
  "action": "create_chart",
  "duration_ms": 1523,
  "ip": "192.168.1.1"
}
```

#### Agregação
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (Grafana Labs, leve)
- **Cloud**: CloudWatch (AWS), Cloud Logging (GCP)

### 9.3 Alertas

#### Condições
- **Uptime < 99%**: Alerta crítico
- **Error rate > 5%**: Alerta alto
- **Response time p95 > 1s**: Alerta médio
- **Disco > 80%**: Alerta aviso

#### Canais
- Email
- Slack/Discord webhook
- PagerDuty (para on-call)

---

## 10. Roadmap de Desenvolvimento

### Fase 1: MVP (8-10 semanas)

**Semanas 1-2: Setup e Infraestrutura**
- Estrutura do monorepo (Turborepo)
- Docker Compose para dev
- PostgreSQL + migrations (Alembic)
- FastAPI boilerplate
- React + Vite boilerplate
- CI/CD básico (GitHub Actions)

**Semanas 3-4: Autenticação**
- Registro de usuários (JWT)
- Login tradicional
- OAuth2 (Google, GitHub)
- Perfil de usuário
- Testes

**Semanas 5-7: Engine Astrológico**
- Integração PySwisseph
- Cálculo de planetas, casas, aspectos
- Dignidades essenciais
- Sect, Lot of Fortune
- Validação de precisão (testes comparativos)

**Semanas 8-9: Interface e Visualização**
- Formulário de criação de mapa
- Integração com geocoding API
- Visualização com AstroChart
- Lista de mapas (CRUD)
- Dashboard de usuário

**Semana 10: Análise e Export**
- Geração de interpretação textual (templates básicos)
- Export JSON
- Testes E2E
- Ajustes finais

### Fase 2: Enriquecimento (4-6 semanas)

- Geração de PDF com LaTeX
- Interpretações mais ricas (mais templates)
- Estrelas fixas
- Melhorias de UX/UI
- Tema dark mode
- Internacionalização (i18n)

### Fase 3: Features Avançadas (futuro)

- Trânsitos planetários
- Sinastria (comparação de mapas)
- Progressões secundárias
- Solar return
- Compartilhamento de mapas
- Sistema de comentários
- Integração com calendário (Google Calendar)
- Notificações (email, push) para trânsitos importantes

### Fase 4: Escalabilidade e Otimização

- Microserviços (separar cálculos em serviço independente)
- Kubernetes para orquestração
- Cache agressivo (Redis)
- CDN global
- Multi-região (latência baixa mundial)

---

## 11. Considerações Finais e Boas Práticas

### 11.1 Precisão Astrológica

#### Validação Contínua
- Comparar outputs com astro.com regularmente
- Manter suite de testes de regressão
- Documentar diferenças (se houver) e justificar

#### Fontes de Dados
- Swiss Ephemeris: padrão-ouro (JPL DE431)
- Atualizar arquivos de efemérides anualmente
- Considerar efemérides de longo prazo para datas antigas/futuras

#### Configurações Avançadas
- Permitir escolha de Ayanamsa (se sidereal)
- Diferentes sistemas de dignidades (Ptolemaico, Dorothean)
- Orbs customizáveis (usuários avançados)

### 11.2 Experiência do Usuário

#### Onboarding
- Tutorial interativo na primeira visita
- Tooltips explicativas em termos astrológicos
- Demo chart (exemplo pré-carregado)

#### Acessibilidade
- Testes com screen readers (NVDA, JAWS, VoiceOver)
- Navegação completa por teclado
- Alto contraste
- Textos alternativos para gráficos

#### Performance Percebida
- Skeleton screens durante loading
- Otimização de imagens (lazy loading)
- Feedback imediato a ações do usuário

### 11.3 Manutenibilidade

#### Documentação
- README detalhado por app (api, web)
- ADRs para decisões arquiteturais
- Docstrings em funções complexas
- Comentários em lógica não-óbvia

#### Testes
- Coverage > 70%
- Testes de regressão para bugs corrigidos
- CI/CD roda testes automaticamente

#### Code Quality
- Linters configurados (Ruff, ESLint)
- Pre-commit hooks (lint, format)
- Code reviews obrigatórios

### 11.4 Ética e Responsabilidade

#### Disclaimers
- Astrologia é ferramenta de autoconhecimento, não diagnóstico
- Não substitui aconselhamento profissional (psicológico, médico)
- Disclaimer visível em relatórios e interface

#### Privacidade
- Dados de nascimento são sensíveis
- Encorajar usuários a não compartilhar mapas publicamente sem consentimento
- Recursos de privacidade claros

#### Conteúdo
- Interpretações balanceadas (não alarmistas)
- Evitar linguagem determinista ("vai acontecer")
- Preferir "tendência", "potencial", "possibilidade"

---

## 12. Glossário de Termos Astrológicos

**Ascendente (AC)**: Signo que estava nascendo no horizonte leste no momento do nascimento. Cúspide da Casa 1.

**Aspect (Aspecto)**: Ângulo entre dois planetas. Principais: conjunção (0°), sextil (60°), quadratura (90°), trígono (120°), oposição (180°).

**Cusp (Cúspide)**: Início de uma casa astrológica.

**Descendente (DC)**: Ponto oposto ao Ascendente. Cúspide da Casa 7.

**Dignity (Dignidade)**: Força de um planeta baseado em sua posição. Essencial (signo) e Acidental (casa, aspectos).

**Ephemeris (Efeméride)**: Tabela de posições planetárias ao longo do tempo.

**House (Casa)**: Divisão da carta em 12 setores, representando áreas da vida.

**Imum Coeli (IC)**: Ponto mais baixo da carta. Cúspide da Casa 4.

**Medium Coeli (MC)**: Ponto mais alto da carta (Meio do Céu). Cúspide da Casa 10.

**Node (Nodo Lunar)**: Ponto de intersecção da órbita da Lua com a eclíptica. Nodo Norte (ascendente), Nodo Sul (descendente).

**Orb (Orbe)**: Margem de tolerância para aspectos (ex: trígono de 120° ± 8°).

**Retrograde (Retrógrado)**: Movimento aparente de um planeta para trás no zodíaco.

**Sect**: Determinação se um mapa é diurno (Sol acima do horizonte) ou noturno (Sol abaixo).

**Sidereal**: Zodíaco baseado nas constelações fixas.

**Tropical**: Zodíaco baseado nas estações (equinócios/solstícios). Padrão na astrologia ocidental.

---

## 13. Referências

### Astrologia
- Brennan, Chris. "Hellenistic Astrology: The Study of Fate and Fortune"
- Hand, Robert. "Horoscope Symbols"
- Astro.com: https://www.astro.com

### Técnicas
- Swiss Ephemeris Documentation: https://www.astro.com/swisseph/
- PySwisseph: https://github.com/astrorigin/pyswisseph
- AstroChart: https://github.com/Kibo/AstroChart

### Web Development
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- PostgreSQL Docs: https://www.postgresql.org/docs/

### Compliance
- LGPD (Lei Geral de Proteção de Dados): http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- GDPR: https://gdpr-info.eu/

---

**Documento elaborado em**: 2025-01-14
**Versão**: 1.0
**Autor**: Sistema de Especificação Técnica
**Revisão**: Aguardando aprovação
