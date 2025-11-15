# HTTPS em Desenvolvimento Local

Para testar HTTPS localmente sem domínio real, use certificados autoassinados.

## Opção 1: mkcert (Recomendado)

```bash
# Instalar mkcert
brew install mkcert  # macOS
# ou
choco install mkcert  # Windows
# ou
sudo apt install mkcert  # Linux

# Criar CA local
mkcert -install

# Gerar certificados para localhost
cd nginx/ssl
mkcert localhost 127.0.0.1 ::1

# Renomear arquivos
mv localhost+2.pem localhost.crt
mv localhost+2-key.pem localhost.key
```

## Opção 2: OpenSSL (Autoassinado)

```bash
cd nginx/ssl

# Gerar certificado autoassinado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout localhost.key \
  -out localhost.crt \
  -subj "/CN=localhost"
```

## Configurar docker-compose.yml

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx-local-ssl.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
```

## Nginx Config para Dev Local

Arquivo `nginx/nginx-local-ssl.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/localhost.crt;
    ssl_certificate_key /etc/nginx/ssl/localhost.key;

    location / {
        proxy_pass http://web:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Testar

```bash
# Acessar no browser:
https://localhost

# Aceitar o aviso de certificado autoassinado
```

**Nota**: Certificados autoassinados geram avisos no browser. Use apenas para desenvolvimento!
