# Astro Natal Chart API

Backend API para sistema de mapas natais com astrologia tradicional.

## Stack Tecnológica

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL 16** - Banco de dados relacional
- **SQLAlchemy 2.0** - ORM assíncrono
- **Alembic** - Migrations
- **PySwisseph** - Cálculos astrológicos (Swiss Ephemeris)
- **Celery + Redis** - Processamento assíncrono
- **JWT** - Autenticação
- **OAuth2** - Login social (Google, GitHub, Facebook)

## Estrutura de Diretórios

```
app/
├── core/              # Configuração, database, security
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── api/               # API routes
│   └── v1/            # API v1
├── services/          # Business logic
├── astro/             # Astrological calculation engine
├── tasks/             # Celery tasks
└── templates/         # Jinja2 templates (LaTeX)
```

## Setup Local

### Pré-requisitos

- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrations
alembic upgrade head

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload
```

Acesse:
- API: http://localhost:8000
- Documentação interativa (Swagger): http://localhost:8000/docs
- Documentação alternativa (ReDoc): http://localhost:8000/redoc

## Migrations

```bash
# Criar nova migration
alembic revision --autogenerate -m "description"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history
```

## Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_api/
pytest tests/test_astro/

# Ver relatório de coverage
open htmlcov/index.html
```

## Linting e Formatação

```bash
# Lint com Ruff
ruff check .

# Auto-fix
ruff check --fix .

# Type checking com mypy
mypy app/
```

## Estrutura de Dados

### User
```python
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "João Silva",
    "email_verified": true,
    "is_active": true,
    "created_at": "2025-01-14T10:00:00Z"
}
```

### Birth Chart
```python
{
    "id": "uuid",
    "user_id": "uuid",
    "person_name": "Maria Santos",
    "birth_datetime": "1990-05-15T14:30:00-03:00",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "city": "São Paulo",
    "country": "Brazil",
    "house_system": "placidus",
    "zodiac_type": "tropical",
    "chart_data": {
        "planets": [...],
        "houses": [...],
        "aspects": [...]
    }
}
```

## API Endpoints (Planejados)

### Authentication
- `POST /api/v1/auth/register` - Registro de usuário
- `POST /api/v1/auth/login` - Login (JWT)
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/google` - OAuth2 Google
- `GET /api/v1/auth/github` - OAuth2 GitHub

### Users
- `GET /api/v1/users/me` - Perfil do usuário atual
- `PUT /api/v1/users/me` - Atualizar perfil
- `DELETE /api/v1/users/me` - Deletar conta

### Birth Charts
- `GET /api/v1/charts` - Listar mapas do usuário
- `POST /api/v1/charts` - Criar novo mapa
- `GET /api/v1/charts/{id}` - Obter mapa específico
- `PUT /api/v1/charts/{id}` - Atualizar mapa
- `DELETE /api/v1/charts/{id}` - Deletar mapa

### Geolocation
- `GET /api/v1/geo/search?q={city}` - Buscar localização
- `GET /api/v1/geo/timezone?lat={lat}&lon={lon}&date={date}` - Obter timezone

### Export
- `POST /api/v1/export/pdf/{chart_id}` - Gerar PDF (async)
- `GET /api/v1/export/pdf/{chart_id}/download` - Download PDF
- `GET /api/v1/export/json/{chart_id}` - Export JSON

## Variáveis de Ambiente

Ver `.env.example` para lista completa. Principais:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/astro_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=...
OPENCAGE_API_KEY=...
```

## Desenvolvimento

### Adicionar Nova Feature

1. Criar models em `app/models/`
2. Criar schemas em `app/schemas/`
3. Criar service em `app/services/`
4. Criar routes em `app/api/v1/`
5. Adicionar testes em `tests/`
6. Criar migration com Alembic

### Debugging

```bash
# Executar com debugger
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload

# Logs
tail -f logs/app.log
```

## Cálculos Astrológicos

Os cálculos são realizados pelo módulo `app/astro/` usando PySwisseph:

- **Posições planetárias**: Precisão < 1 arcsecond
- **Sistemas de casas**: Placidus, Whole Sign, Koch, Regiomontanus
- **Aspectos**: Ptolemaicos (conjunção, sextil, quadratura, trígono, oposição)
- **Dignidades**: Domicílio, exaltação, triplicidade, termo, face
- **Sect**: Determinação de chart diurno/noturno

## Segurança

- Senhas hasheadas com bcrypt (cost factor 12)
- JWT com expiração curta (15 min)
- HTTPS obrigatório em produção
- Rate limiting ativo
- CORS configurado
- SQL Injection prevenido por ORM
- Validação de inputs com Pydantic
- Audit logs para compliance LGPD

## Performance

- Async/await para I/O
- Connection pooling (PostgreSQL)
- Cache com Redis
- Índices otimizados
- Celery para tasks pesadas (PDF)

## Produção

```bash
# Build Docker image
docker build -t astro-api --target production .

# Run container
docker run -d -p 8000:8000 --env-file .env astro-api
```

## Contribuindo

1. Seguir padrões de código (Ruff, mypy)
2. Escrever testes (coverage > 70%)
3. Documentar funções complexas
4. Usar type hints
5. Commits no padrão Conventional Commits

## Licença

[Definir licença]
