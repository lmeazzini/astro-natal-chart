# Contributing to Astro Natal Chart

Obrigado por contribuir com o Astro App! Este guia explica nosso workflow Git, padrões de código e processo de contribuição.

## 📋 Tabela de Conteúdos

- [Git Workflow (GitFlow)](#git-workflow-gitflow)
- [Tipos de Branches](#tipos-de-branches)
- [Como Contribuir](#como-contribuir)
- [Padrões de Código](#padrões-de-código)
- [Commits](#commits)
- [Pull Requests](#pull-requests)
- [Code Review](#code-review)

---

## 🌳 Git Workflow (GitFlow)

Usamos uma estratégia simplificada de GitFlow com **duas branches principais**:

### Branches Principais

#### 🔴 `main` (Production)
- **Código estável em produção**
- Apenas código testado e aprovado
- Protected branch (requer PR + review)
- Deploy automático para produção
- Versionamento com tags (v1.0.0, v1.1.0, etc.)
- **NUNCA commitar diretamente**

#### 🟡 `dev` (Development)
- **Branch de desenvolvimento ativo**
- Default branch para novos PRs
- Código testado mas pode ter bugs
- Protected branch (requer status checks)
- Deploy automático para staging/preview
- Base para feature branches

### Fluxo Visual

```
main (production)     ──────●────────●────────●─────→
                             ↑        ↑        ↑
                             │        │        │
dev (staging)         ──●────┴───●────┴───●────┴──●──→
                        ↑        ↑       ↑        ↑
                        │        │       │        │
feature/X            ───┴───●────┘       │        │
fix/Y                         ───────────┴───●────┘
```

**Legenda:**
- ● = Merge/Release
- ↑ = Pull Request

---

## 🏷️ Tipos de Branches

### Work Branches (criar a partir de `dev`)

| Prefixo | Descrição | Exemplo |
|---------|-----------|---------|
| `feature/` | Nova funcionalidade | `feature/blog-posts` |
| `fix/` | Correção de bug | `fix/chart-calculation` |
| `chore/` | Manutenção, dependências | `chore/update-deps` |
| `docs/` | Documentação | `docs/api-guide` |
| `refactor/` | Refatoração de código | `refactor/auth-service` |
| `test/` | Adicionar/melhorar testes | `test/chart-service` |
| `hotfix/` | Correção urgente em produção | `hotfix/security-patch` |

### Regras de Nomenclatura

- Use kebab-case: `feature/user-dashboard`
- Seja descritivo: ✅ `fix/login-error` ❌ `fix/bug`
- Use inglês ou português consistente

---

## 🚀 Como Contribuir

### 1. Setup Inicial

```bash
# Clone o repositório
git clone https://github.com/lmeazzini/astro-natal-chart.git
cd astro-natal-chart

# Instalar dependências
make install

# Configurar ambiente
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

# Rodar projeto
make dev
```

### 2. Criar Feature Branch

```bash
# Atualizar dev
git checkout dev
git pull origin dev

# Criar nova branch
git checkout -b feature/my-feature

# Ou para fix
git checkout -b fix/my-bugfix
```

### 3. Desenvolver e Testar

```bash
# Fazer alterações
# ...

# Rodar testes
make test

# Rodar linting
make lint

# Rodar type checking
cd apps/api && uv run mypy app/
cd apps/web && npm run type-check
```

### 4. Commit e Push

```bash
# Add arquivos
git add .

# Commit (ver padrões abaixo)
git commit -m "feat: adicionar funcionalidade X"

# Push
git push origin feature/my-feature
```

### 5. Abrir Pull Request

```bash
# Via GitHub CLI
gh pr create --base dev --title "feat: adicionar funcionalidade X"

# Ou via GitHub Web UI
# https://github.com/lmeazzini/astro-natal-chart/compare/dev...feature/my-feature
```

### 6. Aguardar Review

- CI/CD rodará automaticamente
- Aguarde aprovação de um reviewer
- Faça ajustes se solicitados
- Merge será feito pelo mantenedor

---

## 📝 Padrões de Código

### Backend (Python)

- **Style Guide**: PEP 8
- **Linter**: Ruff
- **Type Checker**: Mypy
- **Formatter**: Ruff
- **Docstrings**: Google style

```python
async def create_chart(
    db: AsyncSession,
    user: User,
    chart_data: ChartCreate,
) -> BirthChart:
    """
    Create a new birth chart for the user.

    Args:
        db: Database session
        user: Authenticated user
        chart_data: Chart creation data

    Returns:
        Created birth chart

    Raises:
        ValueError: If chart data is invalid
    """
    # Implementation
```

**Rodar checks:**
```bash
cd apps/api
uv run ruff check .
uv run mypy app/
uv run pytest
```

### Frontend (TypeScript/React)

- **Style Guide**: Airbnb (com adaptações)
- **Linter**: ESLint
- **Formatter**: Prettier
- **Type Checker**: TypeScript

```typescript
interface ChartProps {
  chartId: string;
  onUpdate?: (chart: Chart) => void;
}

export function ChartDetail({ chartId, onUpdate }: ChartProps): JSX.Element {
  // Implementation
}
```

**Rodar checks:**
```bash
cd apps/web
npm run lint
npm run type-check
npm run test
```

---

## 💬 Commits

### Conventional Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para mensagens padronizadas:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

| Type | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat: adicionar sistema de comentários` |
| `fix` | Correção de bug | `fix: corrigir cálculo de casas` |
| `docs` | Documentação | `docs: atualizar README` |
| `style` | Formatação, sem mudança de código | `style: formatar com prettier` |
| `refactor` | Refatoração sem mudar comportamento | `refactor: extrair lógica de autenticação` |
| `test` | Adicionar/corrigir testes | `test: adicionar testes de autenticação` |
| `chore` | Manutenção, build, dependências | `chore: atualizar dependências` |
| `perf` | Melhoria de performance | `perf: otimizar query de mapas` |
| `ci` | CI/CD changes | `ci: adicionar cache do npm` |
| `build` | Build system, external deps | `build: atualizar configuração Vite` |
| `revert` | Reverter commit anterior | `revert: feat: adicionar feature X` |

#### Scope (Opcional)

- `auth` - Autenticação
- `charts` - Mapas natais
- `blog` - Blog
- `admin` - Portal admin
- `api` - Backend API
- `web` - Frontend

#### Exemplos

```bash
# Feature simples
git commit -m "feat: adicionar botão de compartilhamento"

# Feature com scope
git commit -m "feat(blog): implementar sistema de tags"

# Fix
git commit -m "fix(charts): corrigir cálculo de aspectos"

# Breaking change
git commit -m "feat(api)!: alterar formato de resposta de charts

BREAKING CHANGE: O campo 'data' foi renomeado para 'chart_data'"
```

---

## 🔀 Pull Requests

### Template de PR

Ao abrir um PR, inclua:

```markdown
## 📋 Descrição

Breve descrição das mudanças.

## 🎯 Issue Relacionada

Closes #123

## ✅ Checklist

- [ ] Testes passando (`make test`)
- [ ] Linting OK (`make lint`)
- [ ] Type checking OK (mypy, tsc)
- [ ] Documentação atualizada (se aplicável)
- [ ] Screenshots (para mudanças visuais)

## 📸 Screenshots (se aplicável)

Antes | Depois
:---: | :---:
![before](url) | ![after](url)
```

### Merging para `dev`

- **Squash and merge** (recomendado) - Combina commits em 1
- **Merge commit** - Preserva histórico completo
- **Rebase and merge** - Linear history

### Release para `main`

Apenas maintainers podem fazer merge de `dev` → `main`:

```bash
# 1. Atualizar dev
git checkout dev
git pull origin dev

# 2. Criar PR dev → main
gh pr create --base main --head dev --title "chore: release v1.2.0"

# 3. Aguardar CI passar
# 4. Merge (squash)
# 5. Criar tag
git checkout main
git pull origin main
git tag v1.2.0
git push origin v1.2.0
```

---

## 👀 Code Review

### Como Reviewer

- Seja construtivo e educado
- Explique o "porquê", não só o "o quê"
- Aprove se tudo OK: ✅ Approve
- Solicite mudanças se necessário: 🔄 Request Changes
- Comente sem bloquear: 💬 Comment

### Checklist de Review

- [ ] Código está legível e bem estruturado
- [ ] Testes cobrem casos importantes
- [ ] Sem hardcoded secrets ou dados sensíveis
- [ ] Sem breaking changes não documentados
- [ ] Performance adequada
- [ ] Segurança OK (SQL injection, XSS, etc.)

---

## 🐛 Reportar Bugs

Abra uma issue com:

- Título descritivo
- Steps to reproduce
- Comportamento esperado vs atual
- Screenshots/logs se possível
- Ambiente (OS, browser, versão)

**Template:**
```markdown
**Descrição do bug:**
Ao clicar em "Criar mapa natal", nada acontece.

**Steps to reproduce:**
1. Fazer login
2. Ir para /charts/new
3. Clicar em "Criar mapa natal"

**Comportamento esperado:**
Deveria abrir formulário de criação.

**Comportamento atual:**
Nada acontece.

**Ambiente:**
- OS: Windows 11
- Browser: Chrome 120
- Versão: dev branch
```

---

## 🆘 Dúvidas

- **Slack/Discord**: [Link se houver]
- **Issues**: Para dúvidas técnicas
- **Email**: contact@astro-app.com

---

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT ou outra).

**Obrigado por contribuir! 🚀**
