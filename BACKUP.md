# Database Backup System

Sistema de backup automático do banco de dados PostgreSQL com retenção de 30 dias, armazenamento offsite e procedimentos documentados de restore.

## Visão Geral

O sistema de backup do Astro garante a proteção dos dados críticos através de:

- **Backups automáticos diários** com compressão máxima
- **Retenção de 30 dias** para backups locais
- **Armazenamento offsite opcional** via AWS S3 ou similar
- **Verificação automática de integridade** dos backups
- **Testes periódicos de restore** para garantir recuperabilidade
- **Monitoramento e alertas** via healthchecks.io ou similar

## Dados Protegidos

Os seguintes dados críticos são salvos nos backups:

- Contas de usuário (credenciais, emails, perfis)
- Mapas natais (dados pessoais sensíveis - LGPD/GDPR)
- Conexões OAuth (Google, GitHub, Facebook)
- Audit logs (compliance LGPD)
- Configurações do sistema

## Scripts Disponíveis

### 1. `scripts/backup-db.sh`

Cria backup completo do banco de dados.

**Características:**
- Compressão máxima (nível 9) usando formato custom do PostgreSQL
- Upload automático para S3 (se configurado)
- Limpeza automática de backups antigos (retenção de 30 dias)
- Verificação de integridade após criação
- Logging detalhado
- Healthcheck ping para monitoramento

**Uso:**
```bash
# Backup manual
./scripts/backup-db.sh

# Verificar logs
tail -f /var/log/astro-backup.log

# Com variáveis customizadas
BACKUP_DIR=/custom/path ./scripts/backup-db.sh
```

**Agendamento via Cron:**
```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 3:00 AM
0 3 * * * /path/to/astro/scripts/backup-db.sh >> /var/log/astro-backup.log 2>&1
```

### 2. `scripts/restore-db.sh`

Restaura banco de dados a partir de um backup.

**Características:**
- Parada automática da aplicação
- Confirmação obrigatória (segurança contra execução acidental)
- Verificação de integridade do backup
- Download de backup do S3 (opcional)
- Validação pós-restore
- Reinício automático da aplicação

**Uso:**
```bash
# Listar backups disponíveis
./scripts/restore-db.sh --list-backups

# Restore de backup local
./scripts/restore-db.sh /var/backups/astro-db/astro_backup_20250116_030000.sql.gz

# Restore sem parar serviços (use com cuidado!)
./scripts/restore-db.sh backup.sql.gz --no-stop

# Download e restore do último backup no S3
./scripts/restore-db.sh --download-s3

# Restore sem confirmação (PERIGOSO - use apenas em scripts automatizados)
./scripts/restore-db.sh backup.sql.gz --no-confirm

# Ver ajuda completa
./scripts/restore-db.sh --help
```

### 3. `scripts/test-restore.sh`

Testa a restauração de backups em banco de dados temporário.

**Características:**
- Cria banco temporário para teste
- Restaura backup completo
- Verifica integridade dos dados
- Valida existência de tabelas críticas
- Limpeza automática ao finalizar

**Uso:**
```bash
# Testar último backup
./scripts/test-restore.sh

# Testar backup específico
./scripts/test-restore.sh /var/backups/astro-db/astro_backup_20250116_030000.sql.gz

# Verificar logs
tail -f /var/log/astro-restore-test.log
```

**Agendamento via Cron:**
```bash
# Teste semanal (domingo às 4:00 AM)
0 4 * * 0 /path/to/astro/scripts/test-restore.sh >> /var/log/astro-restore-test.log 2>&1
```

### 4. `scripts/verify-backups.sh`

Verifica saúde e integridade do sistema de backups.

**Características:**
- Verifica idade do último backup
- Valida contagem de backups
- Verifica tamanho dos arquivos
- Testa integridade usando pg_restore
- Monitora espaço em disco
- Verifica backups no S3 (se configurado)
- Envia alertas se problemas detectados

**Uso:**
```bash
# Verificação manual
./scripts/verify-backups.sh

# Verificar logs
tail -f /var/log/astro-backup-verify.log
```

**Agendamento via Cron:**
```bash
# Verificação diária (8:00 AM)
0 8 * * * /path/to/astro/scripts/verify-backups.sh >> /var/log/astro-backup-verify.log 2>&1
```

## Configuração

### Variáveis de Ambiente

Adicione ao arquivo `.env`:

