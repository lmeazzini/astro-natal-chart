/**
 * Methodology Page - Educational content about Traditional Astrology and Swiss Ephemeris
 * Issue #49 - Educational content implementation - Internationalized
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Book, Satellite, Star, Calculator, Check, ArrowLeft, ExternalLink } from 'lucide-react';

export function MethodologyPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label={t('methodology.backToHome')}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">{t('methodology.title')}</h1>
          </Link>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm">
              <Link to="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {t('legal.back')}
              </Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-16 lg:py-24">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12 animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6 font-display">
              {t('methodology.hero.title')}
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              {t('methodology.hero.subtitle')}
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="pb-16 lg:pb-24">
        <div className="max-w-4xl mx-auto px-4 space-y-12">
          {/* Traditional Astrology */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Book className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-3xl font-display">
                    {t('methodology.traditional.title')}
                  </CardTitle>
                  <CardDescription className="text-base mt-1">
                    {t('methodology.traditional.subtitle')}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  <Star className="h-5 w-5 text-primary" />
                  {t('methodology.traditional.whatIs')}
                </h4>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('methodology.traditional.desc1')}
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  {t('methodology.traditional.desc2')}
                </p>
              </div>

              <Separator />

              <div>
                <h4 className="text-xl font-semibold mb-3">
                  {t('methodology.traditional.techniques')}
                </h4>
                <div className="space-y-4">
                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('methodology.traditional.dignities.title')}
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      {t('methodology.traditional.dignities.desc')}
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li>
                        <strong>{t('methodology.traditional.dignities.domicile')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.exaltation')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.triplicity')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.term')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.face')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.peregrine')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.detriment')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.dignities.fall')}</strong>
                      </li>
                    </ul>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('methodology.traditional.sect.title')}
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      {t('methodology.traditional.sect.desc')}
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li>
                        <strong>{t('methodology.traditional.sect.diurnal')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.sect.nocturnal')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.sect.neutral')}</strong>
                      </li>
                    </ul>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6 mt-2">
                      {t('methodology.traditional.sect.note')}
                    </p>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('methodology.traditional.temperament.title')}
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      {t('methodology.traditional.temperament.desc')}
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1 ml-10 mt-2">
                      <li>
                        <strong>{t('methodology.traditional.temperament.choleric')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.temperament.melancholic')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.temperament.sanguine')}</strong>
                      </li>
                      <li>
                        <strong>{t('methodology.traditional.temperament.phlegmatic')}</strong>
                      </li>
                    </ul>
                  </div>

                  <div>
                    <h5 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('methodology.traditional.lord.title')}
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed ml-6">
                      {t('methodology.traditional.lord.desc')}
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="bg-muted/50 p-4 rounded-lg">
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.traditional.comparison.title')}
                </h5>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    <strong>{t('methodology.traditional.comparison.traditional')}</strong>
                  </p>
                  <p>
                    <strong>{t('methodology.traditional.comparison.modern')}</strong>
                  </p>
                  <p className="pt-2 italic">
                    <strong>{t('methodology.traditional.comparison.approach')}</strong>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Swiss Ephemeris */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Satellite className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-3xl font-display">
                    {t('methodology.swissEph.title')}
                  </CardTitle>
                  <CardDescription className="text-base mt-1">
                    {t('methodology.swissEph.subtitle')}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-xl font-semibold mb-3 flex items-center gap-2">
                  <Calculator className="h-5 w-5 text-primary" />
                  {t('methodology.swissEph.whatIs')}
                </h4>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('methodology.swissEph.desc1')}
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  {t('methodology.swissEph.desc2')}
                </p>
              </div>

              <Separator />

              <div>
                <h4 className="text-xl font-semibold mb-3">{t('methodology.swissEph.specs')}</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">
                        {t('methodology.swissEph.precision')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {t('methodology.swissEph.precisionDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">
                        {t('methodology.swissEph.coverage')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {t('methodology.swissEph.coverageDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">
                        {t('methodology.swissEph.jpl')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {t('methodology.swissEph.jplDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">
                        {t('methodology.swissEph.openSource')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {t('methodology.swissEph.openSourceDesc')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-foreground">
                        {t('methodology.swissEph.validation')}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {t('methodology.swissEph.validationDesc')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Implementation Details */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-display">
                {t('methodology.implementation.title')}
              </CardTitle>
              <CardDescription className="text-base mt-1">
                {t('methodology.implementation.subtitle')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.implementation.houseSystems')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li>
                    <strong>{t('methodology.implementation.placidus')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.koch')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.equal')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.wholeSigns')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.campanus')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.regiomontanus')}</strong>
                  </li>
                </ul>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.implementation.planets')}
                </h5>
                <p className="text-sm text-muted-foreground mb-2">
                  {t('methodology.implementation.planetsList')}
                </p>
                <p className="text-xs text-muted-foreground italic">
                  {t('methodology.implementation.planetsNote')}
                </p>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.implementation.aspects')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li>
                    <strong>{t('methodology.implementation.majorAspects')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.minorAspects')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.orbs')}</strong>
                  </li>
                  <li>
                    <strong>{t('methodology.implementation.applying')}</strong>
                  </li>
                </ul>
              </div>

              <Separator className="my-4" />

              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.implementation.future')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                  <li>{t('methodology.implementation.future1')}</li>
                  <li>{t('methodology.implementation.future2')}</li>
                  <li>{t('methodology.implementation.future3')}</li>
                  <li>{t('methodology.implementation.future4')}</li>
                  <li>{t('methodology.implementation.future5')}</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* References */}
          <Card className="border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl font-display">
                {t('methodology.references.title')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.references.classicTexts')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>
                    <strong>Tetrabiblos</strong> - Claudius Ptolemy (II d.C.)
                  </li>
                  <li>
                    <strong>Anthology</strong> - Vettius Valens (II d.C.)
                  </li>
                  <li>
                    <strong>Carmen Astrologicum</strong> - Dorotheus de Sidon (I d.C.)
                  </li>
                  <li>
                    <strong>The Great Introduction</strong> - Abu Ma'shar (IX d.C.)
                  </li>
                  <li>
                    <strong>Christian Astrology</strong> - William Lilly (1647)
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.references.techDocs')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>
                    <a
                      href="https://www.astro.com/swisseph/swephinfo_e.htm"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      Swiss Ephemeris Official Documentation
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://ssd.jpl.nasa.gov/planets/eph_export.html"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      JPL Planetary and Lunar Ephemerides
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/lmeazzini/astro-natal-chart"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      GitHub Repository
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <h5 className="font-semibold text-foreground mb-2">
                  {t('methodology.references.contemporaryAuthors')}
                </h5>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>
                    <strong>Chris Brennan</strong> - "Hellenistic Astrology: The Study of Fate and
                    Fortune"
                  </li>
                  <li>
                    <strong>Demetra George</strong> - "Ancient Astrology in Theory and Practice"
                  </li>
                  <li>
                    <strong>Robert Hand</strong> - "Night & Day: Planetary Sect in Astrology"
                  </li>
                  <li>
                    <strong>Benjamin Dykes</strong> - Medieval/Persian translations
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="text-center py-8">
            <h3 className="text-2xl font-bold mb-4">{t('methodology.cta.title')}</h3>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              {t('methodology.cta.subtitle')}
            </p>
            <div className="flex gap-4 justify-center">
              <Button asChild size="lg">
                <Link to="/register">{t('methodology.cta.createAccount')}</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/charts/new">{t('methodology.cta.seeExample')}</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
