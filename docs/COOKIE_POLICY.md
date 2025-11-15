# Política de Cookies - Astro App

**Última atualização**: 15 de novembro de 2025

---

## 1. O que são Cookies?

**Cookies** são pequenos arquivos de texto armazenados no seu navegador quando você visita um site. Eles permitem que o site "lembre" de você entre visitas, melhorando sua experiência.

---

## 2. Cookies que Usamos

### 2.1 Cookies Essenciais (Obrigatórios)

Estes cookies são **estritamente necessários** para o funcionamento do site e **não podem ser desativados**:

| Cookie               | Finalidade                            | Duração    |
|----------------------|---------------------------------------|------------|
| `astro_access_token` | Autenticação JWT (acesso)             | 15 minutos |
| `astro_refresh_token`| Autenticação JWT (renovação)          | 30 dias    |
| `astro_session`      | Identificação de sessão               | Sessão     |
| `astro_csrf_token`   | Proteção contra CSRF                  | Sessão     |

**Base legal**: Interesse legítimo (segurança e funcionalidade)

### 2.2 Cookies Funcionais (Opcionais)

Estes cookies melhoram sua experiência, mas **podem ser desativados**:

| Cookie               | Finalidade                            | Duração    |
|----------------------|---------------------------------------|------------|
| `astro_lang`         | Salvar preferência de idioma          | 1 ano      |
| `astro_theme`        | Lembrar tema (claro/escuro)           | 1 ano      |
| `astro_timezone`     | Fuso horário preferido                | 1 ano      |
| `astro_consent`      | Registro de consentimento de cookies  | 1 ano      |

**Base legal**: Consentimento (você aceita no banner de cookies)

### 2.3 Cookies Analíticos (Opcionais)

Usamos para entender como você usa o site (dados **anonimizados**):

| Cookie               | Provedor       | Finalidade                       | Duração    |
|----------------------|----------------|----------------------------------|------------|
| `_ga`                | Google Analytics| Distinguir usuários únicos       | 2 anos     |
| `_gid`               | Google Analytics| Distinguir usuários únicos       | 24 horas   |
| `_gat`               | Google Analytics| Limitar taxa de requisições      | 1 minuto   |

**Anonimização**: Ativamos o recurso `anonymizeIp` do Google Analytics, que remove os últimos octetos do seu IP.

**Base legal**: Consentimento (você aceita no banner de cookies)

