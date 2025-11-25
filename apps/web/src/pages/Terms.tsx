/**
 * Terms of Service page - Internationalized
 */

import { Link } from 'react-router-dom';
import { useTranslation, Trans } from 'react-i18next';
import { ArrowLeft } from 'lucide-react';

export function TermsPage() {
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
          <h1 className="text-4xl font-bold text-foreground">{t('terms.title')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('legal.lastUpdated', { date: '15/11/2025' })}
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>{t('terms.acceptance.title')}</h2>
          <p>{t('terms.acceptance.content')}</p>

          <h2>{t('terms.description.title')}</h2>
          <p>{t('terms.description.intro')}</p>
          <ul>
            <li>{t('terms.description.item1')}</li>
            <li>{t('terms.description.item2')}</li>
            <li>{t('terms.description.item3')}</li>
            <li>{t('terms.description.item4')}</li>
          </ul>

          <h2>{t('terms.account.title')}</h2>
          <h3>{t('terms.account.requirementsTitle')}</h3>
          <ul>
            <li>{t('terms.account.req1')}</li>
            <li>{t('terms.account.req2')}</li>
            <li>{t('terms.account.req3')}</li>
          </ul>

          <h3>{t('terms.account.responsibilitiesTitle')}</h3>
          <ul>
            <li>{t('terms.account.resp1')}</li>
            <li>{t('terms.account.resp2')}</li>
            <li>{t('terms.account.resp3')}</li>
          </ul>

          <h2>{t('terms.acceptableUse.title')}</h2>
          <h3>{t('terms.acceptableUse.canTitle')}</h3>
          <ul>
            <li>{t('terms.acceptableUse.can1')}</li>
            <li>{t('terms.acceptableUse.can2')}</li>
            <li>{t('terms.acceptableUse.can3')}</li>
          </ul>

          <h3>{t('terms.acceptableUse.cannotTitle')}</h3>
          <ul>
            <li>{t('terms.acceptableUse.cannot1')}</li>
            <li>{t('terms.acceptableUse.cannot2')}</li>
            <li>{t('terms.acceptableUse.cannot3')}</li>
            <li>{t('terms.acceptableUse.cannot4')}</li>
            <li>{t('terms.acceptableUse.cannot5')}</li>
          </ul>

          <h2>{t('terms.intellectualProperty.title')}</h2>
          <p>{t('terms.intellectualProperty.content')}</p>

          <h2>{t('terms.privacy.title')}</h2>
          <p>{t('terms.privacy.content')}</p>
          <p>
            <Trans
              i18nKey="terms.privacy.seePolicy"
              components={{
                link: <Link to="/privacy" className="text-primary hover:underline" />,
              }}
            />
          </p>

          <h3>{t('terms.privacy.rightsTitle')}</h3>
          <ul>
            <li>
              <strong>{t('terms.privacy.access')}</strong>
            </li>
            <li>
              <strong>{t('terms.privacy.rectification')}</strong>
            </li>
            <li>
              <strong>{t('terms.privacy.deletion')}</strong>
            </li>
            <li>
              <strong>{t('terms.privacy.portability')}</strong>
            </li>
          </ul>

          <h2>{t('terms.limitations.title')}</h2>
          <h3>{t('terms.limitations.disclaimerTitle')}</h3>
          <p>{t('terms.limitations.content')}</p>

          <h2>{t('terms.modifications.title')}</h2>
          <p>{t('terms.modifications.content')}</p>

          <h2>{t('terms.law.title')}</h2>
          <p>{t('terms.law.content')}</p>

          <h2>{t('terms.contact.title')}</h2>
          <p>
            <strong>{t('terms.contact.email')}</strong>: legal@astro-app.com
            <br />
            <strong>{t('terms.contact.dpo')}</strong>: dpo@astro-app.com
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>{t('legal.fullDocument')}</strong>:{' '}
              {t('legal.seeFullVersion', { file: 'TERMS_OF_SERVICE.md' })}
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/privacy" className="hover:text-primary">
            {t('privacy.title')}
          </Link>
          {' • '}
          <Link to="/cookies" className="hover:text-primary">
            {t('cookies.title')}
          </Link>
        </div>
      </div>
    </div>
  );
}
