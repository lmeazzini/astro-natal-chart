# Política de Privacidade - Astro App

**Última atualização**: 15 de novembro de 2025

**Vigência**: Esta política entra em vigor imediatamente e permanece válida por tempo indeterminado.

---

## 1. Introdução

O **Astro App** ("nós", "nosso") respeita sua privacidade e está comprometido em proteger seus dados pessoais. Esta Política de Privacidade explica:
- Quais dados coletamos
- Como usamos e armazenamos seus dados
- Seus direitos sob a **LGPD** (Lei 13.709/2018) e o **GDPR** (Regulamento UE 2016/679)
- Como você pode exercer seus direitos

**Base legal**: Processamos seus dados com base em:
- **Consentimento explícito** (Art. 7º, I, LGPD)
- **Execução de contrato** (fornecimento do serviço)
- **Obrigação legal** (logs de segurança, auditoria fiscal)
- **Interesse legítimo** (segurança, prevenção de fraudes)

---

## 2. Controlador e Encarregado de Dados (DPO)

### 2.1 Controlador de Dados
**Razão Social**: [Astro App Ltda.] *(a definir)*
**CNPJ**: [00.000.000/0000-00] *(a definir)*
**Endereço**: [Rua Exemplo, 123 - São Paulo/SP - CEP 00000-000] *(a definir)*
**Email**: privacy@astro-app.com

### 2.2 Encarregado de Proteção de Dados (DPO)
**Nome**: [Nome do DPO] *(a definir)*
**Email**: dpo@astro-app.com
**Prazo de resposta**: até 15 dias úteis

---

## 3. Dados Coletados

### 3.1 Dados Pessoais Fornecidos por Você

| Dado                  | Finalidade                                    | Base Legal                  |
|-----------------------|-----------------------------------------------|-----------------------------|
| Nome completo         | Identificação, personalização                 | Consentimento, Contrato     |
| Email                 | Autenticação, comunicação, recuperação senha  | Consentimento, Contrato     |
| Senha (hash bcrypt)   | Autenticação segura                           | Contrato                    |
| Data de nascimento    | Cálculo de mapa natal                         | Consentimento explícito     |
| Hora de nascimento    | Cálculo de mapa natal                         | Consentimento explícito     |
| Local de nascimento   | Cálculo de coordenadas geográficas            | Consentimento explícito     |
| Fuso horário          | Conversão de horários                         | Consentimento               |
| Idioma/Locale         | Personalização da interface                   | Consentimento               |

**Observação**: Dados de nascimento (data, hora, local) são **dados sensíveis** sob o ponto de vista astrológico e podem revelar informações sobre sua personalidade. Processamos esses dados **exclusivamente com seu consentimento explícito**.

### 3.2 Dados Coletados Automaticamente

| Dado                       | Finalidade                             | Base Legal            |
|----------------------------|----------------------------------------|-----------------------|
| Endereço IP                | Segurança, rate limiting, geolocalização | Interesse legítimo    |
| User-Agent (navegador/SO)  | Compatibilidade técnica                | Interesse legítimo    |
| Cookies (ver Política de Cookies) | Sessão, preferências, analytics | Consentimento/Legítimo |
| Logs de acesso             | Auditoria, segurança, LGPD             | Obrigação legal       |
| Data/hora de login         | Segurança, monitoramento de sessões    | Interesse legítimo    |

### 3.3 Dados de Terceiros (OAuth2)

Se você se cadastrar via **Google**, **GitHub** ou **Facebook**:
- Coletamos: ID da conta, email, nome, foto de perfil (opcional)
- Base legal: Consentimento (você autoriza via OAuth)
- Armazenamento: Vinculamos sua conta OAuth à sua conta Astro App

**Não armazenamos** suas senhas de serviços de terceiros.

### 3.4 Dados que NÃO Coletamos

- Número de CPF ou documentos de identidade
- Dados bancários ou de cartão de crédito (se implementarmos pagamentos, será via processador terceirizado)
- Dados de saúde não relacionados à astrologia
- Dados de menores de 18 anos (nosso serviço é para maiores de idade)

---

## 4. Como Usamos Seus Dados

### 4.1 Finalidades

