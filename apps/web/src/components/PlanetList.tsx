/**
 * Planet List component - displays all planets with their positions
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { getPlanetSymbol, getSignSymbol, formatDMS } from '../utils/astro';
import { useAstroTranslation } from '../hooks/useAstroTranslation';
import { amplitudeService } from '../services/amplitude';
import {
  Dignities,
  getDignityBadge,
  getDignityScore,
  getScoreColorClass,
  getDignityDetails,
  getClassificationLabel,
} from '../utils/dignities';
import { staggerContainer, staggerItem } from '@/config/animations';
import type { RAGSourceInfo } from '../services/interpretations';

// shadcn/ui components
import { Table, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Info, BookOpen, ChevronDown } from 'lucide-react';

export interface PlanetPosition {
  name: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
  house: number;
  retrograde: boolean;
  dignities?: Dignities;
}

interface LordOfNativityData {
  planet: string;
  score: number;
  sign: string;
  house: number;
  classification: string;
}

interface PlanetListProps {
  planets: PlanetPosition[];
  showOnlyClassical?: boolean;
  interpretations?: Record<string, string>;
  ragSources?: Record<string, RAGSourceInfo[]>;
  lordOfNativity?: LordOfNativityData | null;
}

type SortBy = 'position' | 'house' | 'dignity';

// Classical 7 planets (no modern planets)
const CLASSICAL_PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'];

export function PlanetList({
  planets,
  showOnlyClassical = false,
  interpretations,
  ragSources,
  lordOfNativity,
}: PlanetListProps) {
  const { t } = useTranslation();
  const { translateSign, translatePlanet } = useAstroTranslation();
  const [sortBy, setSortBy] = useState<SortBy>('position');
  const [showDignityInfo, setShowDignityInfo] = useState(false);

  // Filter planets if showOnlyClassical is true
  let displayPlanets = showOnlyClassical
    ? planets.filter((p) => CLASSICAL_PLANETS.includes(p.name))
    : planets;

  // Sort planets based on selected criteria
  displayPlanets = [...displayPlanets].sort((a, b) => {
    if (sortBy === 'dignity') {
      const scoreA = getDignityScore(a.dignities);
      const scoreB = getDignityScore(b.dignities);
      return scoreB - scoreA; // Higher score first
    }
    if (sortBy === 'house') {
      return a.house - b.house;
    }
    // Default: sort by position (longitude)
    return a.longitude - b.longitude;
  });
  // Check if any planet has dignities (for showing dignity column)
  const hasDignities = displayPlanets.some((p) => p.dignities !== undefined);

  return (
    <div className="space-y-6">
      {/* Sorting Controls */}
      {hasDignities && (
        <div className="flex gap-4 items-center flex-wrap">
          <label className="text-sm font-medium text-foreground">
            {t('components.planetList.sortBy', { defaultValue: 'Ordenar por:' })}
          </label>
          <ToggleGroup
            type="single"
            value={sortBy}
            onValueChange={(value) => value && setSortBy(value as SortBy)}
          >
            <ToggleGroupItem
              value="position"
              aria-label={t('components.planetList.sortByPosition', {
                defaultValue: 'Ordenar por posição',
              })}
            >
              {t('components.planetList.position', { defaultValue: 'Posição' })}
            </ToggleGroupItem>
            <ToggleGroupItem
              value="house"
              aria-label={t('components.planetList.sortByHouse', {
                defaultValue: 'Ordenar por casa',
              })}
            >
              {t('components.planetList.house', { defaultValue: 'Casa' })}
            </ToggleGroupItem>
            <ToggleGroupItem
              value="dignity"
              aria-label={t('components.planetList.sortByStrength', {
                defaultValue: 'Ordenar por força',
              })}
            >
              💪 {t('components.planetList.strength', { defaultValue: 'Força' })}
            </ToggleGroupItem>
          </ToggleGroup>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDignityInfo(!showDignityInfo)}
            className="ml-auto"
          >
            <Info className="h-4 w-4 mr-2" />
            {showDignityInfo
              ? t('components.planetList.hideInfo', { defaultValue: 'Esconder Info' })
              : t('components.planetList.showInfo', { defaultValue: 'Mostrar Info' })}
          </Button>
        </div>
      )}

      {/* Dignity Info Card */}
      {showDignityInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {t('components.planetList.essentialDignities', {
                defaultValue: 'Dignidades Essenciais',
              })}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {t('components.planetList.dignitiesDescription', {
                defaultValue:
                  'As dignidades essenciais mostram a força de um planeta em determinado signo, baseadas na astrologia tradicional.',
              })}
            </p>
            <dl className="space-y-2 text-sm">
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  👑 {t('components.planetList.domicile', { defaultValue: 'Domicílio' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.domicileDesc', {
                    defaultValue: 'Planeta no signo que rege (+5)',
                  })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  🌟 {t('components.planetList.exaltation', { defaultValue: 'Exaltação' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.exaltationDesc', {
                    defaultValue: 'Ponto de maior força (+4)',
                  })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  ⬇️ {t('components.planetList.fall', { defaultValue: 'Queda' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.fallDesc', { defaultValue: 'Oposto à exaltação (-4)' })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  ⚠️ {t('components.planetList.detriment', { defaultValue: 'Detrimento' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.detrimentDesc', {
                    defaultValue: 'Oposto ao domicílio (-5)',
                  })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  🔥/🌙 {t('components.planetList.triplicity', { defaultValue: 'Triplicidade' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.triplicityDesc', {
                    defaultValue: 'Afinidade elemental (+3)',
                  })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  📊 {t('components.planetList.term', { defaultValue: 'Termo' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.termDesc', { defaultValue: 'Divisão de graus (+2)' })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  👤 {t('components.planetList.face', { defaultValue: 'Face' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.faceDesc', {
                    defaultValue: 'Divisão de 10 graus (+1)',
                  })}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">
                  🚶 {t('components.planetList.peregrine', { defaultValue: 'Peregrino' })}:
                </dt>
                <dd className="text-muted-foreground">
                  {t('components.planetList.peregrineDesc', { defaultValue: 'Sem dignidades (0)' })}
                </dd>
              </div>
            </dl>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                {t('components.planetList.scoreInfo', {
                  defaultValue:
                    'Score positivo indica planeta forte. Score negativo indica debilitação.',
                })}
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                {t('components.planetList.planet', { defaultValue: 'Planeta' })}
              </TableHead>
              <TableHead>{t('components.planetList.sign', { defaultValue: 'Signo' })}</TableHead>
              <TableHead>
                {t('components.planetList.position', { defaultValue: 'Posição' })}
              </TableHead>
              <TableHead className="text-center">
                {t('components.planetList.house', { defaultValue: 'Casa' })}
              </TableHead>
              {hasDignities && (
                <TableHead>
                  {t('components.planetList.dignities', { defaultValue: 'Dignidades' })}
                </TableHead>
              )}
              <TableHead className="text-center">
                {t('components.planetList.retrograde', { defaultValue: 'Retrógrado' })}
              </TableHead>
              <TableHead className="text-right">
                {t('components.planetList.speed', { defaultValue: 'Velocidade' })}
              </TableHead>
            </TableRow>
          </TableHeader>
          <motion.tbody
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="[&_tr]:border-b"
          >
            <AnimatePresence mode="popLayout">
              {displayPlanets.map((planet, index) => (
                <motion.tr
                  key={planet.name}
                  variants={staggerItem}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  layout
                  layoutId={planet.name}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="border-b transition-colors hover:bg-muted/50 cursor-pointer"
                  onClick={() => {
                    amplitudeService.track('planet_row_clicked', {
                      planet_name: planet.name,
                      sign: planet.sign,
                      house: planet.house,
                      retrograde: planet.retrograde,
                      source: 'planet_list',
                    });
                  }}
                >
                  {/* Planet Name with Symbol */}
                  <TableCell>
                    <motion.div
                      className="flex items-center gap-2"
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      <span className="text-2xl" title={translatePlanet(planet.name)}>
                        {getPlanetSymbol(planet.name)}
                      </span>
                      <span className="font-medium text-foreground">
                        {translatePlanet(planet.name)}
                      </span>
                      {lordOfNativity && lordOfNativity.planet === planet.name && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: 'spring', stiffness: 500, delay: 0.5 }}
                        >
                          <Badge
                            variant="outline"
                            className="bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20 text-xs"
                            title={t('components.planetList.lordOfNativityTitle', {
                              defaultValue: 'Senhor da Natividade - maior dignidade essencial',
                            })}
                          >
                            👑
                          </Badge>
                        </motion.div>
                      )}
                    </motion.div>
                  </TableCell>

                  {/* Sign with Symbol */}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="text-xl" title={translateSign(planet.sign)}>
                        {getSignSymbol(planet.sign)}
                      </span>
                      <span className="text-muted-foreground">{translateSign(planet.sign)}</span>
                    </div>
                  </TableCell>

                  {/* Position (Degree, Minute, Second) */}
                  <TableCell>
                    <span className="font-mono text-muted-foreground">
                      {formatDMS(planet.degree, planet.minute, planet.second)}
                    </span>
                  </TableCell>

                  {/* House */}
                  <TableCell className="text-center">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-xs">
                      {planet.house}
                    </span>
                  </TableCell>

                  {/* Dignities Badge */}
                  {hasDignities && (
                    <TableCell>
                      {planet.dignities ? (
                        <div className="flex flex-col gap-1">
                          <div
                            className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md border text-xs font-medium ${
                              getDignityBadge(planet.dignities).color
                            }`}
                            title={`Score: ${getDignityScore(planet.dignities)}`}
                          >
                            <span>{getDignityBadge(planet.dignities).icon}</span>
                            <span>{getDignityBadge(planet.dignities).label}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <span
                              className={`text-xs font-semibold ${getScoreColorClass(
                                getDignityScore(planet.dignities)
                              )}`}
                            >
                              {getDignityScore(planet.dignities) > 0 ? '+' : ''}
                              {getDignityScore(planet.dignities)}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              ({getClassificationLabel(planet.dignities.classification)})
                            </span>
                          </div>
                          {/* Detailed dignity list */}
                          {getDignityDetails(planet.dignities).length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {getDignityDetails(planet.dignities).map((detail, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center gap-0.5 text-xs text-muted-foreground"
                                  title={`${detail.label}: ${detail.points > 0 ? '+' : ''}${detail.points}`}
                                >
                                  {detail.icon}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  )}

                  {/* Retrograde Indicator */}
                  <TableCell className="text-center">
                    {planet.retrograde ? (
                      <Badge variant="destructive" className="font-semibold">
                        R
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground/30 text-xs">—</span>
                    )}
                  </TableCell>

                  {/* Speed (Daily Motion) */}
                  <TableCell className="text-right">
                    <span
                      className={`font-mono text-xs ${
                        planet.speed < 0 ? 'text-destructive' : 'text-muted-foreground'
                      }`}
                    >
                      {planet.speed.toFixed(4)}°/
                      {t('components.planetList.day', { defaultValue: 'dia' })}
                    </span>
                  </TableCell>
                </motion.tr>
              ))}
            </AnimatePresence>
          </motion.tbody>
        </Table>
      </div>

      {/* Summary */}
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            <strong className="text-foreground">{displayPlanets.length}</strong>{' '}
            {t('components.planetList.planets', { defaultValue: 'planetas' })}
            {showOnlyClassical &&
              ` ${t('components.planetList.classical', { defaultValue: 'clássicos' })}`}{' '}
            {t('components.planetList.calculated', { defaultValue: 'calculados' })} •{' '}
            <strong className="text-foreground">
              {displayPlanets.filter((p) => p.retrograde).length}
            </strong>{' '}
            {t('components.planetList.retrogradeCount', { defaultValue: 'retrógrado(s)' })}
          </p>
          {showOnlyClassical && (
            <p className="mt-2 text-xs text-muted-foreground">
              {t('components.planetList.classicalNote', {
                defaultValue: 'Exibindo apenas os 7 planetas clássicos da astrologia tradicional',
              })}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground">
            {t('components.planetList.astrologicalInterpretations', {
              defaultValue: 'Interpretações Astrológicas',
            })}
          </h3>

          <div className="space-y-4">
            {CLASSICAL_PLANETS.map((planetKey) => {
              const interpretation = interpretations[planetKey];
              const sources = ragSources?.[planetKey] || [];
              if (!interpretation) return null;

              return (
                <Card key={planetKey}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl" title={translatePlanet(planetKey)}>
                        {getPlanetSymbol(planetKey)}
                      </span>
                      {translatePlanet(planetKey)}
                      {sources.length > 0 && (
                        <Badge
                          variant="outline"
                          className="ml-2 bg-purple-500/10 text-purple-700 dark:text-purple-300 border-purple-500/20"
                        >
                          <BookOpen className="h-3 w-3 mr-1" />
                          {sources.length}{' '}
                          {t('chartDetail.rag.sources', { defaultValue: 'fontes' })}
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                      {interpretation}
                    </p>

                    {/* RAG Sources */}
                    {sources.length > 0 && (
                      <Collapsible>
                        <CollapsibleTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="w-full justify-between text-purple-600 hover:text-purple-700 hover:bg-purple-500/10"
                          >
                            <span className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4" />
                              {t('chartDetail.rag.sources', { defaultValue: 'Fontes RAG' })}
                            </span>
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                        </CollapsibleTrigger>
                        <CollapsibleContent className="mt-2">
                          <div className="space-y-2 p-3 bg-purple-500/5 rounded-lg border border-purple-500/10">
                            <p className="text-xs text-muted-foreground mb-2">
                              {t('chartDetail.rag.sourcesDesc', {
                                defaultValue: 'Documentos usados para esta interpretação',
                              })}
                            </p>
                            {sources.map((source, idx) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between p-2 bg-background rounded border text-xs"
                              >
                                <span className="font-medium text-foreground">{source.source}</span>
                                {source.page && (
                                  <Badge variant="secondary" className="text-xs">
                                    {t('chartDetail.rag.page', { defaultValue: 'Página' })}{' '}
                                    {source.page}
                                  </Badge>
                                )}
                              </div>
                            ))}
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    )}
                  </CardContent>
                </Card>
              );
            })}
            {Object.keys(interpretations).filter((k) => CLASSICAL_PLANETS.includes(k)).length ===
              0 && (
              <p className="text-center text-muted-foreground py-8">
                {t('components.planetList.noInterpretations', {
                  defaultValue: 'Nenhuma interpretação disponível',
                })}
              </p>
            )}
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>
                {t('components.planetList.aboutInterpretations', {
                  defaultValue: 'Sobre as interpretações',
                })}
                :
              </strong>{' '}
              {t('components.planetList.interpretationsDesc', {
                defaultValue:
                  'Geradas por IA baseando-se em princípios de astrologia tradicional (dignidades essenciais, sect). Foco nos 7 planetas clássicos.',
              })}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
