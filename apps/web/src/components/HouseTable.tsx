/**
 * House Table component - displays all 12 houses with their cusps
 */

import { getSignSymbol, formatDMS, isAngularHouse, getHouseType } from '../utils/astro';

// shadcn/ui components
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
  return (
    <div className="space-y-6">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Casa</TableHead>
              <TableHead>Signo na Cúspide</TableHead>
              <TableHead>Posição</TableHead>
              <TableHead className="text-center">Tipo</TableHead>
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
                      {houseType}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Legend */}
      <div className="mt-4 px-4 py-3 bg-muted/30 rounded-md text-xs text-muted-foreground space-y-1">
        <p>
          <strong className="text-foreground">Angular</strong> (1, 4, 7, 10) - Casas de ação e iniciativa
        </p>
        <p>
          <strong className="text-foreground">Succedent</strong> (2, 5, 8, 11) - Casas de recursos e valores
        </p>
        <p>
          <strong className="text-foreground">Cadent</strong> (3, 6, 9, 12) - Casas de aprendizado e adaptação
        </p>
      </div>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Interpretações Astrológicas
          </h3>

          <div className="space-y-4">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
              const interpretation = interpretations[houseNum.toString()];
              if (!interpretation) return null;

              return (
                <div
                  key={houseNum}
                  className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
                >
                  <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                      {houseNum}
                    </span>
                    Casa {houseNum}
                  </h4>
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {interpretation}
                  </p>
                </div>
              );
            })}
            {Object.keys(interpretations).length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                Nenhuma interpretação disponível
              </p>
            )}
          </div>

          <div className="mt-6 bg-muted/30 border border-border rounded-lg p-4">
            <p className="text-xs text-muted-foreground">
              <strong>ℹ️ Sobre as interpretações:</strong> Geradas por IA baseando-se em
              princípios de astrologia tradicional. Interpretações consideram o signo na cúspide
              e significado de cada casa.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
