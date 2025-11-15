/**
 * Terms of Service page
 */

import { Link } from 'react-router-dom';

export function TermsPage() {
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
          <h1 className="text-4xl font-bold text-foreground">Termos de Uso</h1>
          <p className="text-muted-foreground mt-2">
            Última atualização: 15 de novembro de 2025
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>1. Aceitação dos Termos</h2>
          <p>
            Ao acessar e usar o Astro App ("Serviço", "Plataforma", "nós"),
            você ("Usuário", "você") concorda em estar vinculado a estes Termos
            de Uso. Se você não concordar com qualquer parte destes termos, não
            use nosso Serviço.
          </p>

          <h2>2. Descrição do Serviço</h2>
          <p>O Astro App é uma plataforma digital que fornece:</p>
          <ul>
            <li>
              Cálculo de mapas natais usando dados astronômicos precisos (Swiss
              Ephemeris)
            </li>
            <li>Visualização gráfica de mapas astrológicos</li>
            <li>
              Interpretações astrológicas baseadas em métodos tradicionais
            </li>
            <li>Armazenamento seguro de dados pessoais de nascimento</li>
          </ul>

          <h2>3. Cadastro e Conta de Usuário</h2>
          <h3>3.1 Requisitos</h3>
          <ul>
            <li>Você deve ter pelo menos 18 anos de idade</li>
            <li>
              Fornecer informações verdadeiras, completas e atualizadas
            </li>
            <li>Manter a confidencialidade de suas credenciais de acesso</li>
          </ul>

          <h3>3.2 Responsabilidades do Usuário</h3>
          <ul>
            <li>
              Você é responsável por todas as atividades em sua conta
            </li>
            <li>
              Notificar-nos imediatamente sobre qualquer uso não autorizado
            </li>
            <li>Não compartilhar suas credenciais com terceiros</li>
          </ul>

          <h2>4. Uso Aceitável</h2>
          <h3>Você PODE:</h3>
          <ul>
            <li>Criar mapas natais para uso pessoal ou profissional</li>
            <li>Compartilhar mapas exportados seguindo nossas diretrizes</li>
            <li>Utilizar os serviços para fins educacionais</li>
          </ul>

          <h3>Você NÃO PODE:</h3>
          <ul>
            <li>Usar o Serviço para fins ilegais ou não autorizados</li>
            <li>Tentar acessar áreas restritas do sistema</li>
            <li>
              Fazer engenharia reversa, descompilar ou modificar nosso software
            </li>
            <li>Coletar dados de outros usuários sem consentimento</li>
            <li>
              Sobrecarregar nossos servidores (scraping, bots, etc.)
            </li>
          </ul>

          <h2>5. Propriedade Intelectual</h2>
          <p>
            O código, design, algoritmos e conteúdo do Astro App são de nossa
            propriedade. Você recebe uma licença limitada, não exclusiva e
            revogável para usar o Serviço.
          </p>

          <h2>6. Privacidade e Proteção de Dados</h2>
          <p>
            Estamos em conformidade com a <strong>LGPD</strong> (Lei Geral de
            Proteção de Dados) e o <strong>GDPR</strong> (General Data
            Protection Regulation).
          </p>
          <p>
            Para mais detalhes, consulte nossa{' '}
            <Link to="/privacy" className="text-primary hover:underline">
              Política de Privacidade
            </Link>
            .
          </p>

          <h3>Seus Direitos LGPD/GDPR:</h3>
          <ul>
            <li>
              <strong>Acesso</strong>: baixar todos os seus dados (exportação
              JSON)
            </li>
            <li>
              <strong>Retificação</strong>: corrigir informações incorretas
            </li>
            <li>
              <strong>Exclusão</strong>: solicitar remoção completa (direito ao
              esquecimento)
            </li>
            <li>
              <strong>Portabilidade</strong>: exportar dados em formato
              estruturado
            </li>
          </ul>

          <h2>7. Limitações e Garantias</h2>
          <h3>Disclaimer Astrológico</h3>
          <p>
            Os mapas natais são gerados para fins{' '}
            <strong>educacionais e de entretenimento</strong>. Não substituem
            aconselhamento médico, psicológico, jurídico ou financeiro.
          </p>

          <h2>8. Modificações nos Termos</h2>
          <p>
            Podemos atualizar estes Termos periodicamente. Notificaremos sobre
            mudanças significativas por email ou notificação no painel.
          </p>

          <h2>9. Lei Aplicável</h2>
          <p>
            Estes Termos são regidos pelas leis do <strong>Brasil</strong>.
            Foro: Comarca de São Paulo/SP.
          </p>

          <h2>10. Contato</h2>
          <p>
            <strong>Email</strong>: legal@astro-app.com
            <br />
            <strong>DPO (LGPD)</strong>: dpo@astro-app.com
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>Documento completo</strong>: Consulte{' '}
              <a
                href="/docs/TERMS_OF_SERVICE.md"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                TERMS_OF_SERVICE.md
              </a>{' '}
              para versão integral.
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/privacy" className="hover:text-primary">
            Política de Privacidade
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
