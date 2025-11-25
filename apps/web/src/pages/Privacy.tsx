/**
 * Privacy Policy page - Internationalized
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft } from 'lucide-react';

export function PrivacyPage() {
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
          <h1 className="text-4xl font-bold text-foreground">{t('privacy.title')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('legal.lastUpdated', { date: '15/11/2025' })}
          </p>
        </div>

        {/* Content */}
        <div className="prose prose-slate dark:prose-invert max-w-none bg-card border border-border rounded-lg p-8">
          <h2>{t('privacy.intro.title')}</h2>
          <p>{t('privacy.intro.content')}</p>

          <h2>{t('privacy.controller.title')}</h2>
          <p>
            <strong>{t('privacy.controller.dataController')}</strong>: Real Astrology
            <br />
            <strong>{t('privacy.controller.dpo')}</strong>: dpo@astro-app.com
            <br />
            <strong>{t('privacy.controller.responseTime')}</strong>:{' '}
            {t('privacy.controller.responseTimeValue')}
          </p>

          <h2>{t('privacy.dataCollected.title')}</h2>

          <h3>{t('privacy.dataCollected.personalTitle')}</h3>
          <ul>
            <li>
              <strong>{t('privacy.dataCollected.fullName')}</strong>:{' '}
              {t('privacy.dataCollected.fullNamePurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.email')}</strong>:{' '}
              {t('privacy.dataCollected.emailPurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.password')}</strong>:{' '}
              {t('privacy.dataCollected.passwordPurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.birthDate')}</strong>:{' '}
              {t('privacy.dataCollected.birthDatePurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.birthTime')}</strong>:{' '}
              {t('privacy.dataCollected.birthTimePurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.birthPlace')}</strong>:{' '}
              {t('privacy.dataCollected.birthPlacePurpose')}
            </li>
          </ul>

          <h3>{t('privacy.dataCollected.autoTitle')}</h3>
          <ul>
            <li>
              <strong>{t('privacy.dataCollected.ip')}</strong>:{' '}
              {t('privacy.dataCollected.ipPurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.userAgent')}</strong>:{' '}
              {t('privacy.dataCollected.userAgentPurpose')}
            </li>
            <li>
              <strong>{t('privacy.dataCollected.cookies')}</strong>:{' '}
              {t('privacy.dataCollected.cookiesPurpose')} (
              <Link to="/cookies" className="text-primary hover:underline">
                {t('cookies.title')}
              </Link>
              )
            </li>
            <li>
              <strong>{t('privacy.dataCollected.logs')}</strong>:{' '}
              {t('privacy.dataCollected.logsPurpose')}
            </li>
          </ul>

          <h3>{t('privacy.dataCollected.thirdPartyTitle')}</h3>
          <p>{t('privacy.dataCollected.oauthInfo')}</p>
          <ul>
            <li>{t('privacy.dataCollected.oauthCollect')}</li>
            <li>{t('privacy.dataCollected.oauthLegal')}</li>
            <li>
              <strong>{t('privacy.dataCollected.oauthNoPassword')}</strong>
            </li>
          </ul>

          <h2>{t('privacy.dataUse.title')}</h2>
          <ul>
            <li>
              <strong>{t('privacy.dataUse.provide')}</strong>: {t('privacy.dataUse.provideDesc')}
            </li>
            <li>
              <strong>{t('privacy.dataUse.auth')}</strong>: {t('privacy.dataUse.authDesc')}
            </li>
            <li>
              <strong>{t('privacy.dataUse.communication')}</strong>:{' '}
              {t('privacy.dataUse.communicationDesc')}
            </li>
            <li>
              <strong>{t('privacy.dataUse.improvements')}</strong>:{' '}
              {t('privacy.dataUse.improvementsDesc')}
            </li>
            <li>
              <strong>{t('privacy.dataUse.legal')}</strong>: {t('privacy.dataUse.legalDesc')}
            </li>
          </ul>

          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-md border border-blue-200 dark:border-blue-800">
            <p className="text-sm">
              <strong>{t('privacy.dataUse.sensitiveNote')}</strong>
            </p>
          </div>

          <h2>{t('privacy.sharing.title')}</h2>
          <p>
            <strong>{t('privacy.sharing.noSell')}</strong>
          </p>
          <ul>
            <li>
              <strong>{t('privacy.sharing.cloud')}</strong>
            </li>
            <li>
              <strong>{t('privacy.sharing.emailService')}</strong>
            </li>
            <li>
              <strong>{t('privacy.sharing.geocoding')}</strong>
            </li>
            <li>
              <strong>{t('privacy.sharing.authorities')}</strong>
            </li>
          </ul>

          <h2>{t('privacy.security.title')}</h2>
          <ul>
            <li>
              <strong>{t('privacy.security.tls')}</strong>
            </li>
            <li>
              <strong>{t('privacy.security.passwords')}</strong>
            </li>
            <li>
              <strong>{t('privacy.security.jwt')}</strong>
            </li>
            <li>
              <strong>{t('privacy.security.rateLimit')}</strong>
            </li>
          </ul>

          <h2>{t('privacy.retention.title')}</h2>
          <ul>
            <li>
              <strong>{t('privacy.retention.active')}</strong>
            </li>
            <li>
              <strong>{t('privacy.retention.inactive')}</strong>
            </li>
            <li>
              <strong>{t('privacy.retention.softDelete')}</strong>
            </li>
            <li>
              <strong>{t('privacy.retention.hardDelete')}</strong>
            </li>
            <li>
              <strong>{t('privacy.retention.audit')}</strong>
            </li>
          </ul>

          <h2>{t('privacy.rights.title')}</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ {t('privacy.rights.access')}</h4>
              <p className="text-sm">
                {t('privacy.rights.accessDesc')}
                <br />
                <strong>{t('privacy.rights.accessHow')}</strong>
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ {t('privacy.rights.rectification')}</h4>
              <p className="text-sm">
                {t('privacy.rights.rectificationDesc')}
                <br />
                <strong>{t('privacy.rights.rectificationHow')}</strong>
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ {t('privacy.rights.portability')}</h4>
              <p className="text-sm">
                {t('privacy.rights.portabilityDesc')}
                <br />
                <strong>{t('privacy.rights.portabilityHow')}</strong>
              </p>
            </div>

            <div className="p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">✓ {t('privacy.rights.erasure')}</h4>
              <p className="text-sm">
                {t('privacy.rights.erasureDesc')}
                <br />
                <strong>{t('privacy.rights.erasureHow')}</strong>
              </p>
            </div>
          </div>

          <h2>{t('privacy.cookiesSection.title')}</h2>
          <p>{t('privacy.cookiesSection.content')}</p>
          <p>
            <Link to="/cookies" className="text-primary hover:underline">
              {t('privacy.cookiesSection.seePolicy')}
            </Link>
          </p>

          <h2>{t('privacy.minors.title')}</h2>
          <p>{t('privacy.minors.content')}</p>

          <h2>{t('privacy.changes.title')}</h2>
          <p>{t('privacy.changes.content')}</p>

          <h2>{t('privacy.contactSection.title')}</h2>
          <p>
            <strong>{t('privacy.contactSection.email')}</strong>: privacy@astro-app.com
            <br />
            <strong>{t('privacy.contactSection.dpo')}</strong>: dpo@astro-app.com
          </p>
          <p>
            <strong>{t('privacy.contactSection.complaints')}</strong>:
            <br />
            {t('privacy.contactSection.brazil')}:{' '}
            <a
              href="https://www.gov.br/anpd"
              className="text-primary hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              ANPD
            </a>
            <br />
            {t('privacy.contactSection.eu')}:{' '}
            <a
              href="https://edpb.europa.eu/about-edpb/board/members_pt"
              className="text-primary hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {t('privacy.contactSection.localAuthority')}
            </a>
          </p>

          <div className="mt-8 p-4 bg-muted rounded-md">
            <p className="text-sm">
              <strong>{t('legal.fullDocument')}</strong>:{' '}
              {t('legal.seeFullVersion', { file: 'PRIVACY_POLICY.md' })}
            </p>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <Link to="/terms" className="hover:text-primary">
            {t('terms.title')}
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
