/**
 * Privacy Policy page
 */

import { Link } from 'react-router-dom';

export function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/"
            className="text-primary hover:underline inline-flex items-center gap-2 mb-4"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                clipRule="evenodd"
              />
            </svg>
            Voltar
          </Link>
          <h1 className="text-4xl font-bold text-foreground">
            Política de Privacidade
          </h1>
          <p className="text-muted-foreground mt-2">
            Última atualização: 15 de novembro de 2025
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>1. Introdução</h2>
          <p>
            O <strong>Real Astrology</strong> respeita sua privacidade e está
            comprometido em proteger seus dados pessoais. Esta Política explica
            como coletamos, usamos e protegemos suas informações conforme a{' '}
            <strong>LGPD</strong> (Lei 13.709/2018) e o <strong>GDPR</strong>{' '}
            (Regulamento UE 2016/679).
          </p>

          <h2>2. Controlador e DPO</h2>
          <p>
            <strong>Controlador de Dados</strong>: Real Astrology
            <br />
            <strong>DPO (Encarregado)</strong>: dpo@astro-app.com
            <br />
            <strong>Prazo de resposta</strong>: até 15 dias úteis
          </p>

          <h2>3. Dados Coletados</h2>

          <h3>3.1 Dados Pessoais Fornecidos</h3>
          <ul>
            <li>
              <strong>Nome completo</strong>: Identificação e personalização
            </li>
            <li>
              <strong>Email</strong>: Autenticação e comunicação
            </li>
            <li>
              <strong>Senha (hash bcrypt)</strong>: Autenticação segura
            </li>
            <li>
              <strong>Data de nascimento</strong>: Cálculo de mapa natal
              (consentimento explícito)
            </li>
            <li>
              <strong>Hora de nascimento</strong>: Cálculo de mapa natal
              (consentimento explícito)
            </li>
            <li>
              <strong>Local de nascimento</strong>: Coordenadas geográficas
              (consentimento explícito)
            </li>
          </ul>

          <h3>3.2 Dados Coletados Automaticamente</h3>
          <ul>
            <li>
              <strong>Endereço IP</strong>: Segurança e rate limiting
            </li>
            <li>
              <strong>User-Agent</strong>: Compatibilidade técnica
            </li>
            <li>
              <strong>Cookies</strong>: Sessão e preferências (ver{' '}
              <Link to="/cookies" className="text-primary hover:underline">
                Política de Cookies
              </Link>
              )
            </li>
            <li>
              <strong>Logs de acesso</strong>: Auditoria e segurança
            </li>
          </ul>

          <h3>3.3 Dados de Terceiros (OAuth2)</h3>
          <p>
            Se você se cadastrar via <strong>Google</strong>,{' '}
            <strong>GitHub</strong> ou <strong>Facebook</strong>:
          </p>
          <ul>
            <li>Coletamos: ID da conta, email, nome, foto de perfil</li>
            <li>Base legal: Consentimento (você autoriza via OAuth)</li>
            <li>
              <strong>Não armazenamos</strong> suas senhas de serviços de
              terceiros
            </li>
          </ul>

          <h2>4. Como Usamos Seus Dados</h2>
          <ul>
            <li>
              <strong>Fornecer o Serviço</strong>: Calcular mapas natais,
              armazenar e exibir
            </li>
            <li>
              <strong>Autenticação</strong>: Validar login e manter sessões
            </li>
            <li>
              <strong>Comunicação</strong>: Emails transacionais (confirmação,
              reset de senha)
            </li>
            <li>
              <strong>Melhorias</strong>: Análises agregadas e anonimizadas
            </li>
            <li>
              <strong>Conformidade Legal</strong>: Logs de auditoria LGPD
            </li>
          </ul>

          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-md border border-blue-200 dark:border-blue-800">
            <p className="text-sm">
              <strong>Importante</strong>: Dados de nascimento são{' '}
              <strong>dados sensíveis</strong>. Processamos exclusivamente com
              seu <strong>consentimento explícito</strong>.
            </p>
          </div>

          <h2>5. Compartilhamento de Dados</h2>
          <p>
            <strong>
              Não vendemos, alugamos ou compartilhamos seus dados pessoais
            </strong>
            , exceto:
          </p>
          <ul>
            <li>
              <strong>Provedores de nuvem</strong> (AWS, DigitalOcean):
              Hospedagem
            </li>
            <li>
              <strong>Serviços de email</strong> (SendGrid, Mailgun): Emails
              transacionais
            </li>
            <li>
              <strong>Geocoding</strong> (OpenCage): Conversão de cidades em
              coordenadas
            </li>
            <li>
              <strong>Autoridades legais</strong>: Cumprimento de ordens
              judiciais
            </li>
          </ul>

          <h2>6. Segurança</h2>
          <ul>
            <li>
              <strong>Criptografia em trânsito</strong>: HTTPS/TLS 1.3
            </li>
            <li>
              <strong>Senhas</strong>: Hash bcrypt com cost factor 12
            </li>
            <li>
              <strong>Autenticação</strong>: JWT com tokens de curta duração
            </li>
            <li>
              <strong>Rate limiting</strong>: Proteção contra ataques
            </li>
          </ul>

          <h2>7. Retenção de Dados</h2>
          <ul>
            <li>
              <strong>Conta ativa</strong>: Enquanto você mantiver a conta
            </li>
            <li>
              <strong>Conta inativa</strong>: 24 meses após último login
            </li>
            <li>
              <strong>Conta excluída (soft delete)</strong>: 30 dias (permite
              recuperação)
            </li>
            <li>
              <strong>Hard delete</strong>: Dados removidos permanentemente após
              30 dias
            </li>
            <li>
              <strong>Logs de auditoria</strong>: 5 anos (obrigação legal LGPD)
            </li>
          </ul>

          <h2>8. Seus Direitos (LGPD e GDPR)</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ Direito de Acesso</h4>
              <p className="text-sm">
                Visualizar todos os dados que armazenamos sobre você.
                <br />
                <strong>Como exercer</strong>: Configurações → Privacidade →
                Ver Dados
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ Direito de Retificação</h4>
              <p className="text-sm">
                Corrigir dados incorretos ou desatualizados.
                <br />
                <strong>Como exercer</strong>: Configurações → Perfil → Editar
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ Direito de Portabilidade</h4>
              <p className="text-sm">
                Baixar todos os seus dados em formato JSON.
                <br />
                <strong>Como exercer</strong>: Configurações → Privacidade →
                Exportar Dados
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">
                ✓ Direito ao Esquecimento
              </h4>
              <p className="text-sm">
                Solicitar remoção completa de seus dados.
                <br />
                <strong>Como exercer</strong>: Configurações → Privacidade →
                Excluir Conta
              </p>
            </div>
          </div>

          <h2>9. Cookies</h2>
          <p>
            Usamos cookies essenciais (autenticação), funcionais (tema,
            idioma) e analíticos (Google Analytics anonimizado).
          </p>
          <p>
            Consulte nossa{' '}
            <Link to="/cookies" className="text-primary hover:underline">
              Política de Cookies
            </Link>{' '}
            para detalhes completos.
          </p>

          <h2>10. Menores de Idade</h2>
          <p>
            Nosso serviço <strong>NÃO é destinado a menores de 18 anos</strong>
            . Se descobrirmos dados de menores, apagaremos imediatamente.
          </p>

          <h2>11. Mudanças nesta Política</h2>
          <p>
            Podemos atualizar esta Política periodicamente. Mudanças
            significativas serão notificadas por email ou banner.
          </p>

          <h2>12. Contato e Reclamações</h2>
          <p>
            <strong>Email</strong>: privacy@astro-app.com
            <br />
            <strong>DPO</strong>: dpo@astro-app.com
          </p>
          <p>
            <strong>Reclamações</strong>:
            <br />
            Brasil:{' '}
            <a
              href="https://www.gov.br/anpd"
              className="text-primary hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              ANPD
            </a>
            <br />
            UE:{' '}
            <a
              href="https://edpb.europa.eu/about-edpb/board/members_pt"
              className="text-primary hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Autoridade Local
            </a>
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>Documento completo</strong>: Consulte{' '}
              <a
                href="/docs/PRIVACY_POLICY.md"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                PRIVACY_POLICY.md
              </a>{' '}
              para versão integral (14 seções, 450+ linhas).
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/terms" className="hover:text-primary">
            Termos de Uso
          </Link>
          {' • '}
          <Link to="/cookies" className="hover:text-primary">
            Política de Cookies
          </Link>
        </div>
      </div>
    </div>
  );
}
