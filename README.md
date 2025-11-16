<div align="center">
  <img src="ux/figures/logo-transparent.png" alt="Real Astrology - Sistema de Mapas Natais" width="200"/>

  # Real Astrology - Sistema de Mapas Natais com Astrologia Tradicional

  Sistema web completo para geração e análise de mapas natais utilizando astrologia tradicional, com cálculos astronômicos de alta precisão baseados em Swiss Ephemeris.

  [![Stars](https://img.shields.io/github/stars/lmeazzini/astro-natal-chart?style=for-the-badge)](https://github.com/lmeazzini/astro-natal-chart/stargazers)
  [![License](https://img.shields.io/github/license/lmeazzini/astro-natal-chart?style=for-the-badge)](LICENSE)
</div>

## Características Principais

- **Cálculos Precisos**: Swiss Ephemeris (JPL DE431) com erro < 1 arcsecond
- **Astrologia Tradicional**: Dignidades essenciais, sect, triplicidades
- **Interpretações IA**: Geração automática de interpretações usando OpenAI GPT-4o-mini
- **Visualização Profissional**: Gráficos SVG interativos
- **Exportação LaTeX**: PDFs profissionais de alta qualidade
- **Autenticação Completa**: JWT + OAuth2 (Google, GitHub, Facebook)
- **Interface Moderna**: React + TypeScript + Tailwind CSS
- **API RESTful**: FastAPI com documentação automática (OpenAPI)

## Stack Tecnológica

### Backend
- **Python 3.11+** com FastAPI
- **PostgreSQL 16** (JSONB para dados flexíveis)
- **PySwisseph** para cálculos astrológicos
- **Celery + Redis** para processamento assíncrono
- **SQLAlchemy 2.0** (async ORM)
- **LaTeX + Jinja2** para geração de PDFs

### Frontend
- **React 18+** com TypeScript
- **Vite** (build tool)
- **TailwindCSS** (estilização)
- **AstroChart** (visualização de mapas)
- **React Query** (cache e gerenciamento de estado)
- **React Hook Form + Zod** (formulários e validação)

### Infraestrutura
- **Turborepo** (monorepo)
- **Docker + Docker Compose**
- **Nginx** (reverse proxy)

## Estrutura do Projeto

```
astro-natal-chart-monorepo/
├── apps/
│   ├── api/              # Backend FastAPI
│   └── web/              # Frontend React
├── packages/
│   ├── shared-types/     # TypeScript types compartilhados
│   └── ui-components/    # Componentes React reutilizáveis
├── docs/
│   └── PROJECT_SPEC.md   # Especificação técnica completa
├── package.json          # Workspace root
├── turbo.json            # Configuração Turborepo
└── docker-compose.yml    # Ambiente de desenvolvimento
```

## Pré-requisitos

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **PostgreSQL** >= 16
- **Redis** >= 7
- **TeX Live** (para geração de PDFs)
- **Docker** (opcional, recomendado)

## Instalação

### Opção 1: Com Docker (Recomendado)

```bash
# Clonar repositório
git clone <repo-url>
cd astro

# Iniciar todos os serviços
docker-compose up -d

# Aplicar migrations
docker-compose exec api alembic upgrade head

# Acessar:
# - Frontend: http://localhost:5173
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Opção 2: Desenvolvimento Local

```bash
# Instalar dependências
npm install

# Backend
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar .env (ver apps/api/.env.example)
cp .env.example .env

# Executar migrations
alembic upgrade head

# Frontend
cd apps/web
npm install

# Executar em modo desenvolvimento (de volta à raiz)
cd ../..
npm run dev
```

## Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev          # Iniciar todos os apps em modo dev

# Build
npm run build        # Build de produção

# Testes
npm run test         # Executar todos os testes

# Linting
npm run lint         # Lint em todos os workspaces
npm run format       # Formatar código com Prettier

# Limpeza
npm run clean        # Remover node_modules e build artifacts
```

## Configuração

### Variáveis de Ambiente (Backend)

Criar `apps/api/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/astro_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Geocoding API
OPENCAGE_API_KEY=your-opencage-api-key

# OpenAI (REQUIRED for AI interpretations)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# Email Domain Restriction
ENABLE_EMAIL_DOMAIN_RESTRICTION=true
ALLOWED_EMAIL_DOMAINS=realastrology

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Variáveis de Ambiente (Frontend)

Criar `apps/web/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### Configuração do OpenAI (Interpretações IA)

O sistema gera automaticamente interpretações astrológicas usando OpenAI GPT-4o-mini. Para habilitar este recurso:

1. **Criar conta OpenAI**: Acesse [platform.openai.com](https://platform.openai.com) e crie uma conta

2. **Obter API key**:
   - Acesse [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Clique em "Create new secret key"
   - Copie a chave (ela só será exibida uma vez)

3. **Adicionar ao .env**:
   ```bash
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
   ```

   **⚠️ IMPORTANTE**: Nunca commit a chave no git! O arquivo `.env` já está no `.gitignore`.

4. **Custo estimado**: ~$0.01 por mapa natal gerado (7 planetas + 12 casas + aspectos)

**Como funciona:**
- Ao criar um mapa natal, interpretações são geradas automaticamente
- Foca apenas nos 7 planetas clássicos (Sol, Lua, Mercúrio, Vênus, Marte, Júpiter, Saturno)
- Considera dignidades essenciais, sect (diurnal/noturno), e contexto tradicional
- Interpretações em português brasileiro com estilo misto (técnico + prático)
- Pode regenerar interpretações via botão "Regenerar" na interface

**Desabilitar interpretações IA:**
Se não configurar a chave OpenAI, os mapas serão criados normalmente, mas sem as interpretações textuais.

### Restrição de Domínio de Email

O sistema permite restringir o cadastro de novos usuários apenas a domínios de email específicos. Esta funcionalidade é útil para controlar o acesso à aplicação.

**Configuração:**

1. **Habilitar restrição**: Configure `ENABLE_EMAIL_DOMAIN_RESTRICTION=true` no `.env` do backend

2. **Domínios permitidos**: Configure `ALLOWED_EMAIL_DOMAINS` com uma lista separada por vírgulas (sem o @)
   ```bash
   ALLOWED_EMAIL_DOMAINS=realastrology,example
   ```

3. **Comportamento**:
   - Quando habilitado, apenas emails dos domínios especificados podem se registrar
   - A validação ocorre tanto no backend (Pydantic validator) quanto no frontend (Zod schema)
   - Tentativas de registro com domínios não autorizados retornam erro descritivo

**Exemplo de mensagem de erro:**
```
Cadastro restrito. Apenas emails dos domínios autorizados são permitidos: @realastrology
```

**Desabilitar restrição:**
Para permitir cadastro com qualquer email, configure `ENABLE_EMAIL_DOMAIN_RESTRICTION=false` no `.env`.

## Arquitetura

### Backend (FastAPI)

O backend segue uma arquitetura em camadas com separação clara de responsabilidades:

1. **API Layer** (`app/api/v1/endpoints/`): Rotas FastAPI, validação de requests/responses
2. **Service Layer** (`app/services/`): Lógica de negócio e orquestração
3. **Repository Layer** (`app/repositories/`): Abstração de acesso a dados
4. **Data Layer** (`app/models/`): Modelos SQLAlchemy e schema do banco

**Padrões Implementados:**
- **Repository Pattern**: Acesso a dados abstraído através de repositories
  - `BaseRepository`: Operações CRUD genéricas (get_by_id, create, update, delete)
  - `UserRepository`: Consultas específicas de usuários (por email, usuários ativos)
  - `ChartRepository`: Consultas de mapas com autorização (por usuário, soft delete, busca, tags)
  - `AuditRepository`: Criação e consulta de logs de auditoria
- **Dependency Injection**: FastAPI `Depends()` para sessão DB e autenticação
- **Async/await**: Totalmente assíncrono (SQLAlchemy async, FastAPI async)

### Frontend (React)

- **Pages**: Componentes de rotas (Login, Register, ChartDetail, NewChart, Charts, Dashboard)
- **Components**: Componentes reutilizáveis (ChartWheel, PlanetList, AspectGrid, HouseTable)
- **Services**: Cliente API baseado em fetch
- **Context**: AuthContext para gerenciamento de autenticação
- **Utils**: Funções utilitárias (símbolos astrológicos, formatação)

## Rate Limiting

O sistema implementa rate limiting para proteger a API contra abuso e controlar custos de APIs externas.

### Limites por Endpoint

| Endpoint | Método | Limite | Janela | Identificação |
|----------|--------|--------|--------|---------------|
| `/auth/login` | POST | 10 | 1 minuto | IP |
| `/auth/register` | POST | 5 | 1 hora | IP |
| `/auth/refresh` | POST | 10 | 1 minuto | IP |
| `/charts/` | POST | 30 | 1 hora | User ID |
| `/charts/` | GET | 100 | 1 minuto | User ID |
| `/charts/{id}` | GET | 200 | 1 minuto | User ID |
| `/charts/{id}` | PUT | 60 | 1 hora | User ID |
| `/charts/{id}` | DELETE | 30 | 1 hora | User ID |
| `/geocoding/search` | GET | 60 | 1 minuto | IP |
| `/geocoding/coordinates` | GET | 60 | 1 minuto | IP |
| `/oauth/login/{provider}` | GET | 10 | 1 minuto | IP |
| `/oauth/callback/{provider}` | GET | 10 | 1 minuto | IP |

### Configuração

O rate limiting utiliza **Redis** como backend de armazenamento e a biblioteca **slowapi** para FastAPI.

**Estratégias:**
- **Endpoints públicos** (login, register, geocoding): Limitados por **endereço IP**
- **Endpoints autenticados** (charts): Limitados por **User ID** (do JWT token)

**Headers de Resposta:**
Quando o limite é excedido (HTTP 429), a resposta inclui:
- `X-RateLimit-Limit`: Limite total de requests
- `X-RateLimit-Remaining`: Requests restantes na janela atual
- `X-RateLimit-Reset`: Timestamp Unix quando o limite será resetado
- `Retry-After`: Segundos até poder tentar novamente

**Exemplo de resposta 429:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "10 per 1 minute"
}
```

### Desabilitar em Desenvolvimento

Para desabilitar rate limiting durante desenvolvimento local (não Docker):

```python
# apps/api/app/core/rate_limit.py
# Comente a linha:
# storage_uri=str(settings.REDIS_URL),

# E use:
storage_uri="memory://",  # In-memory storage (não persistente)
```

**Nota:** Em ambiente Docker, o Redis já está configurado e funciona sem alterações.

## Testes

```bash
# Backend (pytest)
cd apps/api
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes de rate limiting
pytest tests/test_rate_limit.py -v

# Frontend (vitest)
cd apps/web
npm run test

# E2E (playwright)
npm run test:e2e
```

## Documentação

- **Especificação Técnica**: [`PROJECT_SPEC.md`](./PROJECT_SPEC.md) - Requisitos funcionais, não funcionais, arquitetura completa
- **OAuth2 Setup**: [`docs/OAUTH_SETUP.md`](./docs/OAUTH_SETUP.md) - Guia completo de configuração do OAuth2 (Google, GitHub, Facebook)
- **API Docs**: http://localhost:8000/docs (Swagger UI automático)
- **API Redoc**: http://localhost:8000/redoc

## Roadmap

### Fase 1: MVP (10 semanas) ✅ Em Progresso
- [x] Especificação técnica completa
- [x] Setup do monorepo
- [ ] Sistema de autenticação (JWT + OAuth2)
- [ ] Engine de cálculos astrológicos
- [ ] Interface de criação de mapas
- [ ] Visualização gráfica
- [ ] Export básico (JSON)

### Fase 2: Enriquecimento (4-6 semanas)
- [ ] Geração de PDF com LaTeX
- [x] Interpretações textuais ricas (IA com OpenAI GPT-4o-mini)
- [ ] Estrelas fixas
- [ ] Tema dark mode
- [ ] Internacionalização (i18n)

### Fase 3: Features Avançadas
- [ ] Trânsitos planetários
- [ ] Sinastria (comparação de mapas)
- [ ] Progressões secundárias
- [ ] Compartilhamento de mapas

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- **Backend**: Ruff (linting), mypy (type checking), pytest
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Commits**: Conventional Commits (feat:, fix:, docs:, etc.)

## Segurança

- Reportar vulnerabilidades: [security@example.com]
- Compliance: LGPD/GDPR
- Dados sensíveis: Data/hora/local de nascimento são protegidos

## Licença

[Definir licença] - Ver arquivo LICENSE

## Autores

[Seu Nome/Equipe]

## Agradecimentos

- **Swiss Ephemeris** - Cálculos astronômicos precisos
- **AstroChart (Kibo)** - Visualização de mapas natais
- **Astro.com** - Referência para validação de cálculos
- Comunidade open-source de astrologia

---

**Status do Projeto**: 🚧 Em Desenvolvimento Ativo

Para mais detalhes técnicos, consulte [`PROJECT_SPEC.md`](./PROJECT_SPEC.md).