1. **Fornecer o Serviço**
   - Calcular mapas natais com precisão astronômica (Swiss Ephemeris)
   - Gerar interpretações astrológicas
   - Armazenar e exibir seus mapas salvos

2. **Autenticação e Segurança**
   - Validar login e manter sessões
   - Prevenir fraudes e acessos não autorizados
   - Aplicar rate limiting (limitar requisições abusivas)

3. **Comunicação**
   - Enviar emails transacionais (confirmação de cadastro, reset de senha)
   - Notificações importantes sobre sua conta
   - **Não enviamos emails de marketing sem consentimento explícito**

4. **Melhorias do Serviço**
   - Análises agregadas e anonimizadas (quantos mapas criados, recursos mais usados)
   - Debugging e correção de erros
   - Desenvolvimento de novas funcionalidades

5. **Conformidade Legal**
   - Cumprir obrigações fiscais e regulatórias
   - Responder a requisições judiciais legítimas
   - Manter logs de auditoria LGPD (quem acessou dados sensíveis)

### 4.2 Compartilhamento de Dados

**Não vendemos, alugamos ou compartilhamos seus dados pessoais com terceiros**, exceto:

| Com Quem                  | Finalidade                                  | Base Legal       |
|---------------------------|---------------------------------------------|------------------|
| Provedores de nuvem (AWS, DigitalOcean) | Hospedagem de servidores                   | Contrato         |
| Serviços de email (SendGrid, Mailgun)   | Envio de emails transacionais              | Contrato         |
| Serviços de geocoding (OpenCage)         | Conversão de cidades em coordenadas        | Contrato         |
| Autoridades legais        | Cumprimento de ordens judiciais            | Obrigação legal  |

**Todos os fornecedores são contratualmente obrigados a proteger seus dados conforme LGPD/GDPR.**

---

## 5. Armazenamento e Segurança

### 5.1 Onde Armazenamos

- **Servidores**: Brasil ou União Europeia (data centers certificados ISO 27001)
- **Backup**: Cópias de segurança diárias, retidas por 30 dias
- **Transferência internacional**: Se necessário, garantimos medidas de segurança adequadas (cláusulas contratuais padrão)

### 5.2 Medidas de Segurança

- **Criptografia em trânsito**: HTTPS/TLS 1.3
- **Criptografia em repouso**: Dados sensíveis criptografados no banco de dados
- **Senhas**: Hash bcrypt com cost factor 12
- **Autenticação**: JWT com tokens de curta duração (15 min acesso, 30 dias refresh)
- **Rate limiting**: Proteção contra ataques de força bruta
- **Logs de auditoria**: Rastreamento de acessos a dados sensíveis

### 5.3 Retenção de Dados

| Dado                    | Período de Retenção                          |
|-------------------------|----------------------------------------------|
| Conta ativa             | Enquanto você mantiver a conta              |
| Conta inativa           | 24 meses após último login (notificação prévia) |
| Conta excluída (soft delete) | 30 dias (permite recuperação)         |
| Conta excluída (hard delete) | Dados removidos permanentemente após 30 dias |
| Logs de auditoria       | 5 anos (obrigação legal Art. 16, LGPD)      |
| Backup                  | 30 dias (para recuperação de desastres)     |

**Exclusão automática**: Após 30 dias de soft delete, seus dados são **permanentemente apagados** e **não podem ser recuperados**.

---

## 6. Seus Direitos (LGPD e GDPR)

### 6.1 Direito de Acesso
- Visualizar todos os dados pessoais que armazenamos sobre você
- **Como exercer**: Configurações → Privacidade → Ver Meus Dados

### 6.2 Direito de Retificação
- Corrigir dados incorretos ou desatualizados
- **Como exercer**: Configurações → Perfil → Editar Informações

### 6.3 Direito de Portabilidade
- Baixar todos os seus dados em formato **JSON estruturado**
- Inclui: perfil, mapas natais, histórico de ações
- **Como exercer**: Configurações → Privacidade → Exportar Meus Dados

### 6.4 Direito ao Esquecimento (Exclusão)
- Solicitar **remoção completa** de todos os seus dados
- **Soft delete**: 30 dias de carência (pode cancelar)
- **Hard delete**: Após 30 dias, dados são **irrecuperavelmente apagados**
- **Como exercer**: Configurações → Privacidade → Excluir Minha Conta

