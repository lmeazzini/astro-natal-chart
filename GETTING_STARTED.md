# Guia de Início Rápido

Este guia vai te ajudar a configurar e executar o sistema de mapas natais localmente.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker Desktop** (recomendado) - [Download](https://www.docker.com/products/docker-desktop)
  - OU -
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.13+** - [Download](https://www.python.org/)
- **PostgreSQL 16+** - [Download](https://www.postgresql.org/)
- **Redis 7+** - [Download](https://redis.io/)

## Opção 1: Início Rápido com Docker (Recomendado)

### Passo 1: Clone e Configure

```bash
# Clone o repositório (se ainda não fez)
cd /mnt/c/Users/luis_/OneDrive/Documentos/astro

# Copie os arquivos de exemplo de variáveis de ambiente
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

### Passo 2: Inicie os Serviços

```bash
# Inicie todos os serviços com Docker Compose
docker-compose up -d

# Aguarde os serviços iniciarem (30-60 segundos)
# Verifique o status
docker-compose ps
```

### Passo 3: Execute as Migrations

```bash
# Execute as migrations do banco de dados
docker-compose exec api alembic upgrade head
```

### Passo 4: Acesse a Aplicação

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Comandos Úteis

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs apenas da API
docker-compose logs -f api

# Ver logs apenas do frontend
docker-compose logs -f web

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpa banco de dados)
docker-compose down -v

# Reconstruir e reiniciar
docker-compose up -d --build
```

## Opção 2: Desenvolvimento Local (Sem Docker)

### Passo 1: PostgreSQL e Redis

Certifique-se de que PostgreSQL e Redis estão rodando:

```bash
# PostgreSQL (criar banco de dados)
createdb astro_dev

# Redis (deve estar rodando na porta 6379)
redis-server
```

### Passo 2: Backend (FastAPI)

```bash
# Navegue até o diretório da API
cd apps/api

# Crie e ative ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações locais

# Execute migrations
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload
```

API disponível em: http://localhost:8000

### Passo 3: Frontend (React)

Em um novo terminal:

```bash
# Navegue até o diretório web
cd apps/web

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env

# Inicie o servidor de desenvolvimento
npm run dev
```

Frontend disponível em: http://localhost:5173

### Passo 4: Celery Worker (Opcional)

Para processamento assíncrono (geração de PDFs):

```bash
# Em outro terminal
cd apps/api
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info
```

## Usando o Makefile

O projeto inclui um Makefile com comandos úteis:

```bash
# Ver todos os comandos disponíveis
make help

# Comandos principais
make install        # Instalar todas as dependências
make dev            # Iniciar desenvolvimento (Turborepo)
make docker-up      # Iniciar Docker Compose
make docker-down    # Parar Docker Compose
make docker-logs    # Ver logs
make migrate        # Executar migrations
make test           # Executar todos os testes
make lint           # Lint em todo o código
```

## Verificando a Instalação

### 1. Verifique o Backend

```bash
# Teste o endpoint de health
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy","environment":"development"}
```

### 2. Verifique o Frontend

Abra http://localhost:5173 no navegador. Você deve ver a página inicial do Astro.

### 3. Verifique a Documentação da API

Abra http://localhost:8000/docs no navegador para ver a documentação interativa Swagger.

## Próximos Passos

### 1. Criar Primeiro Usuário

Use a interface em http://localhost:5173/register ou via API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "senhaSegura123!",
    "full_name": "Seu Nome"
  }'
```

### 2. Fazer Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "senhaSegura123!"
  }'
```

### 3. Criar Primeiro Mapa Natal

(A implementação dos endpoints será feita nas próximas fases)

## Configurações Opcionais

### OAuth2 (Google, GitHub, Facebook)

Para habilitar login social:

1. Crie aplicações OAuth2 nos respectivos providers
2. Obtenha Client ID e Client Secret
3. Configure em `apps/api/.env`:

```env
GOOGLE_CLIENT_ID=seu-google-client-id
GOOGLE_CLIENT_SECRET=seu-google-client-secret
# ... similar para GitHub e Facebook
```

### API de Geocoding

Para busca de localizações:

1. Crie conta no [OpenCage](https://opencagedata.com/) (free tier: 2500 req/dia)
2. Obtenha API key
3. Configure em `apps/api/.env`:

```env
OPENCAGE_API_KEY=sua-api-key
```

### Swiss Ephemeris (Dados Astrológicos)

Os arquivos de efemérides são necessários para cálculos precisos:

```bash
# Download dos arquivos (dentro do container ou localmente)
mkdir -p /usr/share/ephe
cd /usr/share/ephe
wget https://www.astro.com/ftp/swisseph/ephe/seas_18.se1
# ... outros arquivos conforme necessário
```

Ou configure o caminho em `apps/api/.env`:

```env
EPHEMERIS_PATH=/caminho/para/ephe
```

## Troubleshooting

### Porta já em uso

```bash
# Mudar porta do backend (apps/api/.env)
PORT=8001

# Mudar porta do frontend (apps/web/vite.config.ts)
server: { port: 3000 }
```

### Erro de conexão com PostgreSQL

```bash
# Verifique se PostgreSQL está rodando
docker-compose ps db

# Verifique logs
docker-compose logs db

# Recrie o container
docker-compose down -v
docker-compose up -d db
```

### Erro de permissão (Linux/Mac)

```bash
# Adicione seu usuário ao grupo docker
sudo usermod -aG docker $USER

# Reinicie a sessão
```

### Problemas com node_modules

```bash
# Limpe e reinstale
cd apps/web
rm -rf node_modules package-lock.json
npm install
```

### Problemas com Python packages

```bash
# Recrie o ambiente virtual
cd apps/api
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Desenvolvimento

### Estrutura do Projeto

```
astro/
├── apps/
│   ├── api/          # Backend FastAPI
│   └── web/          # Frontend React
├── packages/         # Pacotes compartilhados
├── docs/             # Documentação
│   └── PROJECT_SPEC.md
├── docker-compose.yml
├── package.json      # Workspace root
├── turbo.json        # Turborepo config
└── Makefile
```

### Fluxo de Trabalho

1. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/nome-da-feature
   ```

2. **Desenvolva** com hot-reload ativo
   - Backend: alterações em Python recarregam automaticamente
   - Frontend: HMR (Hot Module Replacement) ativo

3. **Teste** suas mudanças
   ```bash
   make test
   ```

4. **Commit** seguindo Conventional Commits
   ```bash
   git commit -m "feat: adiciona cálculo de dignidades essenciais"
   ```

5. **Push** e crie Pull Request
   ```bash
   git push origin feature/nome-da-feature
   ```

## Recursos Adicionais

- **Documentação Técnica Completa**: [PROJECT_SPEC.md](./PROJECT_SPEC.md)
- **Backend README**: [apps/api/README.md](./apps/api/README.md)
- **Frontend README**: [apps/web/README.md](./apps/web/README.md)
- **Main README**: [README.md](./README.md)

## Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs -f`
2. Consulte a documentação em [PROJECT_SPEC.md](./PROJECT_SPEC.md)
3. Abra uma issue no repositório

## Próximas Implementações

Conforme o roadmap em PROJECT_SPEC.md:

- ✅ Setup do projeto (CONCLUÍDO)
- 🚧 Sistema de autenticação (Fase 1 - semanas 3-4)
- 📅 Engine astrológico (Fase 1 - semanas 5-7)
- 📅 Interface e visualização (Fase 1 - semanas 8-9)
- 📅 Análise e export (Fase 1 - semana 10)

Bom desenvolvimento! 🚀
