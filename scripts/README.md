# Scripts

Scripts utilitários para gerenciamento e manutenção do Astro.

Todos os scripts estão centralizados nesta pasta única para facilitar a manutenção.

## Database Backup Scripts

Scripts para backup e restore do banco de dados PostgreSQL e Qdrant. **Veja documentação completa em [BACKUP.md](../BACKUP.md)**.

### backup-db.sh

Cria backup completo do PostgreSQL e Qdrant com compressão.

```bash
# Backup padrão (com timestamp)
./scripts/backup-db.sh

# Backup com nome específico (ex: estado inicial)
BACKUP_NAME=initial ./scripts/backup-db.sh
```

**Funcionalidades:**
- Backup automático com compressão máxima (PostgreSQL + Qdrant)
- Upload para S3 (opcional)
- Limpeza automática de backups antigos
- Verificação de integridade
- Monitoramento via healthcheck

### restore-db.sh

Restaura banco de dados a partir de um backup.

```bash
# Ver backups disponíveis
./scripts/restore-db.sh --list-backups

# Restaurar de backup
./scripts/restore-db.sh /path/to/backup.sql.gz

# Ver ajuda
./scripts/restore-db.sh --help
```

**Funcionalidades:**
- Parada automática da aplicação
- Confirmação de segurança
- Verificação de integridade
- Download de S3
- Reinício da aplicação

### test-restore.sh

Testa restore em banco temporário (sem afetar produção).

```bash
./scripts/test-restore.sh
```

**Funcionalidades:**
- Teste em banco temporário
- Validação de dados
- Limpeza automática

### verify-backups.sh

Verifica saúde do sistema de backups.

```bash
./scripts/verify-backups.sh
```

**Funcionalidades:**
- Verifica idade do último backup
- Valida integridade
- Monitora espaço em disco
- Envia alertas se problemas

## Setup Scripts

### check-setup.sh

Verifica se o ambiente está configurado corretamente.

```bash
./scripts/check-setup.sh
```

### reboot.sh

Reinicia todos os serviços Docker.

```bash
./scripts/reboot.sh
```

## SSL Scripts

### setup-ssl.sh

Configura certificados SSL usando Let's Encrypt.

```bash
./scripts/setup-ssl.sh
```

### renew-ssl.sh

Renova certificados SSL.

```bash
./scripts/renew-ssl.sh
```

## Logo Scripts

### generate_logos.sh

Gera logos em diferentes tamanhos.

```bash
./scripts/generate_logos.sh
```

## Python Data Scripts

Scripts Python para popular dados do sistema. Devem ser executados a partir do diretório `apps/api`.

### populate_rag.py

Popula o banco de dados vetorial Qdrant com documentos RAG para interpretações astrológicas.

```bash
cd apps/api && uv run python ../../scripts/populate_rag.py

# Limpar documentos existentes antes de popular
cd apps/api && uv run python ../../scripts/populate_rag.py --clear
```

### populate_public_charts.py

Popula a tabela de mapas públicos com dados de pessoas famosas.

```bash
cd apps/api && uv run python ../../scripts/populate_public_charts.py
```

### generate_missing_interpretations.py

Gera interpretações para mapas que ainda não as possuem.

```bash
cd apps/api && uv run python ../../scripts/generate_missing_interpretations.py

# Limitar quantidade de mapas
cd apps/api && uv run python ../../scripts/generate_missing_interpretations.py --limit 10

# Modo dry-run (apenas mostra o que seria feito)
cd apps/api && uv run python ../../scripts/generate_missing_interpretations.py --dry-run
```

## OAuth/Email Scripts

### get_gmail_refresh_token.py

Obtém refresh token do Gmail para envio de emails OAuth2.

```bash
cd apps/api && uv run python ../../scripts/get_gmail_refresh_token.py
```

### test_oauth_email.py

Testa configuração de email OAuth2.

```bash
cd apps/api && uv run python ../../scripts/test_oauth_email.py
```

## Agendamento (Cron)

Exemplo de configuração de crontab:

```bash
# Editar crontab
crontab -e

# Adicionar jobs
# Backup diário às 3:00 AM
0 3 * * * /path/to/astro/scripts/backup-db.sh >> /var/log/astro-backup.log 2>&1

# Teste de restore semanal (domingo às 4:00 AM)
0 4 * * 0 /path/to/astro/scripts/test-restore.sh >> /var/log/astro-restore-test.log 2>&1

# Verificação diária às 8:00 AM
0 8 * * * /path/to/astro/scripts/verify-backups.sh >> /var/log/astro-backup-verify.log 2>&1
```

## Logs

Todos os scripts geram logs detalhados:

```bash
# Ver logs de backup
tail -f /var/log/astro-backup.log

# Ver logs de restore
tail -f /var/log/astro-restore.log

# Ver logs de testes
tail -f /var/log/astro-restore-test.log

# Ver logs de verificação
tail -f /var/log/astro-backup-verify.log
```

## Variáveis de Ambiente

Configurações principais no `.env`:

```bash
# Backup
BACKUP_DIR=/var/backups/astro-db
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=
BACKUP_HEALTHCHECK_URL=

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=astro_dev
DB_USER=astro
DB_PASSWORD=dev_password
```

## Documentação

- **Backup completo:** [BACKUP.md](../BACKUP.md)
- **Projeto:** [README.md](../README.md)
- **Especificações:** [PROJECT_SPEC.md](../PROJECT_SPEC.md)
