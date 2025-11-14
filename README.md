# Sistema de Mapas Natais - Astrologia Tradicional

Sistema web completo para geração e análise de mapas natais utilizando astrologia tradicional, com cálculos astronômicos de alta precisão baseados em Swiss Ephemeris.

## Características Principais

- **Cálculos Precisos**: Swiss Ephemeris (JPL DE431) com erro < 1 arcsecond
- **Astrologia Tradicional**: Dignidades essenciais, sect, triplicidades
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

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Variáveis de Ambiente (Frontend)

Criar `apps/web/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Testes

```bash
# Backend (pytest)
cd apps/api
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Frontend (vitest)
cd apps/web
npm run test

# E2E (playwright)
npm run test:e2e
```

## Documentação

- **Especificação Técnica**: [`PROJECT_SPEC.md`](./PROJECT_SPEC.md) - Requisitos funcionais, não funcionais, arquitetura completa
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
- [ ] Interpretações textuais ricas
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
