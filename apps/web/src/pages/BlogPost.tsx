import * as React from 'react';
import { Link, useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import {
  getBlogPost,
  getRecentPosts,
  type BlogPost,
  type BlogPostListItem,
} from '../services/blog';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { useAuth } from '../contexts/AuthContext';
import { amplitudeService } from '../services/amplitude';
import {
  Clock,
  Eye,
  Calendar,
  ArrowLeft,
  Share2,
  Tag,
  User,
  ChevronRight,
  Check,
  Loader2,
} from 'lucide-react';

function formatDate(dateString: string | null, locale: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString(locale, {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });
}

export function BlogPostPage() {
  const { t, i18n } = useTranslation();
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const [post, setPost] = React.useState<BlogPost | null>(null);
  const [recentPosts, setRecentPosts] = React.useState<BlogPostListItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [sharing, setSharing] = React.useState(false);
  const [copied, setCopied] = React.useState(false);

  // Amplitude tracking refs
  const hasTrackedPageView = React.useRef(false);
  const hasTrackedReadCompletion = React.useRef(false);
  const pageLoadTime = React.useRef(Date.now());

  // Reset tracking refs when slug changes (for SPA navigation between posts)
  React.useEffect(() => {
    hasTrackedPageView.current = false;
    hasTrackedReadCompletion.current = false;
    pageLoadTime.current = Date.now();
  }, [slug]);

  React.useEffect(() => {
    if (!slug) return;

    async function loadPost(postSlug: string) {
      setLoading(true);
      setError(null);
      try {
        const data = await getBlogPost(postSlug);
        setPost(data);
      } catch (err) {
        setError(t('blog.postNotFound'));
        console.error('Error loading blog post:', err);
      } finally {
        setLoading(false);
      }
    }

    loadPost(slug);
  }, [slug, t]);

  React.useEffect(() => {
    async function loadRecent() {
      try {
        const data = await getRecentPosts(5);
        setRecentPosts(data.filter((p) => p.slug !== slug));
      } catch (err) {
        console.error('Error loading recent posts:', err);
      }
    }

    loadRecent();
  }, [slug]);

  // Track page view on mount (with ref guard to prevent StrictMode double-tracking)
  React.useEffect(() => {
    if (!hasTrackedPageView.current && post && !loading) {
      amplitudeService.track('blog_post_viewed', {
        post_slug: post.slug,
        post_title: post.title,
        reading_time: post.read_time_minutes,
        source: searchParams.get('source') || 'direct',
        ...(user?.id && { user_id: user.id }),
      });
      hasTrackedPageView.current = true;
      pageLoadTime.current = Date.now(); // Reset page load time when post loads
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [post, loading]); // Track once when post loads

  // Track read completion with Intersection Observer
  React.useEffect(() => {
    if (!post || hasTrackedReadCompletion.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasTrackedReadCompletion.current) {
            const timeOnPage = Math.floor((Date.now() - pageLoadTime.current) / 1000);
            amplitudeService.track('blog_post_read_completed', {
              post_slug: post.slug,
              estimated_read_percentage: 80,
              time_on_page_seconds: timeOnPage,
              ...(user?.id && { user_id: user.id }),
            });
            hasTrackedReadCompletion.current = true;
            observer.disconnect();
          }
        });
      },
      { threshold: 0.5 }
    );

    // Small delay to ensure DOM is ready
    const timeoutId = setTimeout(() => {
      const endMarker = document.getElementById('blog-post-end-marker');
      if (endMarker) observer.observe(endMarker);
    }, 100);

    return () => {
      clearTimeout(timeoutId);
      observer.disconnect();
    };
  }, [post, user?.id]);

  async function handleShare() {
    if (sharing) return;
    setSharing(true);
    setCopied(false);

    try {
      if (navigator.share && post) {
        await navigator.share({
          title: post.title,
          text: post.excerpt,
          url: window.location.href,
        });
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(window.location.href);
        setCopied(true);
        // Reset copied state after 2 seconds
        setTimeout(() => setCopied(false), 2000);
      }
    } catch (err) {
      // User cancelled or share failed - still try to copy
      if (!navigator.share) {
        try {
          await navigator.clipboard.writeText(window.location.href);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        } catch {
          // Clipboard also failed
        }
      }
    } finally {
      setSharing(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b bg-card">
          <div className="container mx-auto flex h-16 items-center justify-between px-4">
            <Link to="/" className="text-xl font-bold text-primary">
              Real Astrology
            </Link>
            <div className="flex items-center gap-4">
              <LanguageSelector />
              <ThemeToggle />
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="mx-auto max-w-3xl">
            <Skeleton className="mb-4 h-8 w-3/4" />
            <Skeleton className="mb-8 h-4 w-1/2" />
            <Skeleton className="mb-4 aspect-video w-full" />
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b bg-card">
          <div className="container mx-auto flex h-16 items-center justify-between px-4">
            <Link to="/" className="text-xl font-bold text-primary">
              Real Astrology
            </Link>
            <div className="flex items-center gap-4">
              <LanguageSelector />
              <ThemeToggle />
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-16 text-center">
          <h1 className="mb-4 text-2xl font-bold text-foreground">{t('blog.postNotFound')}</h1>
          <p className="mb-8 text-muted-foreground">{t('blog.postNotFoundDescription')}</p>
          <Button onClick={() => navigate('/blog')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t('blog.backToBlog')}
          </Button>
        </main>
      </div>
    );
  }

  const seoTitle = post.seo_title || post.title;
  const seoDescription = post.seo_description || post.excerpt;
  const canonicalUrl = `${window.location.origin}/blog/${post.slug}`;

  return (
    <>
      <Helmet>
        <title>{seoTitle} | Real Astrology Blog</title>
        <meta name="description" content={seoDescription} />
        {post.seo_keywords && <meta name="keywords" content={post.seo_keywords.join(', ')} />}

        {/* Open Graph */}
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDescription} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={canonicalUrl} />
        {post.featured_image_url && <meta property="og:image" content={post.featured_image_url} />}
        {post.published_at && (
          <meta property="article:published_time" content={post.published_at} />
        )}
        <meta property="article:section" content={post.category} />
        {post.tags.map((tag) => (
          <meta key={tag} property="article:tag" content={tag} />
        ))}

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDescription} />
        {post.featured_image_url && <meta name="twitter:image" content={post.featured_image_url} />}

        <link rel="canonical" href={canonicalUrl} />

        {/* JSON-LD Structured Data */}
        <script type="application/ld+json">
          {JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'BlogPosting',
            headline: post.title,
            description: post.excerpt,
            image: post.featured_image_url,
            datePublished: post.published_at,
            dateModified: post.updated_at,
            author: post.author
              ? {
                  '@type': 'Person',
                  name: post.author.full_name || 'Real Astrology Team',
                }
              : {
                  '@type': 'Organization',
                  name: 'Real Astrology',
                },
            publisher: {
              '@type': 'Organization',
              name: 'Real Astrology',
              logo: {
                '@type': 'ImageObject',
                url: `${window.location.origin}/logo.png`,
              },
            },
            mainEntityOfPage: {
              '@type': 'WebPage',
              '@id': canonicalUrl,
            },
          })}
        </script>
      </Helmet>

      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto flex h-16 items-center justify-between px-4">
            <Link to="/" className="flex items-center gap-2">
              <img
                src="/logo.png"
                alt="Real Astrology"
                className="h-9 w-9 rounded-full object-cover border border-primary/10"
              />
              <span className="text-xl font-bold text-primary">Real Astrology</span>
            </Link>
            <div className="flex items-center gap-4">
              <LanguageSelector />
              <ThemeToggle />
              {user ? (
                <Link to="/charts">
                  <Button variant="outline" size="sm">
                    {t('common.myCharts')}
                  </Button>
                </Link>
              ) : (
                <Link to="/login">
                  <Button variant="outline" size="sm">
                    {t('common.login')}
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </header>

        {/* Breadcrumb */}
        <nav className="border-b bg-muted/30 py-3">
          <div className="container mx-auto px-4">
            <ol className="flex items-center gap-2 text-sm text-muted-foreground">
              <li>
                <Link to="/" className="hover:text-primary">
                  {t('nav.home')}
                </Link>
              </li>
              <ChevronRight className="h-4 w-4" />
              <li>
                <Link to="/blog" className="hover:text-primary">
                  Blog
                </Link>
              </li>
              <ChevronRight className="h-4 w-4" />
              <li className="text-foreground">{post.title}</li>
            </ol>
          </div>
        </nav>

        <main className="container mx-auto px-4 py-8">
          <div className="grid gap-8 lg:grid-cols-4">
            {/* Article */}
            <article className="lg:col-span-3">
              <div className="mx-auto max-w-3xl">
                {/* Back button */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/blog')}
                  className="mb-6"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t('blog.backToBlog')}
                </Button>

                {/* Category */}
                <Link to={`/blog?category=${encodeURIComponent(post.category)}`}>
                  <Badge variant="outline" className="mb-4">
                    {post.category}
                  </Badge>
                </Link>

                {/* Title */}
                <h1 className="mb-4 text-4xl font-bold leading-tight text-foreground">
                  {post.title}
                </h1>

                {/* Subtitle */}
                {post.subtitle && (
                  <p className="mb-6 text-xl text-muted-foreground">{post.subtitle}</p>
                )}

                {/* Meta info */}
                <div className="mb-8 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                  {post.author && (
                    <span className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      {post.author.full_name || 'Real Astrology Team'}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {formatDate(post.published_at, i18n.language)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {post.read_time_minutes} min {t('blog.readTime')}
                  </span>
                  <span className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    {post.views_count} {t('blog.views')}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleShare}
                    disabled={sharing}
                    className="ml-auto"
                  >
                    {sharing ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : copied ? (
                      <Check className="mr-2 h-4 w-4 text-green-500" />
                    ) : (
                      <Share2 className="mr-2 h-4 w-4" />
                    )}
                    {sharing ? t('blog.sharing') : copied ? t('blog.copied') : t('blog.share')}
                  </Button>
                </div>

                {/* Featured image */}
                {post.featured_image_url && (
                  <img
                    src={post.featured_image_url}
                    alt={post.title}
                    className="mb-8 aspect-video w-full rounded-lg object-cover"
                  />
                )}

                {/* Content */}
                <div className="prose prose-lg max-w-none dark:prose-invert">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeRaw, rehypeSanitize]}
                  >
                    {post.content}
                  </ReactMarkdown>
                </div>

                {/* Invisible marker for read completion tracking */}
                <div id="blog-post-end-marker" aria-hidden="true" />

                {/* Tags */}
                {post.tags.length > 0 && (
                  <div className="mt-8 border-t pt-6">
                    <div className="flex items-center gap-2">
                      <Tag className="h-4 w-4 text-muted-foreground" />
                      <div className="flex flex-wrap gap-2">
                        {post.tags.map((tag) => (
                          <Link key={tag} to={`/blog?tag=${encodeURIComponent(tag)}`}>
                            <Badge
                              variant="secondary"
                              className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                            >
                              #{tag}
                            </Badge>
                          </Link>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </article>

            {/* Sidebar */}
            <aside className="space-y-6">
              {/* Recent Posts */}
              {recentPosts.length > 0 && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="mb-4 font-semibold text-foreground">{t('blog.recentPosts')}</h3>
                    <ul className="space-y-4">
                      {recentPosts.slice(0, 4).map((recentPost) => (
                        <li key={recentPost.id}>
                          <Link to={`/blog/${recentPost.slug}`} className="group block">
                            <h4 className="line-clamp-2 text-sm font-medium text-foreground group-hover:text-primary">
                              {recentPost.title}
                            </h4>
                            <span className="mt-1 text-xs text-muted-foreground">
                              {formatDate(recentPost.published_at, i18n.language)}
                            </span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* CTA */}
              <Card className="bg-primary text-primary-foreground">
                <CardContent className="p-4 text-center">
                  <h3 className="mb-2 font-semibold">{t('blog.ctaTitle')}</h3>
                  <p className="mb-4 text-sm opacity-90">{t('blog.ctaDescription')}</p>
                  <Link to={user ? '/charts/new' : '/register'}>
                    <Button variant="secondary" size="sm">
                      {t('blog.ctaButton')}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </aside>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-card border-t border-border py-12">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <img src="/logo.png" alt="Real Astrology" className="h-6 w-6" />
                  <span className="font-bold text-foreground">Real Astrology</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t('landing.footer.tagline', {
                    defaultValue: 'Astrologia Tradicional Para o Mundo Moderno',
                  })}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-foreground mb-4">
                  {t('landing.footer.legal', { defaultValue: 'Legal' })}
                </h4>
                <div className="space-y-2">
                  <Link
                    to="/terms"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.terms', { defaultValue: 'Termos de Uso' })}
                  </Link>
                  <Link
                    to="/privacy"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.privacy', { defaultValue: 'Política de Privacidade' })}
                  </Link>
                  <Link
                    to="/cookies"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.cookies', { defaultValue: 'Política de Cookies' })}
                  </Link>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-foreground mb-4">
                  {t('landing.footer.access', { defaultValue: 'Acesso' })}
                </h4>
                <div className="space-y-2">
                  <Link
                    to="/login"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.login', { defaultValue: 'Entrar' })}
                  </Link>
                  <Link
                    to="/register"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.register', { defaultValue: 'Criar Conta' })}
                  </Link>
                  <Link
                    to="/dashboard"
                    className="block text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {t('landing.footer.dashboard', { defaultValue: 'Dashboard' })}
                  </Link>
                </div>
              </div>
            </div>
            <div className="pt-8 border-t border-border text-center">
              <p className="text-sm text-muted-foreground">
                © {new Date().getFullYear()} Real Astrology.{' '}
                {t('landing.footer.madeWith', { defaultValue: 'Feito com ♄ e ♃ no Brasil.' })}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