**Opt-out**: Você pode desativar em **Configurações → Privacidade → Cookies Analíticos** ou instalar o [Google Analytics Opt-out Browser Add-on](https://tools.google.com/dlpage/gaoptout).

### 2.4 Cookies de Marketing (Não Usados)

Atualmente, **não usamos cookies de publicidade, remarketing ou rastreamento de terceiros** (Facebook Pixel, Google Ads, etc.).

Se implementarmos no futuro, solicitaremos **consentimento explícito** antes.

---

## 3. Cookies de Terceiros

### 3.1 OAuth2 (Login Social)

Ao fazer login via **Google**, **GitHub** ou **Facebook**, esses serviços podem definir seus próprios cookies:
- **Google**: Consulte [Política de Privacidade do Google](https://policies.google.com/privacy)
- **GitHub**: Consulte [Política de Privacidade do GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)
- **Facebook**: Consulte [Política de Dados do Facebook](https://www.facebook.com/privacy/explanation)

**Não temos controle sobre esses cookies**. Eles são gerenciados diretamente pelos provedores.

### 3.2 Geocoding (OpenCage)

Ao buscar localizações, usamos a API OpenCage. Eles **não definem cookies**, mas podem registrar seu IP:
- [Política de Privacidade OpenCage](https://opencagedata.com/privacy)

---

## 4. Como Gerenciar Cookies

### 4.1 No Astro App

1. **Configurações → Privacidade → Gerenciar Cookies**
2. Ative/desative cookies opcionais (funcionais, analíticos)
3. Cookies essenciais não podem ser desativados

### 4.2 No Navegador

Você pode bloquear ou apagar cookies diretamente no navegador:

- **Chrome**: Configurações → Privacidade e segurança → Cookies
- **Firefox**: Configurações → Privacidade e segurança → Cookies e dados de sites
- **Safari**: Preferências → Privacidade → Gerenciar dados de websites
- **Edge**: Configurações → Privacidade, pesquisa e serviços → Cookies

⚠️ **Aviso**: Desativar cookies essenciais impedirá o login e uso do serviço.

### 4.3 Do Not Track (DNT)

Respeitamos o sinal **Do Not Track** do navegador:
- Se DNT estiver ativado, **desabilitamos cookies analíticos automaticamente**
- Cookies essenciais continuam funcionando (necessários para autenticação)

---

## 5. Cookies e LGPD/GDPR

### 5.1 Consentimento

Conforme **Art. 7º, I da LGPD** e **Art. 4º, 11 do GDPR**:
- Solicitamos consentimento via **banner de cookies** na primeira visita
- Você pode **revogar consentimento** a qualquer momento
- Cookies essenciais **não requerem consentimento** (interesse legítimo)

### 5.2 Transparência

Esta política descreve **todos os cookies** que usamos, incluindo:
- Nome
- Finalidade
- Duração
- Provedor (próprio ou terceiro)

### 5.3 Direitos

Você tem o direito de:
- **Recusar cookies opcionais** (no banner ou configurações)
- **Apagar cookies existentes** (navegador ou configurações)
- **Solicitar lista completa de cookies** (dpo@astro-app.com)

---

## 6. Outras Tecnologias de Rastreamento

Além de cookies, podemos usar:

### 6.1 Local Storage

Armazenamento local no navegador (não enviado ao servidor):
- `astro_user_preferences`: Preferências da UI (tema, tamanho de fonte)
- `astro_draft_charts`: Mapas natais em rascunho (não salvos)

**Não contém dados sensíveis**. Você pode limpar em: Navegador → Ferramentas do desenvolvedor → Application → Local Storage.

### 6.2 Session Storage

Similar ao Local Storage, mas **apagado ao fechar a aba**:
- `astro_temp_token`: Token temporário para fluxos OAuth

### 6.3 Fingerprinting

**Não usamos** técnicas de fingerprinting (identificação por características do dispositivo).

### 6.4 Web Beacons / Pixels

**Não usamos** pixels de rastreamento em emails ou páginas.

---

## 7. Retenção de Dados de Cookies

| Tipo                  | Retenção                                      |
|-----------------------|-----------------------------------------------|
| Cookies de sessão     | Apagados ao fechar o navegador                |
| Cookies persistentes  | Conforme tabela acima (até 2 anos máximo)     |
| Local/Session Storage | Apagados ao limpar cache ou sessão do navegador |

**Limpeza automática**: Cookies expirados são removidos automaticamente pelo navegador.

---

## 8. Atualizações nesta Política

Esta política pode ser atualizada para refletir mudanças em:
- Cookies que usamos
- Legislação de privacidade
- Funcionalidades do site

**Notificação**: Mudanças significativas serão comunicadas via banner ou email.

---

## 9. Contato

Dúvidas sobre cookies?

**Email**: privacy@astro-app.com
**DPO**: dpo@astro-app.com

---

## 10. Glossário

- **Cookie de sessão**: Expiram quando você fecha o navegador
- **Cookie persistente**: Permanecem por um período definido
- **Cookie de primeira parte**: Definidos pelo Astro App
- **Cookie de terceiros**: Definidos por outros domínios (ex: Google)
- **HTTPOnly**: Cookie não acessível via JavaScript (mais seguro)
- **Secure**: Cookie só enviado via HTTPS
- **SameSite**: Proteção contra CSRF

---

**Consentimento**

Ao aceitar o banner de cookies, você consente com cookies **funcionais e analíticos**.

Cookies **essenciais** são usados independentemente de consentimento (necessários para funcionalidade básica).

Você pode gerenciar ou revogar consentimento a qualquer momento em: **Configurações → Privacidade → Gerenciar Cookies**.

---

© 2025 Astro App. Todos os direitos reservados.
