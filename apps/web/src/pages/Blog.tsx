import * as React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import {
  getBlogPosts,
  getBlogMetadata,
  type BlogPostListItem,
  type BlogMetadata,
} from '../services/blog';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { useAuth } from '../contexts/AuthContext';
import { amplitudeService } from '../services/amplitude';
import { Clock, Eye, Calendar, ChevronLeft, ChevronRight, Tag, FolderOpen } from 'lucide-react';

function formatDate(dateString: string | null, locale: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString(locale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function BlogPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [posts, setPosts] = React.useState<BlogPostListItem[]>([]);
  const [metadata, setMetadata] = React.useState<BlogMetadata | null>(null);
  const [totalPages, setTotalPages] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const hasTrackedPageView = React.useRef(false);

  const category = searchParams.get('category') || undefined;
  const tag = searchParams.get('tag') || undefined;
  const page = parseInt(searchParams.get('page') || '1', 10);
  const pageSize = 9;

  const loadData = React.useCallback(async () => {
    setLoading(true);
    try {
      const data = await getBlogPosts({
        category,
        tag,
        page,
        page_size: pageSize,
      });
      setPosts(data.items);
      setTotalPages(data.total_pages);
    } catch (error) {
      console.error('Error loading blog posts:', error);
    } finally {
      setLoading(false);
    }
  }, [category, tag, page, pageSize]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  React.useEffect(() => {
    loadMetadata();
  }, []);

  async function loadMetadata() {
    try {
      const data = await getBlogMetadata();
      setMetadata(data);
    } catch (error) {
      console.error('Error loading blog metadata:', error);
    }
  }

  // Track page view on mount (with ref guard to prevent StrictMode double-tracking)
  React.useEffect(() => {
    if (!hasTrackedPageView.current && !loading && posts.length >= 0) {
      amplitudeService.track('blog_viewed', {
        source: searchParams.get('source') || 'direct',
        post_count: posts.length,
        ...(category && { category_filter: category }),
        ...(tag && { tag_filter: tag }),
        ...(user?.id && { user_id: user.id }),
      });
      hasTrackedPageView.current = true;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading]); // Track once when loading completes

  // Track post clicks
  function handlePostClick(post: BlogPostListItem) {
    amplitudeService.track('blog_post_clicked', {
      post_slug: post.slug,
      post_title: post.title,
      source: 'blog_list',
      ...(user?.id && { user_id: user.id }),
    });
  }

  function handleCategoryClick(cat: string | null) {
    const newParams = new URLSearchParams();
    if (cat) {
      newParams.set('category', cat);
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  }

  function handleTagClick(tagName: string) {
    const newParams = new URLSearchParams();
    newParams.set('tag', tagName);
    newParams.set('page', '1');
    setSearchParams(newParams);
  }

  function handlePageChange(newPage: number) {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const pageTitle = category
    ? `${t('blog.title')} - ${category}`
    : tag
      ? `${t('blog.title')} - #${tag}`
      : t('blog.title');

  return (
    <>
      <Helmet>
        <title>{pageTitle} | Real Astrology</title>
        <meta name="description" content={t('blog.description')} />
        <meta property="og:title" content={pageTitle} />
        <meta property="og:description" content={t('blog.description')} />
        <meta property="og:type" content="website" />
        <link rel="canonical" href={`${window.location.origin}/blog`} />
      </Helmet>

      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto flex h-16 items-center justify-between px-4">
            <Link to="/" className="text-xl font-bold text-primary">
              Real Astrology
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

        <main className="container mx-auto px-4 py-8">
          {/* Page Title */}
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-foreground">{t('blog.title')}</h1>
            <p className="mt-2 text-lg text-muted-foreground">{t('blog.subtitle')}</p>
          </div>

          {/* Active Filters */}
          {(category || tag) && (
            <div className="mb-6 flex items-center gap-2">
              <span className="text-sm text-muted-foreground">{t('blog.filteringBy')}:</span>
              {category && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <FolderOpen className="h-3 w-3" />
                  {category}
                  <button
                    onClick={() => handleCategoryClick(null)}
                    className="ml-1 hover:text-destructive"
                    aria-label={t('blog.clearFilter')}
                  >
                    ×
                  </button>
                </Badge>
              )}
              {tag && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Tag className="h-3 w-3" />
                  {tag}
                  <button
                    onClick={() => setSearchParams(new URLSearchParams())}
                    className="ml-1 hover:text-destructive"
                    aria-label={t('blog.clearFilter')}
                  >
                    ×
                  </button>
                </Badge>
              )}
            </div>
          )}

          <div className="grid gap-8 lg:grid-cols-4">
            {/* Main Content */}
            <div className="lg:col-span-3">
              {/* Posts Grid */}
              {loading ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <Card key={i}>
                      <Skeleton className="aspect-video w-full" />
                      <CardContent className="p-4">
                        <Skeleton className="mb-2 h-6 w-3/4" />
                        <Skeleton className="mb-4 h-4 w-full" />
                        <Skeleton className="h-4 w-1/2" />
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : posts.length === 0 ? (
                <div className="rounded-lg border border-dashed p-12 text-center">
                  <p className="text-muted-foreground">{t('blog.noPosts')}</p>
                </div>
              ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {posts.map((post) => (
                    <Link
                      key={post.id}
                      to={`/blog/${post.slug}`}
                      onClick={() => handlePostClick(post)}
                    >
                      <Card className="h-full overflow-hidden transition-shadow hover:shadow-lg">
                        {post.featured_image_url ? (
                          <img
                            src={post.featured_image_url}
                            alt={post.title}
                            className="aspect-video w-full object-cover"
                          />
                        ) : (
                          <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-primary/20 to-primary/5">
                            <span className="text-4xl">✨</span>
                          </div>
                        )}
                        <CardContent className="p-4">
                          <Badge variant="outline" className="mb-2">
                            {post.category}
                          </Badge>
                          <h2 className="mb-2 line-clamp-2 text-lg font-semibold text-foreground">
                            {post.title}
                          </h2>
                          <p className="mb-4 line-clamp-2 text-sm text-muted-foreground">
                            {post.excerpt}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatDate(post.published_at, i18n.language)}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {post.read_time_minutes} min
                            </span>
                            <span className="flex items-center gap-1">
                              <Eye className="h-3 w-3" />
                              {post.views_count}
                            </span>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex items-center justify-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(page - 1)}
                    disabled={page <= 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    {t('common.previous')}
                  </Button>
                  <span className="px-4 text-sm text-muted-foreground">
                    {t('common.pageOf', { page, total: totalPages })}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(page + 1)}
                    disabled={page >= totalPages}
                  >
                    {t('common.next')}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <aside className="space-y-6">
              {/* Categories */}
              {metadata && metadata.categories.length > 0 && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="mb-3 font-semibold text-foreground">{t('blog.categories')}</h3>
                    <ul className="space-y-2">
                      <li>
                        <button
                          onClick={() => handleCategoryClick(null)}
                          className={`flex w-full items-center justify-between text-sm transition-colors hover:text-primary ${
                            !category ? 'font-medium text-primary' : 'text-muted-foreground'
                          }`}
                        >
                          <span>{t('blog.allCategories')}</span>
                          <span>{metadata.total_posts}</span>
                        </button>
                      </li>
                      {metadata.categories.map((cat) => (
                        <li key={cat.category}>
                          <button
                            onClick={() => handleCategoryClick(cat.category)}
                            className={`flex w-full items-center justify-between text-sm transition-colors hover:text-primary ${
                              category === cat.category
                                ? 'font-medium text-primary'
                                : 'text-muted-foreground'
                            }`}
                          >
                            <span>{cat.category}</span>
                            <span>{cat.count}</span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Popular Tags */}
              {metadata && metadata.popular_tags.length > 0 && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="mb-3 font-semibold text-foreground">{t('blog.popularTags')}</h3>
                    <div className="flex flex-wrap gap-2">
                      {metadata.popular_tags.slice(0, 15).map((tagItem) => (
                        <Badge
                          key={tagItem.tag}
                          variant={tag === tagItem.tag ? 'default' : 'secondary'}
                          className="cursor-pointer transition-colors hover:bg-primary hover:text-primary-foreground"
                          onClick={() => handleTagClick(tagItem.tag)}
                        >
                          #{tagItem.tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
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
