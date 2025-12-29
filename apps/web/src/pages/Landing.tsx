/**
 * Landing Page - Midnight & Paper Design System
 * Elegant, conversion-focused homepage with traditional astrology focus
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Star, Sun, Moon, Compass, Scroll, Target, ShieldCheck, ArrowRight } from 'lucide-react';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Button } from '@/components/ui/button';
import heroBg from '@/assets/ancient_celestial_map_background.jpg';

export function LandingPage() {
  const { t } = useTranslation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="w-full overflow-x-hidden">
      {/* Navigation - Sticky with border on scroll */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-primary/95 backdrop-blur-md border-b border-primary-foreground/20 shadow-lg'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <span className="text-xl font-serif font-medium text-primary-foreground">
              Real Astrology
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link
              to="/blog"
              className="text-sm font-medium text-primary-foreground/80 hover:text-primary-foreground transition-colors"
            >
              {t('landing.nav.blog')}
            </Link>
            <Link
              to="/methodology"
              className="text-sm font-medium text-primary-foreground/80 hover:text-primary-foreground transition-colors"
            >
              {t('landing.nav.techniques')}
            </Link>
            <Link
              to="/pricing"
              className="text-sm font-medium text-primary-foreground/80 hover:text-primary-foreground transition-colors"
            >
              {t('landing.nav.pricing')}
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <LanguageSelector />
            <ThemeToggle />
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="text-primary-foreground hover:bg-primary-foreground/10"
            >
              <Link to="/login">{t('landing.login')}</Link>
            </Button>
            <Button
              asChild
              size="sm"
              className="bg-accent text-accent-foreground hover:bg-accent/90"
            >
              <Link to="/register">{t('landing.signup')}</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-primary text-primary-foreground">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src={heroBg}
            alt="Celestial Map"
            className="w-full h-full object-cover opacity-40 mix-blend-overlay"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-primary/30 via-primary/60 to-background" />
        </div>

        <div className="relative z-10 container mx-auto px-4 text-center max-w-4xl space-y-6 md:space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <span className="inline-block py-1 px-3 rounded-full border border-accent/30 bg-accent/10 text-accent text-xs font-medium tracking-widest uppercase mb-4 md:mb-6">
              {t('landing.hero.badge')}
            </span>
            <h1 className="text-4xl sm:text-5xl md:text-7xl font-serif font-medium tracking-tight leading-[1.1] mb-6 text-balance">
              {t('landing.hero.title')}{' '}
              <span className="italic text-secondary-foreground/90">
                {t('landing.hero.titleHighlight')}
              </span>
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-primary-foreground/80 max-w-2xl mx-auto leading-relaxed mb-8 md:mb-10 text-balance">
              {t('landing.hero.subtitle')}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="w-full sm:w-auto px-8 py-4 bg-accent text-accent-foreground rounded-full font-medium text-lg transition-transform hover:scale-105 active:scale-95 shadow-lg shadow-accent/20 flex items-center justify-center gap-2"
              >
                {t('landing.hero.cta')} <ArrowRight className="w-4 h-4" />
              </Link>
              <a
                href="#features"
                className="w-full sm:w-auto px-8 py-4 bg-transparent border border-primary-foreground/20 text-primary-foreground rounded-full font-medium text-lg hover:bg-primary-foreground/5 transition-colors"
              >
                {t('landing.hero.explore')}
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-4">
            <h2 className="text-3xl md:text-4xl font-serif text-primary">
              {t('landing.features.title')}
            </h2>
            <p className="text-muted-foreground text-lg">{t('landing.features.subtitle')}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Star className="w-6 h-6" />,
                title: t('landing.features.dignities.title'),
                desc: t('landing.features.dignities.desc'),
              },
              {
                icon: <Sun className="w-6 h-6" />,
                title: t('landing.features.sect.title'),
                desc: t('landing.features.sect.desc'),
              },
              {
                icon: <Compass className="w-6 h-6" />,
                title: t('landing.features.arabicParts.title'),
                desc: t('landing.features.arabicParts.desc'),
              },
              {
                icon: <Scroll className="w-6 h-6" />,
                title: t('landing.features.temperament.title'),
                desc: t('landing.features.temperament.desc'),
              },
              {
                icon: <Target className="w-6 h-6" />,
                title: t('landing.features.classical.title'),
                desc: t('landing.features.classical.desc'),
              },
              {
                icon: <Moon className="w-6 h-6" />,
                title: t('landing.features.timing.title'),
                desc: t('landing.features.timing.desc'),
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group p-8 rounded-xl bg-card border border-border hover:border-primary/20 hover:shadow-xl transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-full bg-secondary/30 flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-serif font-medium mb-3 text-primary">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* "Not Guesswork" Section */}
      <section className="py-24 bg-muted/30 border-y border-border/50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <h2 className="text-4xl md:text-5xl font-serif text-primary leading-tight">
                {t('landing.notGuesswork.title')} <br />
                <span className="text-muted-foreground italic">
                  {t('landing.notGuesswork.subtitle')}
                </span>
              </h2>
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="mt-1 w-10 h-10 flex-shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-primary font-serif font-bold">
                    1
                  </div>
                  <div>
                    <h4 className="text-xl font-serif font-medium mb-2">
                      {t('landing.notGuesswork.step1.title')}
                    </h4>
                    <p className="text-muted-foreground">{t('landing.notGuesswork.step1.desc')}</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="mt-1 w-10 h-10 flex-shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-primary font-serif font-bold">
                    2
                  </div>
                  <div>
                    <h4 className="text-xl font-serif font-medium mb-2">
                      {t('landing.notGuesswork.step2.title')}
                    </h4>
                    <p className="text-muted-foreground">{t('landing.notGuesswork.step2.desc')}</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="mt-1 w-10 h-10 flex-shrink-0 rounded-full bg-primary/10 flex items-center justify-center text-primary font-serif font-bold">
                    3
                  </div>
                  <div>
                    <h4 className="text-xl font-serif font-medium mb-2">
                      {t('landing.notGuesswork.step3.title')}
                    </h4>
                    <p className="text-muted-foreground">{t('landing.notGuesswork.step3.desc')}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-accent/20 blur-3xl rounded-full transform rotate-12" />
              <div className="relative bg-card border border-border rounded-2xl p-8 shadow-2xl">
                {/* Visual Abstract Chart Representation */}
                <div className="aspect-square rounded-full border-2 border-dashed border-primary/20 relative flex items-center justify-center">
                  <div className="absolute inset-4 rounded-full border border-primary/10" />
                  <div className="absolute inset-12 rounded-full border border-primary/10" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-px h-full bg-primary/10" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-px bg-primary/10" />

                  {/* Animated Planets */}
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-0"
                  >
                    <div className="absolute top-8 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-accent shadow-[0_0_10px_hsl(var(--accent))]" />
                  </motion.div>

                  <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 45, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-8"
                  >
                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-primary" />
                  </motion.div>

                  <div className="text-center space-y-1 z-10 bg-card/80 backdrop-blur px-4 py-2 rounded border border-border">
                    <p className="text-xs uppercase tracking-widest text-muted-foreground">
                      {t('landing.notGuesswork.chart.label')}
                    </p>
                    <p className="font-serif text-lg text-primary">
                      {t('landing.notGuesswork.chart.dignity')}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section id="philosophy" className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center space-y-12">
            <div className="space-y-6">
              <h2 className="text-3xl md:text-5xl font-serif text-primary">
                {t('landing.philosophy.title')}
              </h2>
              <p className="text-xl text-muted-foreground leading-relaxed font-light text-balance">
                {t('landing.philosophy.quote')}
              </p>
            </div>

            <div className="relative py-12">
              {/* Decorative line */}
              <div className="absolute top-1/2 left-0 right-0 h-px bg-border" />
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-4">
                <Star className="w-6 h-6 text-accent" />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-12 text-left">
              <div className="space-y-4">
                <h3 className="font-serif text-2xl text-primary">
                  {t('landing.philosophy.map.title')}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {t('landing.philosophy.map.desc')}
                </p>
              </div>
              <div className="space-y-4">
                <h3 className="font-serif text-2xl text-primary">
                  {t('landing.philosophy.character.title')}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {t('landing.philosophy.character.desc')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 bg-background text-center">
        <div className="container mx-auto px-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 text-green-700 dark:text-green-400 text-sm font-medium mb-8">
            <ShieldCheck className="w-4 h-4" /> {t('landing.cta.gdpr')}
          </div>
          <h2 className="text-3xl md:text-5xl font-serif text-primary mb-6">
            {t('landing.cta.title')}
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto mb-10">
            {t('landing.cta.subtitle')}
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-10 py-4 bg-primary text-primary-foreground rounded-full font-medium text-lg transition-all hover:shadow-xl hover:-translate-y-1"
          >
            {t('landing.cta.button')}
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/logo.png" alt="Real Astrology" className="h-6 w-6" />
                <span className="font-serif font-medium text-foreground">Real Astrology</span>
              </div>
              <p className="text-sm text-muted-foreground">{t('landing.footer.tagline')}</p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('landing.footer.legal')}</h4>
              <div className="space-y-2">
                <Link
                  to="/terms"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.footer.terms')}
                </Link>
                <Link
                  to="/privacy"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.footer.privacy')}
                </Link>
                <Link
                  to="/cookies"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.footer.cookies')}
                </Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('landing.footer.access')}</h4>
              <div className="space-y-2">
                <Link
                  to="/login"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.footer.login')}
                </Link>
                <Link
                  to="/register"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.footer.register')}
                </Link>
                <Link
                  to="/blog"
                  className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {t('landing.nav.blog')}
                </Link>
              </div>
            </div>
          </div>
          <div className="pt-8 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Real Astrology. {t('footer.allRightsReserved')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
