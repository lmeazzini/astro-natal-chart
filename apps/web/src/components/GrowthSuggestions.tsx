/**
 * Growth Suggestions Component
 * Displays AI-generated personal development suggestions based on natal chart
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  TrendingUp,
  AlertTriangle,
  Star,
  Target,
  Loader2,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getToken } from '@/services/api';
import { amplitudeService } from '@/services/amplitude';
import {
  interpretationsService,
  type GrowthSuggestionsData,
  type InterpretationItem,
} from '@/services/interpretations';

interface GrowthSuggestionsProps {
  chartId: string;
  initialGrowth?: Record<string, InterpretationItem> | null;
  /** Pre-parsed growth suggestions from chart_data (already in GrowthSuggestionsData format) */
  cachedSuggestions?: GrowthSuggestionsData | null;
}

interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  sectionType?: string;
}

function CollapsibleSection({
  title,
  children,
  defaultOpen = true,
  sectionType,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  function handleToggle() {
    const newState = !isOpen;
    setIsOpen(newState);

    // Track section expansion
    if (newState) {
      amplitudeService.track('growth_section_expanded', {
        section_name: title,
        section_type: sectionType || 'unknown',
        source: 'growth_suggestions',
      });
    }
  }

  return (
    <div className="border-b border-border/50 last:border-b-0">
      <button
        onClick={handleToggle}
        className="w-full flex items-center justify-between py-3 text-left hover:bg-muted/30 transition-colors px-2 rounded-lg"
      >
        <span className="font-semibold text-foreground">{title}</span>
        {isOpen ? (
          <ChevronUp className="h-5 w-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        )}
      </button>
      {isOpen && <div className="pb-4 px-2">{children}</div>}
    </div>
  );
}

/**
 * Convert growth interpretation items to GrowthSuggestionsData structure
 */
function parseGrowthItems(
  growthItems: Record<string, InterpretationItem> | null
): GrowthSuggestionsData | null {
  if (!growthItems || Object.keys(growthItems).length === 0) {
    return null;
  }

  try {
    // Parse each component from JSON content
    const points = growthItems.points ? JSON.parse(growthItems.points.content) : [];
    const challenges = growthItems.challenges ? JSON.parse(growthItems.challenges.content) : [];
    const opportunities = growthItems.opportunities
      ? JSON.parse(growthItems.opportunities.content)
      : [];
    const purpose = growthItems.purpose ? JSON.parse(growthItems.purpose.content) : null;

    return {
      growth_points: points,
      challenges,
      opportunities,
      purpose,
      summary: '',
    };
  } catch (error) {
    console.error('Error parsing growth items:', error);
    return null;
  }
}

export function GrowthSuggestions({
  chartId,
  initialGrowth,
  cachedSuggestions,
}: GrowthSuggestionsProps) {
  const { t } = useTranslation();
  // Use cachedSuggestions directly if available, otherwise parse initialGrowth
  const [suggestions, setSuggestions] = useState<GrowthSuggestionsData | null>(
    cachedSuggestions ?? parseGrowthItems(initialGrowth ?? null)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialLoad, setInitialLoad] = useState(true);

  // Initialize suggestions from props when available
  useEffect(() => {
    if (cachedSuggestions) {
      setSuggestions(cachedSuggestions);
    } else if (initialGrowth) {
      const parsed = parseGrowthItems(initialGrowth);
      setSuggestions(parsed);
    }
    setInitialLoad(false);
  }, [initialGrowth, cachedSuggestions]);

  const generateSuggestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = getToken();
      if (!token) {
        setError(
          t('growth.errors.notAuthenticated', {
            defaultValue: 'Please log in to generate suggestions',
          })
        );
        return;
      }

      // Use dedicated growth suggestions endpoint (POST /charts/{id}/growth-suggestions)
      const data = await interpretationsService.generateGrowthSuggestions(chartId, token);

      if (data) {
        setSuggestions(data);
      } else {
        setError(
          t('growth.errors.generateFailed', { defaultValue: 'Failed to generate suggestions' })
        );
      }
    } catch (err) {
      console.error('Error generating growth suggestions:', err);
      if (err instanceof Error) {
        if (err.message.includes('402')) {
          setError(
            t('growth.errors.insufficientCredits', {
              defaultValue: 'Insufficient credits. This feature requires 2 credits.',
            })
          );
        } else if (err.message.includes('403')) {
          setError(
            t('growth.errors.emailRequired', {
              defaultValue: 'Please verify your email to access this feature',
            })
          );
        } else if (err.message.includes('404')) {
          setError(t('growth.errors.chartNotFound', { defaultValue: 'Chart not found' }));
        } else if (err.message.includes('429')) {
          setError(
            t('growth.errors.rateLimited', {
              defaultValue: 'Too many requests. Please try again later.',
            })
          );
        } else {
          setError(err.message);
        }
      } else {
        setError(
          t('growth.errors.networkError', { defaultValue: 'Network error. Please try again.' })
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // Initial loading state while checking cache
  if (initialLoad) {
    return (
      <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
        <CardContent className="py-12">
          <div className="flex flex-col items-center justify-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="text-muted-foreground">
              {t('growth.loading', { defaultValue: 'Loading growth suggestions...' })}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Initial state - show button to generate (no cached suggestions found)
  if (!suggestions && !loading) {
    return (
      <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-h3 font-display flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            {t('growth.title', { defaultValue: 'Personal Development Suggestions' })}
          </CardTitle>
          <CardDescription>
            {t('growth.description', {
              defaultValue: 'Discover growth paths based on your natal chart',
            })}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            {t('growth.intro', {
              defaultValue:
                'Our AI analyzes your birth chart to identify growth opportunities, challenges to overcome, natural talents, and life purpose insights.',
            })}
          </p>
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
          <Button onClick={generateSuggestions} disabled={loading} className="w-full sm:w-auto">
            <Sparkles className="mr-2 h-4 w-4" />
            {t('growth.generate', { defaultValue: 'Generate Suggestions' })}
          </Button>
          <p className="text-xs text-muted-foreground">
            {t('growth.disclaimer', {
              defaultValue:
                'These suggestions are based on astrological analysis and should not replace professional advice.',
            })}
          </p>
        </CardContent>
      </Card>
    );
  }

  // Loading state
  if (loading) {
    return (
      <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
        <CardContent className="py-12">
          <div className="flex flex-col items-center justify-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="text-muted-foreground">
              {t('growth.generating', {
                defaultValue: 'Analyzing your chart and generating personalized suggestions...',
              })}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('growth.generatingTime', { defaultValue: 'This may take 15-30 seconds' })}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Results state
  return (
    <div className="space-y-6">
      {/* Growth Points */}
      {suggestions?.growth_points && suggestions.growth_points.length > 0 && (
        <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
              <TrendingUp className="h-5 w-5" />
              {t('growth.growthPoints.title', { defaultValue: 'Growth Points' })}
            </CardTitle>
            <CardDescription>
              {t('growth.growthPoints.description', {
                defaultValue: 'Areas for personal development and actionable steps',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {suggestions.growth_points.map((point, index) => (
              <CollapsibleSection key={index} title={point.area} sectionType="growth_point">
                <div className="space-y-4 mt-2">
                  <div className="flex items-start gap-2">
                    <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                      {point.indicator}
                    </span>
                  </div>
                  <p className="text-muted-foreground">{point.explanation}</p>

                  <div className="bg-muted/50 p-4 rounded-lg">
                    <p className="font-semibold text-sm mb-2">
                      {t('growth.growthPoints.actions', { defaultValue: 'Practical Actions:' })}
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      {point.practical_actions.map((action, i) => (
                        <li key={i} className="text-sm text-muted-foreground">
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-950/30 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">
                      {t('growth.growthPoints.mindset', { defaultValue: 'Mindset Shift:' })}
                    </p>
                    <p className="text-sm italic text-blue-600 dark:text-blue-400">
                      "{point.mindset_shift}"
                    </p>
                  </div>
                </div>
              </CollapsibleSection>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Challenges */}
      {suggestions?.challenges && suggestions.challenges.length > 0 && (
        <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-600 dark:text-orange-400">
              <AlertTriangle className="h-5 w-5" />
              {t('growth.challenges.title', { defaultValue: 'Challenges to Overcome' })}
            </CardTitle>
            <CardDescription>
              {t('growth.challenges.description', {
                defaultValue: 'Obstacles and strategies to overcome them',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {suggestions.challenges.map((challenge, index) => (
              <CollapsibleSection key={index} title={challenge.name} sectionType="challenge">
                <div className="space-y-4 mt-2">
                  <div className="flex items-start gap-2">
                    <span className="text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 px-2 py-1 rounded">
                      {challenge.pattern}
                    </span>
                  </div>

                  <div>
                    <p className="font-semibold text-sm mb-1">
                      {t('growth.challenges.manifestation', { defaultValue: 'How it manifests:' })}
                    </p>
                    <p className="text-muted-foreground text-sm">{challenge.manifestation}</p>
                  </div>

                  <div>
                    <p className="font-semibold text-sm mb-1">
                      {t('growth.challenges.strategy', { defaultValue: 'Strategy:' })}
                    </p>
                    <p className="text-muted-foreground text-sm">{challenge.strategy}</p>
                  </div>

                  <div className="bg-orange-50 dark:bg-orange-950/30 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
                    <p className="text-sm font-semibold text-orange-700 dark:text-orange-300 mb-2">
                      {t('growth.challenges.practices', { defaultValue: 'Practices:' })}
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      {challenge.practices.map((practice, i) => (
                        <li key={i} className="text-sm text-orange-600 dark:text-orange-400">
                          {practice}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CollapsibleSection>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Opportunities */}
      {suggestions?.opportunities && suggestions.opportunities.length > 0 && (
        <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
              <Star className="h-5 w-5" />
              {t('growth.opportunities.title', { defaultValue: 'Talents & Opportunities' })}
            </CardTitle>
            <CardDescription>
              {t('growth.opportunities.description', {
                defaultValue: 'Natural gifts and how to leverage them',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {suggestions.opportunities.map((opp, index) => (
              <CollapsibleSection key={index} title={opp.talent} sectionType="opportunity">
                <div className="space-y-4 mt-2">
                  <div className="flex items-start gap-2">
                    <span className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 px-2 py-1 rounded">
                      {opp.indicator}
                    </span>
                  </div>
                  <p className="text-muted-foreground">{opp.description}</p>

                  <div className="bg-yellow-50 dark:bg-yellow-950/30 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <p className="text-sm font-semibold text-yellow-700 dark:text-yellow-300 mb-2">
                      {t('growth.opportunities.leverage', { defaultValue: 'How to leverage:' })}
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      {opp.leverage_tips.map((tip, i) => (
                        <li key={i} className="text-sm text-yellow-600 dark:text-yellow-400">
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CollapsibleSection>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Purpose */}
      {suggestions?.purpose && (
        <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-purple-600 dark:text-purple-400">
              <Target className="h-5 w-5" />
              {t('growth.purpose.title', { defaultValue: 'Life Purpose & Direction' })}
            </CardTitle>
            <CardDescription>
              {t('growth.purpose.description', {
                defaultValue: 'Soul direction and vocation insights',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">
                  {t('growth.purpose.soulDirection', { defaultValue: 'Soul Direction' })}
                </h4>
                <p className="text-sm text-purple-600 dark:text-purple-400">
                  {suggestions.purpose.soul_direction}
                </p>
              </div>

              <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">
                  {t('growth.purpose.vocation', { defaultValue: 'Vocation' })}
                </h4>
                <p className="text-sm text-purple-600 dark:text-purple-400">
                  {suggestions.purpose.vocation}
                </p>
              </div>

              <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">
                  {t('growth.purpose.contribution', { defaultValue: 'Contribution' })}
                </h4>
                <p className="text-sm text-purple-600 dark:text-purple-400">
                  {suggestions.purpose.contribution}
                </p>
              </div>

              <div className="bg-purple-50 dark:bg-purple-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">
                  {t('growth.purpose.integration', { defaultValue: 'Integration' })}
                </h4>
                <p className="text-sm text-purple-600 dark:text-purple-400">
                  {suggestions.purpose.integration}
                </p>
              </div>
            </div>

            {suggestions.purpose.next_steps && suggestions.purpose.next_steps.length > 0 && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/30 dark:to-blue-950/30 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-3">
                  {t('growth.purpose.nextSteps', { defaultValue: 'Next Steps' })}
                </h4>
                <ol className="list-decimal list-inside space-y-2">
                  {suggestions.purpose.next_steps.map((step, i) => (
                    <li key={i} className="text-sm text-purple-600 dark:text-purple-400">
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-center text-muted-foreground">
        {t('growth.disclaimer', {
          defaultValue:
            'These suggestions are based on astrological analysis and should not replace professional advice.',
        })}
      </p>
    </div>
  );
}
