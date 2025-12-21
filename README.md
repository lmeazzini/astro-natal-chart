<div align="center">
  <img src="ux/figures/logo-transparent.png" alt="Real Astrology - Sistema de Mapas Natais" width="200"/>

  # Real Astrology - Sistema de Mapas Natais com Astrologia Tradicional

  Sistema web completo para geração e análise de mapas natais utilizando astrologia tradicional, com cálculos astronômicos de alta precisão baseados em Swiss Ephemeris.

  [![Stars](https://img.shields.io/github/stars/lmeazzini/astro-natal-chart?style=for-the-badge)](https://github.com/lmeazzini/astro-natal-chart/stargazers)
  [![License](https://img.shields.io/github/license/lmeazzini/astro-natal-chart?style=for-the-badge)](LICENSE)
</div>

## Características Principais

- **Cálculos Precisos**: Swiss Ephemeris (Moshier) com alta precisão
- **Astrologia Tradicional**: Dignidades essenciais, sect, Arabic Parts, temperamento, fases lunares
- **Interpretações IA + RAG**: Geração automática de interpretações usando OpenAI + Qdrant
- **Visualização Profissional**: Gráficos SVG interativos
- **Autenticação Completa**: JWT + OAuth2 (Google, GitHub, Facebook)
- **Verificação de Email**: Tokens JWT com expiração de 24h
- **Reset de Senha**: Tokens SHA256 com expiração de 1h
- **Rate Limiting**: Proteção SlowAPI + Redis em todos endpoints críticos
- **LGPD/GDPR**: Compliance completo com política de privacidade
- **Interface Moderna**: React + TypeScript + Tailwind CSS
- **API RESTful**: FastAPI com documentação automática (OpenAPI)

## Stack Tecnológica

### Backend
- **Python 3.13+** com FastAPI
- **UV** (package manager - 10-100x mais rápido que pip)
- **PostgreSQL 16** (JSONB para dados flexíveis)
- **PySwisseph** para cálculos astrológicos (Moshier ephemeris)
- **Celery + Redis** para processamento assíncrono
- **SQLAlchemy 2.0** (async ORM)
- **Qdrant** para RAG (interpretações IA)
- **Ruff** para linting e formatação
- **Mypy** para type checking

### Frontend
- **React 18+** com TypeScript
- **Vite 5** (build tool com HMR rápido)
- **TailwindCSS** (estilização)
- **Componentes SVG** customizados para visualização de mapas

### Infraestrutura
- **Turborepo** (monorepo)
- **Docker + Docker Compose**
- **AWS S3** (armazenamento de PDFs - opcional)

## Estrutura do Projeto

```
astro-natal-chart-monorepo/
├── apps/
│   ├── api/              # Backend FastAPI (Python 3.13+)
│   │   ├── app/          # Código principal
│   │   │   ├── api/      # Endpoints REST
│   │   │   ├── astro/    # Cálculos astrológicos tradicionais
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── services/ # Lógica de negócio
│   │   │   └── repositories/ # Acesso a dados
│   │   └── tests/        # Testes pytest (439 testes)
│   └── web/              # Frontend React
│       └── src/          # Código React + TypeScript
├── packages/             # (Planejado para código compartilhado)
├── docs/                 # Documentação
│   ├── PROJECT_SPEC.md   # Especificação técnica completa
│   ├── PRIVACY_POLICY.md # Política de privacidade (LGPD)
│   └── TERMS_OF_SERVICE.md # Termos de serviço
├── scripts/              # Scripts de automação (backup, restore)
├── package.json          # Workspace root
├── turbo.json            # Configuração Turborepo
└── docker-compose.yml    # Ambiente de desenvolvimento
```

## Pré-requisitos

- **Node.js** >= 18.0.0
- **Python** >= 3.13
- **UV** (package manager) - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **PostgreSQL** >= 16
- **Redis** >= 7
- **Docker** (recomendado para desenvolvimento)

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
# Instalar dependências do monorepo
npm install

# Backend (usando UV - muito mais rápido que pip)
cd apps/api
uv sync  # Instala todas as dependências do pyproject.toml

# Configurar .env (ver apps/api/.env.example)
cp .env.example .env

# Executar migrations
uv run alembic upgrade head

# Frontend
cd ../web
npm install

# Executar em modo desenvolvimento (de volta à raiz)
cd ../..
npm run dev
```

### Política de Restart dos Containers Docker

Todos os containers Docker possuem a política `restart: unless-stopped` configurada, o que significa:

**Comportamento de Restart Automático:**
- ✅ **Restart após crash**: Se um container falhar ou crashar, ele será automaticamente reiniciado
- ✅ **Restart após reinicialização do sistema**: Os containers reiniciam automaticamente quando o Docker daemon ou o sistema operacional reiniciar
- ✅ **Restart após reinicialização do Docker daemon**: Se o serviço Docker for reiniciado, os containers voltam automaticamente
- ❌ **NÃO restart após stop explícito**: Se você parar um container manualmente com `docker stop` ou `docker-compose stop`, ele NÃO será reiniciado automaticamente

**Serviços com restart automático:**
- `astro-db` (PostgreSQL)
- `astro-redis` (Redis)
- `astro-api` (FastAPI Backend)
- `astro-celery` (Celery Worker)
- `astro-web` (React Frontend)

**Comandos úteis:**
```bash
# Ver status de todos os containers
docker ps -a --filter "name=astro-"

# Parar um serviço específico (NÃO reinicia automaticamente)
docker-compose stop web

# Reiniciar um serviço manualmente
docker-compose restart web

# Parar todos os serviços (NÃO reiniciam automaticamente)
docker-compose stop

# Iniciar todos os serviços
docker-compose up -d
```

**Nota:** Esta política garante alta disponibilidade em produção, mantendo os serviços rodando mesmo após falhas temporárias ou reinicializações do sistema.

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

### Configuração do AWS S3 (Armazenamento de PDFs)

O sistema pode armazenar os PDFs gerados de mapas natais no AWS S3 para persistência e escalabilidade. Por padrão, PDFs são salvos localmente (modo desenvolvimento).

1. **Criar conta AWS** (se não tiver): Acesse [aws.amazon.com](https://aws.amazon.com)

2. **Criar bucket S3**:
   - Acesse o console S3: [s3.console.aws.amazon.com](https://s3.console.aws.amazon.com)
   - Clique em "Create bucket"
   - Nome sugerido: `seu-app-pdfs-dev` (desenvolvimento) ou `seu-app-pdfs-prod` (produção)
   - Região: escolha a mais próxima (ex: `us-east-1`, `sa-east-1`)
   - **Importante**: Mantenha o bucket **privado** (não público)

3. **Criar usuário IAM**:
   - Acesse IAM: [console.aws.amazon.com/iam](https://console.aws.amazon.com/iam)
   - Users → Add user
   - Nome: `astro-pdf-uploader`
   - Access type: Programmatic access
   - Anexe a política customizada:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": [
             "s3:PutObject",
             "s3:GetObject",
             "s3:DeleteObject",
             "s3:ListBucket"
           ],
           "Resource": [
             "arn:aws:s3:::seu-bucket-name/*",
             "arn:aws:s3:::seu-bucket-name"
           ]
         }
       ]
     }
     ```
   - Copie as credenciais: **Access Key ID** e **Secret Access Key**

4. **Adicionar ao .env** (backend):
   ```bash
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIAYEKP5HT3XXXXXXX
   AWS_SECRET_ACCESS_KEY=HVxGhIuj/u0mn+XXXXXXXXXXXXXXXXX
   S3_BUCKET_NAME=seu-bucket-name
   S3_PREFIX=birth-charts
   S3_PRESIGNED_URL_EXPIRATION=3600  # 1 hora (em segundos)
   ```

   **⚠️ SEGURANÇA**: Nunca commit credenciais AWS no git!

5. **Custo estimado** (região us-east-1):
   - Armazenamento: $0.023/GB/mês
   - 1000 PDFs (2MB cada) = 2GB = **< $1/mês**
   - AWS Free Tier: 5GB grátis por 12 meses

**Como funciona:**
- PDFs são gerados localmente com LaTeX
- Upload automático para S3 após geração bem-sucedida
- Arquivo local é deletado após upload (economia de espaço)
- API retorna URLs presignadas (válidas por 1h) para download seguro
- Fallback para armazenamento local se S3 falhar

**Desabilitar S3:**
Deixe as variáveis `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` vazias. PDFs serão salvos em `/media/pdfs/` (local).

### Configuração do Amplitude Analytics (Product Analytics)

O sistema integra com Amplitude para rastreamento de eventos e análise de produto (opcional).

1. **Criar conta Amplitude**: Acesse [analytics.amplitude.com](https://analytics.amplitude.com) e crie uma conta gratuita

2. **Obter API Key**:
   - Acesse o dashboard do Amplitude
   - Vá em Settings → Projects → Seu Projeto
   - Copie a **API Key** (chave pública para JavaScript/frontend)

3. **Adicionar ao .env** (backend):
   ```bash
   AMPLITUDE_API_KEY=your-amplitude-api-key-here
   AMPLITUDE_ENABLED=true
   ```

4. **Adicionar ao .env** (frontend):
   ```bash
   VITE_AMPLITUDE_API_KEY=your-amplitude-api-key-here
   VITE_AMPLITUDE_ENABLED=true
   ```

**Como funciona:**
- Tracking automático de eventos padrão (sessions, page views)
- Eventos customizados podem ser adicionados no código
- Backend: `amplitude_service.track()` em `app/services/amplitude_service.py`
- Frontend: `amplitudeService.track()` em `src/services/amplitude.ts`

**Usando o Amplitude no Código:**

Backend (Python):
```python
from app.services.amplitude_service import amplitude_service

# Rastrear evento
amplitude_service.track(
    event_type="chart_created",
    user_id=str(user.id),
    event_properties={"chart_type": "natal", "house_system": "placidus"}
)

# Identificar usuário
amplitude_service.identify(
    user_id=str(user.id),
    user_properties={"plan": "premium", "locale": "pt-BR"}
)

# Forçar envio de eventos (útil em testes)
amplitude_service.flush()
```

Frontend (TypeScript):
```typescript
import { amplitudeService } from '@/services/amplitude';

# Rastrear evento
amplitudeService.track('button_clicked', {
  button_name: 'generate_pdf',
  chart_id: chartId
});

# Identificar usuário (após login)
amplitudeService.identify(userId, {
  email: user.email,
  subscription: 'premium'
});

# Limpar identidade (após logout)
amplitudeService.reset();
```

**Custo:**
- Free tier: 10M eventos/mês
- Usuários ilimitados
- Retenção de dados: 1 ano

**Desabilitar Amplitude:**
Configure `AMPLITUDE_ENABLED=false` (backend) e `VITE_AMPLITUDE_ENABLED=false` (frontend).

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
# Backend (pytest) - 439 testes
cd apps/api
uv run pytest

# Com coverage
uv run pytest --cov=app --cov-report=html

# Teste específico
uv run pytest tests/test_api/test_auth.py -v

# Frontend (vitest)
cd apps/web
npm run test
```

## Documentação

- **Especificação Técnica**: [`PROJECT_SPEC.md`](./PROJECT_SPEC.md) - Requisitos funcionais, não funcionais, arquitetura completa
- **OAuth2 Setup**: [`docs/OAUTH_SETUP.md`](./docs/OAUTH_SETUP.md) - Guia completo de configuração do OAuth2 (Google, GitHub, Facebook)
- **API Docs**: http://localhost:8000/docs (Swagger UI automático)
- **API Redoc**: http://localhost:8000/redoc

## Roadmap

### Fase 1: MVP (~88% Completo) ✅
- [x] Especificação técnica completa
- [x] Setup do monorepo com Turborepo
- [x] Sistema de autenticação (JWT + OAuth2: Google, GitHub, Facebook)
- [x] Verificação de email e reset de senha
- [x] Engine de cálculos astrológicos (PySwisseph)
- [x] Cálculos tradicionais (dignidades, sect, Arabic Parts, temperamento)
- [x] Interface de criação de mapas com geocoding
- [x] Visualização gráfica (SVG interativo)
- [x] Rate limiting (SlowAPI + Redis)
- [x] LGPD/GDPR compliance
- [x] Backup automation (PostgreSQL + S3)
- [x] Interpretações IA + RAG (OpenAI + Qdrant)
- [x] Profile management e configurações
- [x] Amplitude Analytics

### Fase 2: Enriquecimento
- [ ] Geração de PDF com LaTeX
- [ ] Chiron e asteroides (Ceres, Pallas, Juno, Vesta)
- [ ] Estrelas fixas
- [ ] Tema dark mode
- [ ] Internacionalização (i18n)

### Fase 3: Features Avançadas
- [ ] Profections e Firdaria
- [ ] Solar Returns
- [ ] Trânsitos planetários
- [ ] Sinastria (comparação de mapas)
- [ ] Progressões secundárias
- [ ] Galeria pública de mapas famosos

## Contribuindo

Contribuições são bem-vindas! Veja o guia completo em [`CONTRIBUTING.md`](./CONTRIBUTING.md).

### Git Workflow (GitFlow)

Usamos GitFlow com duas branches principais:

- 🔴 **`main`** - Produção (stable, protected, auto-deploy)
- 🟡 **`dev`** - Desenvolvimento (default branch, staging)

**Quick start:**

```bash
# 1. Clone e configure
git clone <repo-url>
cd astro

# 2. Criar feature branch (sempre a partir de dev)
git checkout dev
git pull origin dev
git checkout -b feature/my-feature

# 3. Desenvolver, testar, commitar
make test
make lint
git commit -m "feat: add my feature"

# 4. Push e abrir PR para dev
git push origin feature/my-feature
gh pr create --base dev
```

### Padrões de Código

- **Backend**: UV (package manager), Ruff (linting + formatting), Mypy (type checking), pytest
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Commits**: Conventional Commits (feat:, fix:, docs:, etc.)
- **PRs**: Sempre para `dev`, nunca direto para `main`
- **CI/CD**: GitHub Actions (backend + frontend checks obrigatórios)

### Pre-commit Hooks

O projeto utiliza **pre-commit** para garantir qualidade do código antes de cada commit. Os hooks verificam automaticamente:

- **Trailing whitespace** e **end of file** fixers
- **YAML e JSON** syntax check
- **Large files** detection (> 1MB)
- **Merge conflicts** detection
- **Private keys** detection
- **Ruff** linting e formatting (backend Python)
- **ESLint** e **Prettier** (frontend TypeScript/React)
- **Conventional Commits** validation

**Instalação:**

```bash
# Instalar pre-commit (via UV no backend)
cd apps/api
uv sync

# Instalar os hooks no repositório
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Rodar em todos os arquivos (primeira vez ou verificação manual)
uv run pre-commit run --all-files
```

**Uso:**
- Hooks rodam automaticamente em cada `git commit`
- Se algum hook falhar, o commit é abortado
- Corrija os problemas e tente commitar novamente
- Para bypass temporário (não recomendado): `git commit --no-verify`

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

**Status do Projeto**: 🚧 MVP em Desenvolvimento (~88% Completo)

**Testes**: 439 testes backend | CI/CD com GitHub Actions

Para mais detalhes técnicos, consulte [`PROJECT_SPEC.md`](./PROJECT_SPEC.md).
