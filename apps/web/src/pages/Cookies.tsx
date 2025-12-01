/**
 * Cookie Policy page - Internationalized
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft } from 'lucide-react';

export function CookiesPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link to="/" className="text-primary hover:underline inline-flex items-center gap-2 mb-4">
            <ArrowLeft className="h-5 w-5" />
            {t('legal.back')}
          </Link>
          <h1 className="text-4xl font-bold text-foreground">{t('cookies.title')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('legal.lastUpdated', { date: '15/11/2025' })}
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>{t('cookies.what.title')}</h2>
          <p>{t('cookies.what.content')}</p>

          <h2>{t('cookies.types.title')}</h2>

          <h3>{t('cookies.types.essentialTitle')}</h3>
          <p>{t('cookies.types.essentialDesc')}</p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">{t('cookies.table.cookie')}</th>
                  <th className="text-left">{t('cookies.table.purpose')}</th>
                  <th className="text-left">{t('cookies.table.duration')}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>astro_access_token</code>
                  </td>
                  <td>{t('cookies.table.jwtAuth')}</td>
                  <td>15 min</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_refresh_token</code>
                  </td>
                  <td>{t('cookies.table.refreshAuth')}</td>
                  <td>30 days</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_session</code>
                  </td>
                  <td>{t('cookies.table.sessionId')}</td>
                  <td>{t('cookies.table.session')}</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_csrf_token</code>
                  </td>
                  <td>{t('cookies.table.csrfProtection')}</td>
                  <td>{t('cookies.table.session')}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>{t('cookies.types.functionalTitle')}</h3>
          <p>{t('cookies.types.functionalDesc')}</p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">{t('cookies.table.cookie')}</th>
                  <th className="text-left">{t('cookies.table.purpose')}</th>
                  <th className="text-left">{t('cookies.table.duration')}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>astro_lang</code>
                  </td>
                  <td>{t('cookies.table.language')}</td>
                  <td>1 year</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_theme</code>
                  </td>
                  <td>{t('cookies.table.theme')}</td>
                  <td>1 year</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_timezone</code>
                  </td>
                  <td>{t('cookies.table.timezone')}</td>
                  <td>1 year</td>
                </tr>
                <tr>
                  <td>
                    <code>astro_consent</code>
                  </td>
                  <td>{t('cookies.table.consentRecord')}</td>
                  <td>1 year</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>{t('cookies.types.analyticalTitle')}</h3>
          <p>{t('cookies.types.analyticalDesc')}</p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left">{t('cookies.table.cookie')}</th>
                  <th className="text-left">{t('cookies.table.provider')}</th>
                  <th className="text-left">{t('cookies.table.purpose')}</th>
                  <th className="text-left">{t('cookies.table.duration')}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <code>_ga</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>{t('cookies.table.distinguishUsers')}</td>
                  <td>2 years</td>
                </tr>
                <tr>
                  <td>
                    <code>_gid</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>{t('cookies.table.distinguishUsers')}</td>
                  <td>24 hours</td>
                </tr>
                <tr>
                  <td>
                    <code>_gat</code>
                  </td>
                  <td>Google Analytics</td>
                  <td>{t('cookies.table.rateLimit')}</td>
                  <td>1 min</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-md border border-blue-200 dark:border-blue-800">
            <p className="text-sm">
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

          <h3>{t('cookies.types.marketingTitle')}</h3>
          <p>{t('cookies.types.marketingDesc')}</p>

          <h2>{t('cookies.thirdParty.title')}</h2>

          <h3>{t('cookies.thirdParty.oauthTitle')}</h3>
          <p>{t('cookies.thirdParty.oauthDesc')}</p>
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

          <h2>{t('cookies.manage.title')}</h2>

          <h3>{t('cookies.manage.inAppTitle')}</h3>
          <ol>
            <li>{t('cookies.manage.step1')}</li>
            <li>{t('cookies.manage.step2')}</li>
            <li>{t('cookies.manage.step3')}</li>
          </ol>

          <h3>{t('cookies.manage.browserTitle')}</h3>
          <ul>
            <li>
              <strong>{t('cookies.manage.chrome')}</strong>
            </li>
            <li>
              <strong>{t('cookies.manage.firefox')}</strong>
            </li>
            <li>
              <strong>{t('cookies.manage.safari')}</strong>
            </li>
            <li>
              <strong>{t('cookies.manage.edge')}</strong>
            </li>
          </ul>

          <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-md border border-yellow-200 dark:border-yellow-800">
            <p className="text-sm">{t('cookies.manage.warning')}</p>
          </div>

          <h3>{t('cookies.manage.dntTitle')}</h3>
          <p>{t('cookies.manage.dntDesc')}</p>
          <ul>
            <li>{t('cookies.manage.dntOn')}</li>
            <li>{t('cookies.manage.dntEssential')}</li>
          </ul>

          <h2>{t('cookies.lgpdGdpr.title')}</h2>
          <p>{t('cookies.lgpdGdpr.content')}</p>
          <ul>
            <li>{t('cookies.lgpdGdpr.consent')}</li>
            <li>{t('cookies.lgpdGdpr.revoke')}</li>
            <li>{t('cookies.lgpdGdpr.essential')}</li>
          </ul>

          <h2>{t('cookies.otherTech.title')}</h2>

          <h3>{t('cookies.otherTech.storageTitle')}</h3>
          <p>{t('cookies.otherTech.storageDesc')}</p>
          <ul>
            <li>
              <strong>{t('cookies.otherTech.localStorage')}</strong>
            </li>
            <li>
              <strong>{t('cookies.otherTech.sessionStorage')}</strong>
            </li>
          </ul>
          <p className="text-sm">{t('cookies.otherTech.noSensitive')}</p>

          <h2>{t('cookies.contact.title')}</h2>
          <p>
            {t('cookies.contact.questions')}
            <br />
            <strong>{t('cookies.contact.email')}</strong>: privacy@astro-app.com
            <br />
            <strong>{t('cookies.contact.dpo')}</strong>: dpo@astro-app.com
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>{t('legal.fullDocument')}</strong>:{' '}
              {t('legal.seeFullVersion', { file: 'COOKIE_POLICY.md' })}
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/terms" className="hover:text-primary">
            {t('terms.title')}
          </Link>
          {' • '}
          <Link to="/privacy" className="hover:text-primary">
            {t('privacy.title')}
          </Link>
        </div>
      </div>
    </div>
  );
}
