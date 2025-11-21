/**
 * Cookie Policy page
 */

import { Link } from 'react-router-dom';

export function CookiesPage() {
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
            Política de Cookies
          </h1>
          <p className="text-muted-foreground mt-2">
            Última atualização: 15 de novembro de 2025
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>1. O que são Cookies?</h2>
          <p>
            <strong>Cookies</strong> são pequenos arquivos de texto armazenados
            no seu navegador quando você visita um site. Eles permitem que o
            site "lembre" de você entre visitas, melhorando sua experiência.
          </p>

          <h2>2. Cookies que Usamos</h2>

          <h3>2.1 Cookies Essenciais (Obrigatórios)</h3>
          <p>
            Estes cookies são <strong>estritamente necessários</strong> e{' '}
            <strong>não podem ser desativados</strong>:
          </p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">Cookie</th>
                  <th className="text-left">Finalidade</th>
                  <th className="text-left">Duração</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>astro_access_token</code>
                  </td>
                  <td>Autenticação JWT</td>
                  <td>15 minutos</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_refresh_token</code>
                  </td>
                  <td>Renovação de autenticação</td>
                  <td>30 dias</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_session</code>
                  </td>
                  <td>Identificação de sessão</td>
                  <td>Sessão</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_csrf_token</code>
                  </td>
                  <td>Proteção CSRF</td>
                  <td>Sessão</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>2.2 Cookies Funcionais (Opcionais)</h3>
          <p>Melhoram sua experiência, mas podem ser desativados:</p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">Cookie</th>
                  <th className="text-left">Finalidade</th>
                  <th className="text-left">Duração</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>astro_lang</code>
                  </td>
                  <td>Preferência de idioma</td>
                  <td>1 ano</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_theme</code>
                  </td>
                  <td>Tema (claro/escuro)</td>
                  <td>1 ano</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_timezone</code>
                  </td>
                  <td>Fuso horário preferido</td>
                  <td>1 ano</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_consent</code>
                  </td>
                  <td>Registro de consentimento</td>
                  <td>1 ano</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>2.3 Cookies Analíticos (Opcionais)</h3>
          <p>
            Usamos para entender como você usa o site (dados{' '}
            <strong>anonimizados</strong>):
          </p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">Cookie</th>
                  <th className="text-left">Provedor</th>
                  <th className="text-left">Finalidade</th>
                  <th className="text-left">Duração</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>_ga</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>Distinguir usuários</td>
                  <td>2 anos</td>
                </tr>
                <tr>
                  <td>
                    <code>_gid</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>Distinguir usuários</td>
                  <td>24 horas</td>
                </tr>
                <tr>
                  <td>
                    <code>_gat</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>Limitar taxa</td>
                  <td>1 minuto</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-md border border-blue-200 dark:border-blue-800">
            <p className="text-sm">
              <strong>Anonimização</strong>: Ativamos o recurso{' '}
              <code>anonymizeIp</code> do Google Analytics, que remove os
              últimos octetos do seu IP.
            </p>
            <p className="text-sm mt-2">
              <strong>Opt-out</strong>:{' '}
              <a
                href="https://tools.google.com/dlpage/gaoptout"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google Analytics Opt-out Browser Add-on
              </a>
            </p>
          </div>

          <h3>2.4 Cookies de Marketing</h3>
          <p>
            Atualmente, <strong>não usamos</strong> cookies de publicidade,
            remarketing ou rastreamento de terceiros (Facebook Pixel, Google
            Ads, etc.).
          </p>

          <h2>3. Cookies de Terceiros</h2>

          <h3>3.1 OAuth2 (Login Social)</h3>
          <p>
            Ao fazer login via <strong>Google</strong>, <strong>GitHub</strong>{' '}
            ou <strong>Facebook</strong>, esses serviços podem definir seus
            próprios cookies:
          </p>
          <ul>
            <li>
              <a
                href="https://policies.google.com/privacy"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google Privacy Policy
              </a>
            </li>
            <li>
              <a
                href="https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub Privacy Statement
              </a>
            </li>
            <li>
              <a
                href="https://www.facebook.com/privacy/explanation"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Facebook Data Policy
              </a>
            </li>
          </ul>

          <h2>4. Como Gerenciar Cookies</h2>

          <h3>4.1 No Real Astrology</h3>
          <ol>
            <li>
              Acesse <strong>Configurações → Privacidade → Gerenciar Cookies</strong>
            </li>
            <li>Ative/desative cookies opcionais (funcionais, analíticos)</li>
            <li>Cookies essenciais não podem ser desativados</li>
          </ol>

          <h3>4.2 No Navegador</h3>
          <ul>
            <li>
              <strong>Chrome</strong>: Configurações → Privacidade e segurança
              → Cookies
            </li>
            <li>
              <strong>Firefox</strong>: Configurações → Privacidade e segurança
              → Cookies
            </li>
            <li>
              <strong>Safari</strong>: Preferências → Privacidade → Gerenciar
              dados
            </li>
            <li>
              <strong>Edge</strong>: Configurações → Privacidade → Cookies
            </li>
          </ul>

          <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-md border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm">
              <strong>⚠️ Aviso</strong>: Desativar cookies essenciais impedirá o
              login e uso do serviço.
            </p>
          </div>

          <h3>4.3 Do Not Track (DNT)</h3>
          <p>
            Respeitamos o sinal <strong>Do Not Track</strong> do navegador:
          </p>
          <ul>
            <li>
              Se DNT estiver ativado, desabilitamos cookies analíticos
              automaticamente
            </li>
            <li>
              Cookies essenciais continuam funcionando (necessários para
              autenticação)
            </li>
          </ul>

          <h2>5. LGPD/GDPR</h2>
          <p>
            Conforme <strong>Art. 7º, I da LGPD</strong> e{' '}
            <strong>Art. 4º, 11 do GDPR</strong>:
          </p>
          <ul>
            <li>
              Solicitamos consentimento via <strong>banner de cookies</strong>{' '}
              na primeira visita
            </li>
            <li>
              Você pode <strong>revogar consentimento</strong> a qualquer
              momento
            </li>
            <li>
              Cookies essenciais <strong>não requerem consentimento</strong>{' '}
              (interesse legítimo)
            </li>
          </ul>

          <h2>6. Outras Tecnologias</h2>

          <h3>Local Storage e Session Storage</h3>
          <p>Além de cookies, usamos:</p>
          <ul>
            <li>
              <strong>Local Storage</strong>: Preferências da UI (tema, tamanho
              de fonte)
            </li>
            <li>
              <strong>Session Storage</strong>: Tokens temporários (OAuth)
            </li>
          </ul>
          <p className="text-sm">
            <strong>Não contém dados sensíveis</strong>. Você pode limpar em:
            Navegador → Ferramentas do desenvolvedor → Application → Storage.
          </p>

          <h2>7. Contato</h2>
          <p>
            Dúvidas sobre cookies?
            <br />
            <strong>Email</strong>: privacy@astro-app.com
            <br />
            <strong>DPO</strong>: dpo@astro-app.com
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>Documento completo</strong>: Consulte{' '}
              <a
                href="/docs/COOKIE_POLICY.md"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                COOKIE_POLICY.md
              </a>{' '}
              para versão integral.
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/terms" className="hover:text-primary">
            Termos de Uso
          </Link>
          {' • '}
          <Link to="/privacy" className="hover:text-primary">
            Política de Privacidade
          </Link>
        </div>
      </div>
    </div>
  );
}
