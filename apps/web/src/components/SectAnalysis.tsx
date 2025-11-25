/**
 * SectAnalysis - Component for visualizing chart sect (day/night) analysis
 *
 * Features:
 * - Visual diagram showing Sun above/below horizon
 * - Classification of planets as in-sect or out-of-sect
 * - Benefics and malefics performance indicators
 * - Educational section explaining sect concepts
 */

import { useTranslation } from 'react-i18next';
import { Sun, Moon, Star, AlertTriangle, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { getPlanetSymbol } from '@/utils/astro';
import type { SectAnalysisData } from '@/services/charts';

// Classical planet order for sorting (traditional)
const CLASSICAL_PLANET_ORDER = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'];

interface SectAnalysisProps {
  sectData: SectAnalysisData;
}

export function SectAnalysis({ sectData }: SectAnalysisProps) {
  const { t } = useTranslation('translation', { keyPrefix: 'components.sect' });
  const { sect, sun_house, planets_by_sect, benefics, malefics } = sectData;
  const isDiurnal = sect === 'diurnal';

  // Combine all planets for the table
  const allPlanets = [
    ...planets_by_sect.in_sect,
    ...planets_by_sect.out_of_sect,
    ...planets_by_sect.neutral,
  ].sort((a, b) => {
    // Sort using classical planet order constant
    return CLASSICAL_PLANET_ORDER.indexOf(a.name) - CLASSICAL_PLANET_ORDER.indexOf(b.name);
  });

  return (
    <div className="space-y-6">
      {/* Header - Sect Type */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            {isDiurnal ? (
              <>
                <Sun className="w-8 h-8 text-yellow-500" />
                <span>{t('diurnalChart', { defaultValue: 'Diurnal Chart (Day)' })}</span>
              </>
            ) : (
              <>
                <Moon className="w-8 h-8 text-blue-400" />
                <span>{t('nocturnalChart', { defaultValue: 'Nocturnal Chart (Night)' })}</span>
              </>
            )}
          </CardTitle>
          <CardDescription>
            {t('sunInHouse', {
              defaultValue: 'Sun in House {{house}} ({{position}})',
              house: sun_house,
              position:
                sun_house >= 7
                  ? t('aboveHorizon', { defaultValue: 'above the horizon' })
                  : t('belowHorizon', { defaultValue: 'below the horizon' }),
            })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {isDiurnal
              ? t('diurnalDesc', {
                  defaultValue:
                    '☀️ Birth during the day - Sun above the horizon. Diurnal planets (Sun, Jupiter, Saturn) work better in this chart.',
                })
              : t('nocturnalDesc', {
                  defaultValue:
                    '🌙 Birth during the night - Sun below the horizon. Nocturnal planets (Moon, Venus, Mars) work better in this chart.',
                })}
          </p>
        </CardContent>
      </Card>

      {/* Visual Diagram */}
      <Card>
        <CardHeader>
          <CardTitle>{t('visualDiagram', { defaultValue: 'Visual Diagram' })}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative w-full h-48 bg-gradient-to-b from-sky-200 to-amber-100 dark:from-sky-900 dark:to-amber-900 rounded-lg overflow-hidden">
            {/* Horizon Line */}
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-black dark:bg-white" />

            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
              <span className="bg-white dark:bg-black px-2 py-1 text-xs font-semibold rounded">
                {t('horizon', { defaultValue: 'HORIZON' })}
              </span>
            </div>

            {/* Above Horizon Label */}
            <div className="absolute top-2 left-4">
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-sky-800 dark:text-sky-200">
                  {t('aboveHorizonLabel', { defaultValue: 'Above Horizon' })}
                </span>
                <span className="text-xs text-sky-600 dark:text-sky-300">
                  {t('houses7to12', { defaultValue: 'Houses 7-12 (Diurnal)' })}
                </span>
              </div>
            </div>

            {/* Below Horizon Label */}
            <div className="absolute bottom-2 left-4">
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-amber-800 dark:text-amber-200">
                  {t('belowHorizonLabel', { defaultValue: 'Below Horizon' })}
                </span>
                <span className="text-xs text-amber-600 dark:text-amber-300">
                  {t('houses1to6', { defaultValue: 'Houses 1-6 (Nocturnal)' })}
                </span>
              </div>
            </div>

            {/* Sun Position Indicator */}
            <div
              className={`absolute left-1/2 transform -translate-x-1/2 ${
                sun_house >= 7 ? 'top-8' : 'bottom-8'
              }`}
            >
              <div className="flex flex-col items-center">
                <div className="bg-yellow-500 rounded-full p-2 shadow-lg">
                  <Sun className="w-6 h-6 text-white" />
                </div>
                <p className="text-xs text-center mt-1 font-medium">
                  ☀️ {t('house', { defaultValue: 'House' })} {sun_house}
                </p>
              </div>
            </div>

            {/* Sect Badge */}
            <div className="absolute top-2 right-2">
              <Badge variant={isDiurnal ? 'default' : 'secondary'} className="text-sm">
                {isDiurnal
                  ? '☀️ ' + t('diurnal', { defaultValue: 'Diurnal' })
                  : '🌙 ' + t('nocturnal', { defaultValue: 'Nocturnal' })}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Benefics and Malefics */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Benefics Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="text-yellow-500" />
              {t('benefics', { defaultValue: 'Benefics' })}
            </CardTitle>
            <CardDescription>
              {t('beneficsDesc', { defaultValue: 'Jupiter and Venus - naturally helpful planets' })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {benefics.in_sect && (
              <div className="bg-green-50 dark:bg-green-950 p-3 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="text-green-600" size={20} />
                  <span className="font-semibold">
                    {getPlanetSymbol(benefics.in_sect.name)} {benefics.in_sect.name} (
                    {t('inSect', { defaultValue: 'In Sect' })}) ✓
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t('beneficInSectDesc', {
                    defaultValue: '{{planet}} in {{sign}} works optimally - balanced generosity.',
                    planet: benefics.in_sect.name,
                    sign: benefics.in_sect.sign,
                  })}
                </p>
              </div>
            )}

            {benefics.out_of_sect && (
              <div className="bg-yellow-50 dark:bg-yellow-950 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="text-yellow-600" size={20} />
                  <span className="font-semibold">
                    {getPlanetSymbol(benefics.out_of_sect.name)} {benefics.out_of_sect.name} (
                    {t('outOfSect', { defaultValue: 'Out of Sect' })}) ⚠️
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t('beneficOutOfSectDesc', {
                    defaultValue:
                      '{{planet}} in {{sign}} still helps, but may overdo it - indulgence.',
                    planet: benefics.out_of_sect.name,
                    sign: benefics.out_of_sect.sign,
                  })}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Malefics Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="text-red-500" />
              {t('malefics', { defaultValue: 'Malefics' })}
            </CardTitle>
            <CardDescription>
              {t('maleficsDesc', {
                defaultValue: 'Saturn and Mars - challenging but necessary planets',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {malefics.in_sect && (
              <div className="bg-orange-50 dark:bg-orange-950 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="text-orange-600" size={20} />
                  <span className="font-semibold">
                    {getPlanetSymbol(malefics.in_sect.name)} {malefics.in_sect.name} (
                    {t('inSect', { defaultValue: 'In Sect' })}) ✓
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t('maleficInSectDesc', {
                    defaultValue:
                      '{{planet}} in {{sign}} challenges constructively - useful discipline.',
                    planet: malefics.in_sect.name,
                    sign: malefics.in_sect.sign,
                  })}
                </p>
              </div>
            )}

            {malefics.out_of_sect && (
              <div className="bg-red-50 dark:bg-red-950 p-3 rounded-lg border border-red-200 dark:border-red-800">
                <div className="flex items-center gap-2 mb-1">
                  <XCircle className="text-red-600" size={20} />
                  <span className="font-semibold">
                    {getPlanetSymbol(malefics.out_of_sect.name)} {malefics.out_of_sect.name} (
                    {t('outOfSect', { defaultValue: 'Out of Sect' })}) ✗
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {t('maleficOutOfSectDesc', {
                    defaultValue:
                      '{{planet}} in {{sign}} is more challenging - requires special attention.',
                    planet: malefics.out_of_sect.name,
                    sign: malefics.out_of_sect.sign,
                  })}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* All Planets Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t('allPlanetsBySect', { defaultValue: 'All Planets by Sect' })}</CardTitle>
          <CardDescription>
            {t('allPlanetsDesc', {
              defaultValue: 'Classification of each planet according to sect rules',
            })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('planet', { defaultValue: 'Planet' })}</TableHead>
                <TableHead>{t('sign', { defaultValue: 'Sign' })}</TableHead>
                <TableHead>{t('naturalSect', { defaultValue: 'Natural Sect' })}</TableHead>
                <TableHead>{t('status', { defaultValue: 'Status' })}</TableHead>
                <TableHead>{t('performance', { defaultValue: 'Performance' })}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allPlanets.map((planet) => (
                <TableRow key={planet.name}>
                  <TableCell className="font-semibold">
                    {getPlanetSymbol(planet.name)} {planet.name}
                  </TableCell>
                  <TableCell>{planet.sign}</TableCell>
                  <TableCell>
                    {planet.planet_sect === 'diurnal' &&
                      '☀️ ' + t('diurnal', { defaultValue: 'Diurnal' })}
                    {planet.planet_sect === 'nocturnal' &&
                      '🌙 ' + t('nocturnal', { defaultValue: 'Nocturnal' })}
                    {planet.planet_sect === 'neutral' &&
                      '⚖️ ' + t('neutral', { defaultValue: 'Neutral' })}
                  </TableCell>
                  <TableCell>
                    {planet.in_sect ? (
                      <Badge variant="default" className="bg-green-600">
                        {t('inSect', { defaultValue: 'In Sect' })} ✓
                      </Badge>
                    ) : planet.planet_sect === 'neutral' ? (
                      <Badge variant="secondary">{t('neutral', { defaultValue: 'Neutral' })}</Badge>
                    ) : (
                      <Badge variant="outline">
                        {t('outOfSect', { defaultValue: 'Out of Sect' })}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {planet.performance === 'optimal' && (
                      <span className="text-green-600 font-medium">
                        {t('optimal', { defaultValue: 'Optimal' })}
                      </span>
                    )}
                    {planet.performance === 'moderate' && (
                      <span className="text-yellow-600 font-medium">
                        {t('moderate', { defaultValue: 'Moderate' })}
                      </span>
                    )}
                    {planet.performance === 'challenging' && (
                      <span className="text-red-600 font-medium">
                        {t('challenging', { defaultValue: 'Challenging' })}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Educational Section */}
      <Card>
        <CardHeader>
          <CardTitle>📚 {t('understandingSect', { defaultValue: 'Understanding Sect' })}</CardTitle>
        </CardHeader>
        <CardContent className="prose dark:prose-invert max-w-none">
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-semibold text-base mb-2">
                {t('whatIsSect', { defaultValue: 'What is Sect?' })}
              </h4>
              <p className="text-muted-foreground">
                {t('whatIsSectDesc', {
                  defaultValue:
                    'In traditional astrology, charts are divided into diurnal (day) and nocturnal (night) based on the Sun\'s position. Planets work better when they are "in sect" - aligned with the chart type.',
                })}
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-base mb-2">
                {t('whyItMatters', { defaultValue: 'Why does it matter?' })}
              </h4>
              <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                <li>
                  <strong>{t('beneficsInSect', { defaultValue: 'Benefics in sect' })}</strong>{' '}
                  {t('beneficsInSectEffect', {
                    defaultValue: '(Jupiter in day, Venus in night) are more generous and balanced',
                  })}
                </li>
                <li>
                  <strong>
                    {t('beneficsOutOfSect', { defaultValue: 'Benefics out of sect' })}
                  </strong>{' '}
                  {t('beneficsOutOfSectEffect', {
                    defaultValue: 'still help, but may overdo or be less effective',
                  })}
                </li>
                <li>
                  <strong>{t('maleficsInSect', { defaultValue: 'Malefics in sect' })}</strong>{' '}
                  {t('maleficsInSectEffect', {
                    defaultValue: '(Saturn in day, Mars in night) challenge constructively',
                  })}
                </li>
                <li>
                  <strong>
                    {t('maleficsOutOfSect', { defaultValue: 'Malefics out of sect' })}
                  </strong>{' '}
                  {t('maleficsOutOfSectEffect', {
                    defaultValue: 'are harder to integrate and can be more destructive',
                  })}
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-base mb-2">
                {t('howToUse', { defaultValue: 'How to use this?' })}
              </h4>
              <p className="text-muted-foreground">
                {t('howToUseDesc', {
                  defaultValue:
                    'Pay special attention to your out-of-sect malefics - these are areas that need more conscious work. Your in-sect benefics are natural resources you can leverage.',
                })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