```bash
# Diretório de backups locais
BACKUP_DIR=/var/backups/astro-db

# Retenção de backups (dias)
BACKUP_RETENTION_DAYS=30

# AWS S3 para backups offsite (opcional)
BACKUP_S3_BUCKET=astro-backups-production
BACKUP_S3_PREFIX=backups

# Monitoramento (healthchecks.io)
BACKUP_HEALTHCHECK_URL=https://hc-ping.com/your-uuid-here
BACKUP_HEALTHCHECK_FAIL_URL=https://hc-ping.com/your-uuid-here/fail

# Parâmetros de verificação
MAX_BACKUP_AGE_HOURS=26
MIN_BACKUP_SIZE=102400
MIN_BACKUP_COUNT=7
```

### Configuração do AWS S3 (Opcional)

Para habilitar backups offsite no S3:

1. **Instalar AWS CLI:**
```bash
pip install awscli
```

2. **Configurar credenciais:**
```bash
aws configure
# Inserir: Access Key ID, Secret Access Key, Region
```

3. **Criar bucket:**
```bash
aws s3 mb s3://astro-backups-production
```

4. **Testar upload:**
```bash
aws s3 ls s3://astro-backups-production
```

### Docker Compose (Alternativa)

Para usar o container de backup automático, edite `docker-compose.yml` e descomente:

```yaml
db-backup:
  image: prodrigestivill/postgres-backup-local:16
  container_name: astro-db-backup
  restart: unless-stopped
  environment:
    POSTGRES_HOST: db
    POSTGRES_DB: astro_dev
    POSTGRES_USER: astro
    POSTGRES_PASSWORD: dev_password
    POSTGRES_EXTRA_OPTS: -Z9 --format=custom
    BACKUP_DIR: /backups
    SCHEDULE: "0 3 * * *"  # 3 AM diariamente
    BACKUP_KEEP_DAYS: 30
    BACKUP_KEEP_WEEKS: 4
    BACKUP_KEEP_MONTHS: 6
  volumes:
    - backup_data:/backups
  depends_on:
    db:
      condition: service_healthy
  networks:
    - astro-network
```

Depois reinicie os containers:
```bash
docker compose up -d db-backup
```

## Monitoramento

### Healthchecks.io (Recomendado)

Healthchecks.io é um serviço gratuito que monitora jobs cron e envia alertas se falharem.

**Setup:**

1. Criar conta em https://healthchecks.io
2. Criar novo check "Database Backup"
3. Copiar URL de ping
4. Adicionar ao `.env`:
```bash
BACKUP_HEALTHCHECK_URL=https://hc-ping.com/your-uuid-here
```

**O script enviará:**
- ✅ Ping de sucesso quando backup completa
- ❌ Nenhum ping se backup falhar (alerta automático após período configurado)

### Logs

Todos os scripts geram logs detalhados:

```bash
# Logs de backup
tail -f /var/log/astro-backup.log

# Logs de restore
tail -f /var/log/astro-restore.log

# Logs de teste
tail -f /var/log/astro-restore-test.log

# Logs de verificação
tail -f /var/log/astro-backup-verify.log
```

### Alertas por Email

Para configurar alertas por email quando verificação falhar, adicione ao script `verify-backups.sh`:

```bash
send_email_alert() {
    echo "$1" | mail -s "ALERTA: Backup Falhou" admin@astro.com
}
```

## Procedimentos de Emergência

### Cenário 1: Perda Total do Servidor

**Passos:**

1. **Provisionar novo servidor**
2. **Instalar dependências:**
```bash
apt-get update
apt-get install postgresql-client-16 awscli
```

3. **Clonar repositório:**
```bash
git clone <repo-url>
cd astro
```

4. **Download do último backup do S3:**
```bash
aws s3 ls s3://astro-backups-production/backups/ --recursive | \
    grep "astro_backup_.*\.sql\.gz$" | sort -r | head -1

aws s3 cp s3://astro-backups-production/backups/path/to/latest/backup.sql.gz .
```

5. **Subir infraestrutura:**
```bash
docker compose up -d db redis
```

6. **Restaurar banco:**
```bash
./scripts/restore-db.sh backup.sql.gz --no-confirm
```

7. **Verificar dados:**
```bash
docker compose exec db psql -U astro -d astro_dev -c "SELECT COUNT(*) FROM users;"
```

8. **Subir aplicação:**
```bash
docker compose up -d
```

### Cenário 2: Corrupção de Dados (últimas 6 horas)

**Passos:**

1. **Listar backups recentes:**
```bash
./scripts/restore-db.sh --list-backups
```

2. **Identificar backup antes da corrupção**
3. **Restaurar:**
```bash
./scripts/restore-db.sh /var/backups/astro-db/astro_backup_YYYYMMDD_HHMMSS.sql.gz
```

