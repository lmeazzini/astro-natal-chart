import * as React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { listRagDocuments, getRagStats, type RagDocument, type RagStats } from '../services/rag';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';

export function RagDocumentsPage() {
  const { t } = useTranslation();
  const { user, isLoading: authLoading } = useAuth();
  const [documents, setDocuments] = React.useState<RagDocument[]>([]);
  const [stats, setStats] = React.useState<RagStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [page, setPage] = React.useState(1);
  const [totalPages, setTotalPages] = React.useState(1);
  const [total, setTotal] = React.useState(0);
  const [filterType, setFilterType] = React.useState<string>('');
  const pageSize = 20;

  const loadData = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [docsResponse, statsResponse] = await Promise.all([
        listRagDocuments(page, pageSize, filterType || undefined),
        getRagStats(),
      ]);
      setDocuments(docsResponse.documents);
      setTotalPages(docsResponse.total_pages);
      setTotal(docsResponse.total);
      setStats(statsResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load RAG documents');
    } finally {
      setLoading(false);
    }
  }, [page, filterType]);

  React.useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user, loadData]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Skeleton className="h-8 w-32 mx-auto mb-2" />
          <Skeleton className="h-4 w-24 mx-auto" />
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <ThemeToggle />
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard">{t('common.back')}</Link>
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            {t('ragDocuments.title', 'RAG Knowledge Base')}
          </h2>
          <p className="text-muted-foreground">
            {t('ragDocuments.description', 'Documents used for AI-enhanced astrological interpretations')}
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('ragDocuments.totalDocuments', 'Total Documents')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{stats.total_documents}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('ragDocuments.indexedDocuments', 'Indexed')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold text-green-600">{stats.indexed_documents}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('ragDocuments.textDocs', 'Text Documents')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{stats.documents_by_type?.text || 0}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t('ragDocuments.pdfDocs', 'PDF Documents')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{stats.documents_by_type?.pdf || 0}</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filter */}
        <div className="mb-6 flex gap-2">
          <Button
            variant={filterType === '' ? 'default' : 'outline'}
            size="sm"
            onClick={() => { setFilterType(''); setPage(1); }}
          >
            {t('ragDocuments.filterAll', 'All')}
          </Button>
          <Button
            variant={filterType === 'text' ? 'default' : 'outline'}
            size="sm"
            onClick={() => { setFilterType('text'); setPage(1); }}
          >
            {t('ragDocuments.filterText', 'Text')}
          </Button>
          <Button
            variant={filterType === 'pdf' ? 'default' : 'outline'}
            size="sm"
            onClick={() => { setFilterType('pdf'); setPage(1); }}
          >
            {t('ragDocuments.filterPdf', 'PDF')}
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 text-destructive p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-5 w-64" />
                  <Skeleton className="h-4 w-32" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-16 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <>
            {/* Documents List */}
            <div className="space-y-4">
              {documents.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-muted-foreground">
                    {t('ragDocuments.noDocuments', 'No documents found')}
                  </CardContent>
                </Card>
              ) : (
                documents.map((doc) => (
                  <Card key={doc.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{doc.title}</CardTitle>
                          <CardDescription className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{doc.document_type.toUpperCase()}</Badge>
                            {doc.page !== null && (
                              <span className="text-xs">
                                {t('ragDocuments.page', 'Page')} {doc.page}
                              </span>
                            )}
                            {doc.source && (
                              <span className="text-xs truncate max-w-[200px]" title={doc.source}>
                                {doc.source}
                              </span>
                            )}
                          </CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                          {doc.indexed ? (
                            <Badge variant="default" className="bg-green-600">
                              {t('ragDocuments.indexed', 'Indexed')}
                            </Badge>
                          ) : (
                            <Badge variant="secondary">
                              {t('ragDocuments.pending', 'Pending')}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {doc.content_preview}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        {t('ragDocuments.createdAt', 'Created')}: {new Date(doc.created_at).toLocaleString()}
                      </p>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-muted-foreground">
                  {t('ragDocuments.showing', 'Showing')} {((page - 1) * pageSize) + 1}-{Math.min(page * pageSize, total)} {t('ragDocuments.of', 'of')} {total}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    {t('common.previous', 'Previous')}
                  </Button>
                  <span className="flex items-center px-3 text-sm">
                    {page} / {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    {t('common.next', 'Next')}
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
