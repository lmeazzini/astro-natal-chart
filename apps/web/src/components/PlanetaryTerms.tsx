/**
 * PlanetaryTerms - Display planetary terms (bounds) analysis for a birth chart.
 *
 * Shows which planets are in whose terms, with support for multiple term systems
 * (Egyptian, Ptolemaic, Chaldean, Dorothean).
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';
import { getToken } from '@/services/api';
import { chartsService, termsService } from '@/services/charts';
import { ScrollText, CheckCircle2 } from 'lucide-react';
import type { ChartTermsData, TermsTableData, TermSystem, PlanetTermInfo } from '@/types/terms';

// Re-export types
export type { ChartTermsData, TermsTableData, TermSystem, PlanetTermInfo } from '@/types/terms';

// ============================================================================
// Constants
// ============================================================================

const ZODIAC_SIGNS = [
  'Aries',
  'Taurus',
  'Gemini',
  'Cancer',
  'Leo',
  'Virgo',
  'Libra',
  'Scorpio',
  'Sagittarius',
  'Capricorn',
  'Aquarius',
  'Pisces',
];

const planetSymbols: Record<string, string> = {
  Sun: '\u2609',
  Moon: '\u263D',
  Mercury: '\u263F',
  Venus: '\u2640',
  Mars: '\u2642',
  Jupiter: '\u2643',
  Saturn: '\u2644',
  Uranus: '\u2645',
  Neptune: '\u2646',
  Pluto: '\u2647',
};

const signSymbols: Record<string, string> = {
  Aries: '\u2648',
  Taurus: '\u2649',
  Gemini: '\u264A',
  Cancer: '\u264B',
  Leo: '\u264C',
  Virgo: '\u264D',
  Libra: '\u264E',
  Scorpio: '\u264F',
  Sagittarius: '\u2650',
  Capricorn: '\u2651',
  Aquarius: '\u2652',
  Pisces: '\u2653',
};

// ============================================================================
// Loading Skeleton
// ============================================================================

function TermsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-40" />
      </div>
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

// ============================================================================
// Props Interface
// ============================================================================

interface PlanetaryTermsProps {
  chartId: string;
  isLoading?: boolean;
}

// ============================================================================
// Main Component
// ============================================================================

export function PlanetaryTerms({ chartId, isLoading = false }: PlanetaryTermsProps) {
  const { t } = useTranslation();
  const { translatePlanet, translateSign } = useAstroTranslation();

  // State
  const [system, setSystem] = useState<TermSystem>('egyptian');
  const [termsData, setTermsData] = useState<ChartTermsData | null>(null);
  const [tableData, setTableData] = useState<TermsTableData | null>(null);
  const [loading, setLoading] = useState(false);
  const [showTable, setShowTable] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch chart terms when system changes
  useEffect(() => {
    async function fetchTerms() {
      const token = getToken();
      if (!token || !chartId) return;

      setLoading(true);
      setError(null);

      try {
        const data = await chartsService.getChartTerms(chartId, token, system);
        setTermsData(data);
      } catch (err) {
        console.error('Failed to fetch terms:', err);
        setError(t('components.planetaryTerms.noTermData'));
      } finally {
        setLoading(false);
      }
    }

    fetchTerms();
  }, [chartId, system, t]);

  // Fetch reference table when needed
  useEffect(() => {
    async function fetchTable() {
      if (!showTable) return;

      try {
        const data = await termsService.getTermsTable(system);
        setTableData(data);
      } catch (err) {
        console.error('Failed to fetch terms table:', err);
      }
    }

    fetchTable();
  }, [showTable, system]);

  // Handle system change
  const handleSystemChange = (newSystem: TermSystem) => {
    setSystem(newSystem);
  };

  // Show loading skeleton
  if (isLoading || loading) {
    return <TermsSkeleton />;
  }

  // Show error state
  if (error || !termsData) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-muted-foreground">
            {error || t('components.planetaryTerms.noTermData')}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with system selector */}
      <Card className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <ScrollText className="h-6 w-6 text-amber-600 dark:text-amber-400" />
              <div>
                <CardTitle className="text-lg">{t('components.planetaryTerms.title')}</CardTitle>
                <CardDescription className="text-sm mt-1">
                  {t('components.planetaryTerms.subtitle')}
                </CardDescription>
              </div>
            </div>

            {/* System Selector */}
            <Select value={system} onValueChange={(v) => handleSystemChange(v as TermSystem)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder={t('components.planetaryTerms.selectSystem')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="egyptian">{t('components.planetaryTerms.egyptian')}</SelectItem>
                <SelectItem value="ptolemaic">
                  {t('components.planetaryTerms.ptolemaic')}
                </SelectItem>
                <SelectItem value="chaldean">{t('components.planetaryTerms.chaldean')}</SelectItem>
                <SelectItem value="dorothean">
                  {t('components.planetaryTerms.dorothean')}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Planets Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[150px]">
                    {t('components.planetaryTerms.planet')}
                  </TableHead>
                  <TableHead>{t('components.planetaryTerms.termRuler')}</TableHead>
                  <TableHead className="text-right">
                    {t('components.planetaryTerms.inOwnTerm')}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {termsData.planets.map((planet: PlanetTermInfo) => (
                  <TableRow key={planet.planet}>
                    <TableCell className="font-medium">
                      <span className="inline-flex items-center gap-2">
                        <span className="text-lg">{planetSymbols[planet.planet] || ''}</span>
                        {translatePlanet(planet.planet)}
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex items-center gap-2">
                        <span className="text-lg">{planetSymbols[planet.term_ruler] || ''}</span>
                        {translatePlanet(planet.term_ruler)}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      {planet.in_own_term ? (
                        <Badge
                          variant="outline"
                          className="bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20"
                        >
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          {t('components.planetaryTerms.termPoints')}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Summary */}
          {termsData.summary.planets_in_own_term.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm text-muted-foreground">
                {t('components.planetaryTerms.planetsInOwnTerm')}:
              </span>
              {termsData.summary.planets_in_own_term.map((planet: string) => (
                <Badge key={planet} variant="secondary" className="text-xs">
                  {planetSymbols[planet] || ''} {translatePlanet(planet)}
                </Badge>
              ))}
            </div>
          )}

          {/* About Terms Info */}
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="about">
              <AccordionTrigger className="text-sm">
                {t('components.planetaryTerms.aboutTerms')}
              </AccordionTrigger>
              <AccordionContent>
                <p className="text-sm text-muted-foreground">
                  {t('components.planetaryTerms.aboutTermsDesc')}
                </p>
              </AccordionContent>
            </AccordionItem>

            {/* Reference Table */}
            <AccordionItem value="reference">
              <AccordionTrigger className="text-sm" onClick={() => setShowTable(true)}>
                {t('components.planetaryTerms.referenceTable')}
              </AccordionTrigger>
              <AccordionContent>
                {tableData ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="sticky left-0 bg-background">
                            {t('components.planetaryTerms.sign')}
                          </TableHead>
                          {[1, 2, 3, 4, 5].map((i) => (
                            <TableHead key={i} className="text-center min-w-[100px]">
                              {t('components.planetaryTerms.termNumber', { number: i })}
                            </TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {ZODIAC_SIGNS.map((sign) => (
                          <TableRow key={sign}>
                            <TableCell className="sticky left-0 bg-background font-medium">
                              <span className="inline-flex items-center gap-1">
                                <span>{signSymbols[sign] || ''}</span>
                                {translateSign(sign)}
                              </span>
                            </TableCell>
                            {tableData.signs[sign]?.map((term, idx) => (
                              <TableCell key={idx} className="text-center">
                                <div className="text-sm">
                                  {planetSymbols[term.ruler] || ''} {translatePlanet(term.ruler)}
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  {term.start}°-{term.end}°
                                </div>
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <Skeleton className="h-96 w-full" />
                )}
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}
