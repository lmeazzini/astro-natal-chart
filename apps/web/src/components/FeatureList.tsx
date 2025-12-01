/**
 * FeatureList Component - Dynamic feature list from GitHub issues
 * Issue #74 - Automate dashboard feature lists with GitHub API integration
 */

import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ExternalLink, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Feature {
  title: string;
  number: number;
  url: string;
  created_at: string;
  closed_at: string | null;
}

interface FeaturesData {
  implemented: Feature[];
  in_progress: Feature[];
  planned: Feature[];
  last_updated: string;
}

// Cooldown time in milliseconds (30 seconds)
const REFRESH_COOLDOWN_MS = 30000;

export function FeatureList() {
  const { t, i18n } = useTranslation();
  const [features, setFeatures] = useState<FeaturesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<number>(0);
  const [cooldownRemaining, setCooldownRemaining] = useState<number>(0);

  const loadFeatures = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/github/features`);
      if (!response.ok) {
        throw new Error('Failed to load features');
      }
      const data = await response.json();
      setFeatures(data);
      setError(null);
    } catch {
      setError(t('dashboard.features.loadError', { defaultValue: 'Could not load features' }));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [t]);

  const handleRefresh = useCallback(async () => {
    const now = Date.now();
    const timeSinceLastRefresh = now - lastRefresh;

    // Check cooldown
    if (timeSinceLastRefresh < REFRESH_COOLDOWN_MS) {
      return;
    }

    setRefreshing(true);
    setLastRefresh(now);

    // Clear cache first
    try {
      await fetch(`${API_URL}/api/v1/github/features/cache`, { method: 'DELETE' });
    } catch {
      // Ignore cache clear errors
    }
    await loadFeatures();
  }, [loadFeatures, lastRefresh]);

  // Update cooldown timer
  useEffect(() => {
    if (lastRefresh === 0) return;

    const intervalId = setInterval(() => {
      const remaining = Math.max(0, REFRESH_COOLDOWN_MS - (Date.now() - lastRefresh));
      setCooldownRemaining(remaining);

      if (remaining === 0) {
        clearInterval(intervalId);
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [lastRefresh]);

  useEffect(() => {
    loadFeatures();
  }, [loadFeatures]);

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-64 mt-2" />
          </CardHeader>
          <CardContent className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-6 w-6 rounded" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-48 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </div>
                <Skeleton className="h-6 w-24" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setLoading(true);
              loadFeatures();
            }}
          >
            {t('common.retry', { defaultValue: 'Try again' })}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!features) {
    return null;
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(i18n.language, {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Implemented Features */}
      {features.implemented.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {t('dashboard.features.implemented', { defaultValue: 'Implemented Features' })}
              <Badge variant="default" className="ml-2">
                {features.implemented.length}
              </Badge>
            </CardTitle>
            <CardDescription>
              {t('dashboard.features.implementedDesc', {
                defaultValue: 'Features recently added to the platform',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 max-h-96 overflow-y-auto">
            {features.implemented.map((feature) => (
              <div key={feature.number} className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div className="flex-1">
                  <a
                    href={feature.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium hover:text-primary transition-colors flex items-center gap-1"
                  >
                    {feature.title}
                    <ExternalLink className="h-3 w-3 opacity-50" />
                  </a>
                  <p className="text-sm text-muted-foreground">
                    #{feature.number} •{' '}
                    {feature.closed_at
                      ? formatDate(feature.closed_at)
                      : formatDate(feature.created_at)}
                  </p>
                </div>
                <Badge variant="default">
                  {t('dashboard.features.done', { defaultValue: 'Done' })}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* In Progress Features */}
      {features.in_progress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {t('dashboard.features.inProgress', { defaultValue: 'In Development' })}
              <Badge variant="secondary" className="ml-2">
                {features.in_progress.length}
              </Badge>
            </CardTitle>
            <CardDescription>
              {t('dashboard.features.inProgressDesc', {
                defaultValue: 'Features currently being developed',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 max-h-96 overflow-y-auto">
            {features.in_progress.map((feature) => (
              <div key={feature.number} className="flex items-start gap-3">
                <span className="text-yellow-500 text-xl">⚙️</span>
                <div className="flex-1">
                  <a
                    href={feature.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium hover:text-primary transition-colors flex items-center gap-1"
                  >
                    {feature.title}
                    <ExternalLink className="h-3 w-3 opacity-50" />
                  </a>
                  <p className="text-sm text-muted-foreground">
                    #{feature.number} • {formatDate(feature.created_at)}
                  </p>
                </div>
                <Badge variant="secondary">
                  {t('dashboard.features.inProgressBadge', { defaultValue: 'In Progress' })}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Planned Features */}
      {features.planned.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {t('dashboard.features.planned', { defaultValue: 'Planned' })}
              <Badge variant="outline" className="ml-2">
                {features.planned.length}
              </Badge>
            </CardTitle>
            <CardDescription>
              {t('dashboard.features.plannedDesc', {
                defaultValue: 'Features planned for future versions',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 max-h-96 overflow-y-auto">
            {features.planned.map((feature) => (
              <div key={feature.number} className="flex items-start gap-3">
                <span className="text-muted-foreground text-xl">○</span>
                <div className="flex-1">
                  <a
                    href={feature.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium hover:text-primary transition-colors flex items-center gap-1"
                  >
                    {feature.title}
                    <ExternalLink className="h-3 w-3 opacity-50" />
                  </a>
                  <p className="text-sm text-muted-foreground">
                    #{feature.number} • {formatDate(feature.created_at)}
                  </p>
                </div>
                <Badge variant="outline">
                  {t('dashboard.features.plannedBadge', { defaultValue: 'Planned' })}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Footer with last update and refresh */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <p>
          {t('dashboard.features.lastUpdated', { defaultValue: 'Last updated' })}:{' '}
          {new Date(features.last_updated).toLocaleString(i18n.language)}
        </p>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing || cooldownRemaining > 0}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          {cooldownRemaining > 0
            ? `${Math.ceil(cooldownRemaining / 1000)}s`
            : t('common.refresh', { defaultValue: 'Refresh' })}
        </Button>
      </div>

      {/* Link to full roadmap */}
      <p className="text-sm text-muted-foreground">
        {t('dashboard.features.seeAll', { defaultValue: 'See all planned features on our' })}{' '}
        <a
          href="https://github.com/lmeazzini/astro-natal-chart/issues?q=is%3Aissue+is%3Aopen+label%3Afeature"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
        >
          {t('dashboard.features.publicRoadmap', { defaultValue: 'public roadmap' })} →
        </a>
      </p>
    </div>
  );
}
