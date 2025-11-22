/**
 * House Table component - displays all 12 houses with their cusps
 */

import { useTranslation } from 'react-i18next';
import { getSignSymbol, formatDMS, isAngularHouse, getHouseType } from '../utils/astro';

// shadcn/ui components
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';

export interface HousePosition {
  house: number;
  longitude: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
}

interface HouseTableProps {
  houses: HousePosition[];
  interpretations?: Record<string, string>;
}

export function HouseTable({
  houses,
  interpretations,
}: HouseTableProps) {
  const { t } = useTranslation();

  // Translation function for house types
  const getHouseTypeTranslated = (type: string) => {
    const typeMap: Record<string, string> = {
      'Angular': t('components.houseTable.angular', { defaultValue: 'Angular' }),
      'Succedent': t('components.houseTable.succedent', { defaultValue: 'Sucedente' }),
      'Cadent': t('components.houseTable.cadent', { defaultValue: 'Cadente' }),
    };
    return typeMap[type] || type;
  };

  return (
    <div className="space-y-6">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t('components.houseTable.house', { defaultValue: 'Casa' })}</TableHead>
              <TableHead>{t('components.houseTable.signOnCusp', { defaultValue: 'Signo na Cúspide' })}</TableHead>
              <TableHead>{t('components.houseTable.position', { defaultValue: 'Posição' })}</TableHead>
              <TableHead className="text-center">{t('components.houseTable.type', { defaultValue: 'Tipo' })}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {houses.map((house) => {
              const angular = isAngularHouse(house.house);
              const houseType = getHouseType(house.house);

              return (
                <TableRow key={house.house} className={angular ? 'font-semibold' : ''}>
                  {/* House Number */}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center justify-center w-9 h-9 rounded-full text-sm ${
                          angular
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {house.house}
                      </span>
                      {angular && (
                        <span className="text-xs text-primary">●</span>
                      )}
                    </div>
                  </TableCell>

                  {/* Sign on Cusp with Symbol */}
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="text-xl" title={house.sign}>
                        {getSignSymbol(house.sign)}
                      </span>
                      <span className={angular ? 'text-foreground' : 'text-muted-foreground'}>
                        {house.sign}
                      </span>
                    </div>
                  </TableCell>

                  {/* Position (Degree, Minute, Second) */}
                  <TableCell>
                    <span className={`font-mono ${angular ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {formatDMS(house.degree, house.minute, house.second)}
                    </span>
                  </TableCell>

                  {/* House Type */}
                  <TableCell className="text-center">
                    <Badge
                      variant={
                        houseType === 'Angular'
                          ? 'default'
                          : houseType === 'Succedent'
                          ? 'secondary'
                          : 'outline'
                      }
                    >
                      {getHouseTypeTranslated(houseType)}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t('components.houseTable.houseTypes', { defaultValue: 'Tipos de Casas' })}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <Badge>{t('components.houseTable.angular', { defaultValue: 'Angular' })}</Badge>
            <span className="text-muted-foreground">(1, 4, 7, 10) - {t('components.houseTable.angularDesc', { defaultValue: 'Casas de ação e iniciativa' })}</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{t('components.houseTable.succedent', { defaultValue: 'Sucedente' })}</Badge>
            <span className="text-muted-foreground">(2, 5, 8, 11) - {t('components.houseTable.succedentDesc', { defaultValue: 'Casas de recursos e valores' })}</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{t('components.houseTable.cadent', { defaultValue: 'Cadente' })}</Badge>
            <span className="text-muted-foreground">(3, 6, 9, 12) - {t('components.houseTable.cadentDesc', { defaultValue: 'Casas de aprendizado e adaptação' })}</span>
          </div>
        </CardContent>
      </Card>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground">
            {t('components.houseTable.astrologicalInterpretations', { defaultValue: 'Interpretações Astrológicas' })}
          </h3>

          <div className="space-y-4">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
              const interpretation = interpretations[houseNum.toString()];
              if (!interpretation) return null;

              return (
                <Card key={houseNum}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                        {houseNum}
                      </span>
                      {t('components.houseTable.houseNumber', { defaultValue: 'Casa {{num}}', num: houseNum })}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                      {interpretation}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
            {Object.keys(interpretations).length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                {t('components.houseTable.noInterpretations', { defaultValue: 'Nenhuma interpretação disponível' })}
              </p>
            )}
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>{t('components.houseTable.aboutInterpretations', { defaultValue: 'Sobre as interpretações' })}:</strong> {t('components.houseTable.interpretationsDesc', { defaultValue: 'Geradas por IA baseando-se em princípios de astrologia tradicional. Interpretações consideram o signo na cúspide e significado de cada casa.' })}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