### 6.5 Direito de Objeção
- Opor-se ao processamento de dados específicos (ex: marketing)
- **Como exercer**: Configurações → Privacidade → Preferências de Comunicação

### 6.6 Direito de Revogar Consentimento
- Retirar consentimento para processar dados sensíveis
- **Consequência**: Não poderemos gerar novos mapas natais
- **Como exercer**: Contato com DPO (dpo@astro-app.com)

### 6.7 Direito de Revisão de Decisões Automatizadas
- Não tomamos decisões automatizadas que produzam efeitos legais significativos
- Interpretações astrológicas são para **entretenimento**, não decisões críticas

### 6.8 Prazo de Resposta
- **15 dias úteis** para solicitações simples (acesso, retificação)
- **30 dias úteis** para solicitações complexas (portabilidade completa)

---

## 7. Cookies

Consulte nossa **Política de Cookies** separada para detalhes completos.

**Resumo**:
- **Essenciais**: Autenticação (JWT), sessão (obrigatórios)
- **Funcionais**: Idioma, tema (opcionais)
- **Analíticos**: Google Analytics (opcionais, anonimizados)

Você pode gerenciar cookies em: **Configurações → Privacidade → Gerenciar Cookies**

---

## 8. Menores de Idade

Nosso serviço **NÃO é destinado a menores de 18 anos**. Se descobrirmos que coletamos dados de menores sem consentimento parental, **apagaremos imediatamente**.

Se você é pai/responsável e acredita que seu filho forneceu dados: **dpo@astro-app.com**

---

## 9. Mudanças nesta Política

Podemos atualizar esta Política periodicamente. Mudanças significativas serão notificadas por:
- **Email** (para alterações que requerem novo consentimento)
- **Notificação no painel**
- **Banner de aviso**

**Data da última modificação**: sempre exibida no topo.

**Histórico de versões**: disponível em [link para changelog] *(a implementar)*

---

## 10. Transferências Internacionais

Se transferirmos dados para fora do Brasil ou UE:
- Garantiremos **nível adequado de proteção** (Art. 33, LGPD)
- Utilizaremos **Cláusulas Contratuais Padrão (SCC)** aprovadas
- Notificaremos você sobre o país de destino

---

## 11. Incidentes de Segurança

Em caso de vazamento de dados:
1. **Notificação à ANPD** (Autoridade Nacional de Proteção de Dados): até 24h após detecção
2. **Notificação aos usuários afetados**: até 72h, por email
3. **Medidas corretivas**: implementação imediata

**Reporte vulnerabilidades**: security@astro-app.com (Responsible Disclosure)

---

## 12. Contato e Reclamações

### 12.1 Dúvidas sobre esta Política
**Email**: privacy@astro-app.com
**DPO**: dpo@astro-app.com

### 12.2 Reclamações
Se não ficar satisfeito com nossa resposta, você pode registrar reclamação:

**Brasil**:
**ANPD** (Autoridade Nacional de Proteção de Dados)
https://www.gov.br/anpd

**União Europeia**:
Autoridade de proteção de dados do seu país
https://edpb.europa.eu/about-edpb/board/members_pt

---

## 13. Glossário

- **Titular**: Você, pessoa natural a quem se referem os dados pessoais
- **Controlador**: Astro App (decide sobre o tratamento de dados)
- **Operador**: Terceiros que processam dados em nosso nome (ex: AWS)
- **Tratamento**: Qualquer operação com dados (coleta, armazenamento, compartilhamento, exclusão)
- **Anonimização**: Dados que não podem mais identificar uma pessoa
- **Pseudonimização**: Dados dissociados da identidade real (ex: User ID genérico)

---

## 14. Compromisso

O Astro App se compromete a:
- ✓ Ser **transparente** sobre o uso de dados
- ✓ Coletar **apenas o necessário** (minimização)
- ✓ Proteger dados com **segurança técnica e organizacional**
- ✓ Respeitar **todos os seus direitos** LGPD/GDPR
- ✓ **Nunca vender ou alugar** seus dados

---

**Consentimento**

Ao criar uma conta, você consente com esta Política de Privacidade.

**Você pode revogar este consentimento a qualquer momento**, mas isso pode impactar a funcionalidade do serviço.

---

© 2025 Astro App. Todos os direitos reservados.