### Cenário 3: Exclusão Acidental de Dados

**Passos:**

1. **PARAR aplicação imediatamente:**
```bash
docker compose stop api celery_worker
```

2. **Restaurar de backup recente**
3. **Comparar dados manualmente se necessário**
4. **Reiniciar aplicação**

## Regra 3-2-1 de Backup

Seguimos a regra 3-2-1:
- **3 cópias** dos dados (original + 2 backups)
- **2 mídias diferentes** (local + S3)
- **1 cópia offsite** (S3 em região diferente)

## Conformidade LGPD

⚠️ **Importante:** Backups contêm dados pessoais sensíveis.

**Requisitos:**
- Backups devem ser criptografados (GPG ou S3 encryption)
- Acesso restrito (IAM policies, permissões de arquivo)
- Quando usuário solicitar exclusão de dados (Art. 18, VI), remover também de backups antigos ou garantir que backups sejam anonimizados

**Recomendações:**
- Criptografar backups locais com GPG
- Usar AWS S3 Server-Side Encryption (SSE)
- Documentar política de retenção
- Revisar backups antigos periodicamente

## Testes

### Teste Mensal de Restore Completo

**Procedimento:**

1. **Agendar janela de manutenção** (ex: último domingo do mês, 2:00 AM)

2. **Executar teste:**
```bash
./scripts/test-restore.sh
```

3. **Documentar resultado:**
```bash
echo "Teste de restore $(date +'%Y-%m-%d'): SUCESSO" >> /var/log/backup-tests.log
```

4. **Se falhar:**
   - Investigar logs
   - Corrigir problemas
   - Reexecutar teste
   - Documentar ações corretivas

### Checklist Trimestral

- [ ] Executar restore completo em ambiente de staging
- [ ] Verificar todos os dados foram restaurados corretamente
- [ ] Testar acesso à aplicação com dados restaurados
- [ ] Validar contagem de registros em tabelas principais
- [ ] Revisar logs de backup dos últimos 90 dias
- [ ] Verificar espaço em disco
- [ ] Confirmar backups S3 estão acessíveis
- [ ] Atualizar documentação de procedimentos se necessário

## Troubleshooting

### Backup falha com "disk full"

**Solução:**
```bash
# Verificar espaço
df -h /var/backups

# Limpar backups antigos manualmente
find /var/backups/astro-db -name "*.sql.gz" -mtime +30 -delete

# Ou mover para S3 e remover local
for f in /var/backups/astro-db/*.sql.gz; do
    aws s3 cp "$f" s3://astro-backups-production/archive/
    rm "$f"
done
```

### Restore falha com "authentication failed"

**Solução:**
```bash
# Verificar credenciais no .env
cat apps/api/.env | grep DB_

# Testar conexão manual
psql -h localhost -U astro_user -d postgres
```

### Backup muito lento

**Possíveis causas:**
- Banco de dados muito grande
- CPU limitada durante compressão
- I/O lento

**Soluções:**
```bash
# Usar compressão menor (mais rápido, arquivo maior)
pg_dump --compress=6 ...

# Executar backup em horário de baixo uso
# Verificar I/O: iostat -x 1
```

### S3 upload falha

**Solução:**
```bash
# Verificar credenciais AWS
aws s3 ls

# Verificar permissões do bucket
aws s3api get-bucket-policy --bucket astro-backups-production

# Testar upload manual
aws s3 cp test.txt s3://astro-backups-production/test.txt
```

## Custos Estimados

### Armazenamento Local
- Backup diário: ~100-200 MB comprimido
- 30 backups: ~3-6 GB
- **Custo:** Incluído no servidor

### AWS S3 Standard
- ~$0.023/GB/mês
- 30 backups × 150 MB = 4.5 GB
- **Custo mensal:** ~$0.10/mês

### Backblaze B2 (mais barato)
- ~$0.005/GB/mês
- **Custo mensal:** ~$0.02/mês

### Healthchecks.io
- Até 20 checks: **GRÁTIS**
- Plano pago: $5/mês (checks ilimitados)

## Referências

- [PostgreSQL Backup & Restore](https://www.postgresql.org/docs/current/backup.html)
- [pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
- [pg_restore Documentation](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [AWS S3 CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [3-2-1 Backup Rule](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/)
- [Healthchecks.io Documentation](https://healthchecks.io/docs/)

## Contato

Para dúvidas ou problemas com backups:
- Documentação: Este arquivo (BACKUP.md)
- Logs: `/var/log/astro-backup*.log`
- Issue Tracker: GitHub Issues
