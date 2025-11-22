/**
 * TimezoneSelect - A searchable timezone selector component
 *
 * Features:
 * - Search by city, country, or timezone ID
 * - Shows popular timezones first
 * - Displays UTC offset
 * - Auto-detection from coordinates
 */

import { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Check, ChevronsUpDown, Globe, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TimezoneInfo {
  id: string;
  name: string;
  region: string;
  offset: string;
  offset_hours: number;
  is_dst: boolean;
  abbreviation: string;
}

interface TimezoneSelectProps {
  value: string;
  onChange: (timezone: string) => void;
  coordinates?: { latitude: number; longitude: number } | null;
  disabled?: boolean;
  placeholder?: string;
}

// Comprehensive list of popular timezones for offline use
const POPULAR_TIMEZONES: TimezoneInfo[] = [
  // Americas
  { id: 'America/New_York', name: 'New York', region: 'Americas', offset: 'UTC-05:00', offset_hours: -5, is_dst: false, abbreviation: 'EST' },
  { id: 'America/Chicago', name: 'Chicago', region: 'Americas', offset: 'UTC-06:00', offset_hours: -6, is_dst: false, abbreviation: 'CST' },
  { id: 'America/Denver', name: 'Denver', region: 'Americas', offset: 'UTC-07:00', offset_hours: -7, is_dst: false, abbreviation: 'MST' },
  { id: 'America/Los_Angeles', name: 'Los Angeles', region: 'Americas', offset: 'UTC-08:00', offset_hours: -8, is_dst: false, abbreviation: 'PST' },
  { id: 'America/Sao_Paulo', name: 'Sao Paulo', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'BRT' },
  { id: 'America/Buenos_Aires', name: 'Buenos Aires', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'ART' },
  { id: 'America/Mexico_City', name: 'Mexico City', region: 'Americas', offset: 'UTC-06:00', offset_hours: -6, is_dst: false, abbreviation: 'CST' },
  { id: 'America/Toronto', name: 'Toronto', region: 'Americas', offset: 'UTC-05:00', offset_hours: -5, is_dst: false, abbreviation: 'EST' },
  { id: 'America/Vancouver', name: 'Vancouver', region: 'Americas', offset: 'UTC-08:00', offset_hours: -8, is_dst: false, abbreviation: 'PST' },
  { id: 'America/Lima', name: 'Lima', region: 'Americas', offset: 'UTC-05:00', offset_hours: -5, is_dst: false, abbreviation: 'PET' },
  { id: 'America/Bogota', name: 'Bogota', region: 'Americas', offset: 'UTC-05:00', offset_hours: -5, is_dst: false, abbreviation: 'COT' },
  { id: 'America/Santiago', name: 'Santiago', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'CLT' },
  // Brazil
  { id: 'America/Manaus', name: 'Manaus', region: 'Americas', offset: 'UTC-04:00', offset_hours: -4, is_dst: false, abbreviation: 'AMT' },
  { id: 'America/Fortaleza', name: 'Fortaleza', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'BRT' },
  { id: 'America/Recife', name: 'Recife', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'BRT' },
  { id: 'America/Bahia', name: 'Bahia', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'BRT' },
  { id: 'America/Cuiaba', name: 'Cuiaba', region: 'Americas', offset: 'UTC-04:00', offset_hours: -4, is_dst: false, abbreviation: 'AMT' },
  { id: 'America/Belem', name: 'Belem', region: 'Americas', offset: 'UTC-03:00', offset_hours: -3, is_dst: false, abbreviation: 'BRT' },
  { id: 'America/Porto_Velho', name: 'Porto Velho', region: 'Americas', offset: 'UTC-04:00', offset_hours: -4, is_dst: false, abbreviation: 'AMT' },
  { id: 'America/Rio_Branco', name: 'Rio Branco', region: 'Americas', offset: 'UTC-05:00', offset_hours: -5, is_dst: false, abbreviation: 'ACT' },
  // Europe
  { id: 'Europe/London', name: 'London', region: 'Europe', offset: 'UTC+00:00', offset_hours: 0, is_dst: false, abbreviation: 'GMT' },
  { id: 'Europe/Paris', name: 'Paris', region: 'Europe', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'CET' },
  { id: 'Europe/Berlin', name: 'Berlin', region: 'Europe', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'CET' },
  { id: 'Europe/Madrid', name: 'Madrid', region: 'Europe', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'CET' },
  { id: 'Europe/Rome', name: 'Rome', region: 'Europe', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'CET' },
  { id: 'Europe/Lisbon', name: 'Lisbon', region: 'Europe', offset: 'UTC+00:00', offset_hours: 0, is_dst: false, abbreviation: 'WET' },
  { id: 'Europe/Amsterdam', name: 'Amsterdam', region: 'Europe', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'CET' },
  { id: 'Europe/Moscow', name: 'Moscow', region: 'Europe', offset: 'UTC+03:00', offset_hours: 3, is_dst: false, abbreviation: 'MSK' },
  { id: 'Europe/Istanbul', name: 'Istanbul', region: 'Europe', offset: 'UTC+03:00', offset_hours: 3, is_dst: false, abbreviation: 'TRT' },
  { id: 'Europe/Athens', name: 'Athens', region: 'Europe', offset: 'UTC+02:00', offset_hours: 2, is_dst: false, abbreviation: 'EET' },
  // Asia
  { id: 'Asia/Tokyo', name: 'Tokyo', region: 'Asia', offset: 'UTC+09:00', offset_hours: 9, is_dst: false, abbreviation: 'JST' },
  { id: 'Asia/Shanghai', name: 'Shanghai', region: 'Asia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'CST' },
  { id: 'Asia/Hong_Kong', name: 'Hong Kong', region: 'Asia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'HKT' },
  { id: 'Asia/Singapore', name: 'Singapore', region: 'Asia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'SGT' },
  { id: 'Asia/Seoul', name: 'Seoul', region: 'Asia', offset: 'UTC+09:00', offset_hours: 9, is_dst: false, abbreviation: 'KST' },
  { id: 'Asia/Dubai', name: 'Dubai', region: 'Asia', offset: 'UTC+04:00', offset_hours: 4, is_dst: false, abbreviation: 'GST' },
  { id: 'Asia/Kolkata', name: 'Kolkata (India)', region: 'Asia', offset: 'UTC+05:30', offset_hours: 5.5, is_dst: false, abbreviation: 'IST' },
  { id: 'Asia/Bangkok', name: 'Bangkok', region: 'Asia', offset: 'UTC+07:00', offset_hours: 7, is_dst: false, abbreviation: 'ICT' },
  { id: 'Asia/Jakarta', name: 'Jakarta', region: 'Asia', offset: 'UTC+07:00', offset_hours: 7, is_dst: false, abbreviation: 'WIB' },
  { id: 'Asia/Manila', name: 'Manila', region: 'Asia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'PST' },
  { id: 'Asia/Kathmandu', name: 'Kathmandu (Nepal)', region: 'Asia', offset: 'UTC+05:45', offset_hours: 5.75, is_dst: false, abbreviation: 'NPT' },
  { id: 'Asia/Taipei', name: 'Taipei', region: 'Asia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'CST' },
  { id: 'Asia/Jerusalem', name: 'Jerusalem', region: 'Asia', offset: 'UTC+02:00', offset_hours: 2, is_dst: false, abbreviation: 'IST' },
  // Australia & Pacific
  { id: 'Australia/Sydney', name: 'Sydney', region: 'Australia', offset: 'UTC+11:00', offset_hours: 11, is_dst: true, abbreviation: 'AEDT' },
  { id: 'Australia/Melbourne', name: 'Melbourne', region: 'Australia', offset: 'UTC+11:00', offset_hours: 11, is_dst: true, abbreviation: 'AEDT' },
  { id: 'Australia/Perth', name: 'Perth', region: 'Australia', offset: 'UTC+08:00', offset_hours: 8, is_dst: false, abbreviation: 'AWST' },
  { id: 'Australia/Brisbane', name: 'Brisbane', region: 'Australia', offset: 'UTC+10:00', offset_hours: 10, is_dst: false, abbreviation: 'AEST' },
  { id: 'Pacific/Auckland', name: 'Auckland', region: 'Pacific', offset: 'UTC+13:00', offset_hours: 13, is_dst: true, abbreviation: 'NZDT' },
  { id: 'Pacific/Honolulu', name: 'Honolulu', region: 'Pacific', offset: 'UTC-10:00', offset_hours: -10, is_dst: false, abbreviation: 'HST' },
  { id: 'Pacific/Fiji', name: 'Fiji', region: 'Pacific', offset: 'UTC+12:00', offset_hours: 12, is_dst: false, abbreviation: 'FJT' },
  // Africa
  { id: 'Africa/Cairo', name: 'Cairo', region: 'Africa', offset: 'UTC+02:00', offset_hours: 2, is_dst: false, abbreviation: 'EET' },
  { id: 'Africa/Johannesburg', name: 'Johannesburg', region: 'Africa', offset: 'UTC+02:00', offset_hours: 2, is_dst: false, abbreviation: 'SAST' },
  { id: 'Africa/Lagos', name: 'Lagos', region: 'Africa', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'WAT' },
  { id: 'Africa/Nairobi', name: 'Nairobi', region: 'Africa', offset: 'UTC+03:00', offset_hours: 3, is_dst: false, abbreviation: 'EAT' },
  { id: 'Africa/Casablanca', name: 'Casablanca', region: 'Africa', offset: 'UTC+01:00', offset_hours: 1, is_dst: false, abbreviation: 'WEST' },
  // UTC
  { id: 'UTC', name: 'UTC (Coordinated Universal Time)', region: 'Other', offset: 'UTC+00:00', offset_hours: 0, is_dst: false, abbreviation: 'UTC' },
];

// Group timezones by region
const groupTimezones = (timezones: TimezoneInfo[]): Record<string, TimezoneInfo[]> => {
  return timezones.reduce((acc, tz) => {
    if (!acc[tz.region]) {
      acc[tz.region] = [];
    }
    acc[tz.region].push(tz);
    return acc;
  }, {} as Record<string, TimezoneInfo[]>);
};

export function TimezoneSelect({
  value,
  onChange,
  coordinates,
  disabled = false,
  placeholder,
}: TimezoneSelectProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [timezones] = useState<TimezoneInfo[]>(POPULAR_TIMEZONES);
  const [detectedTimezone, setDetectedTimezone] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);

  // Group timezones by region
  const groupedTimezones = useMemo(() => groupTimezones(timezones), [timezones]);

  // Filter timezones based on search
  const filteredTimezones = useMemo(() => {
    if (!searchQuery) return groupedTimezones;

    const query = searchQuery.toLowerCase();
    const filtered = timezones.filter(
      (tz) =>
        tz.name.toLowerCase().includes(query) ||
        tz.id.toLowerCase().includes(query) ||
        tz.region.toLowerCase().includes(query) ||
        tz.abbreviation.toLowerCase().includes(query)
    );
    return groupTimezones(filtered);
  }, [timezones, searchQuery, groupedTimezones]);

  // Get selected timezone info
  const selectedTimezone = useMemo(
    () => timezones.find((tz) => tz.id === value),
    [timezones, value]
  );

  // Auto-detect timezone from coordinates
  useEffect(() => {
    if (coordinates && coordinates.latitude !== 0 && coordinates.longitude !== 0) {
      setDetecting(true);
      fetch(`${API_URL}/api/v1/timezones/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: coordinates.latitude,
          longitude: coordinates.longitude,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.detected && data.timezone_id) {
            setDetectedTimezone(data.timezone_id);
            // Auto-select if no value is set or if it's the default
            if (!value || value === 'America/Sao_Paulo') {
              onChange(data.timezone_id);
            }
          }
        })
        .catch((err) => {
          console.warn('Failed to detect timezone:', err);
        })
        .finally(() => {
          setDetecting(false);
        });
    }
  }, [coordinates, onChange, value]);

  // Format display string
  const formatTimezone = (tz: TimezoneInfo) => {
    return `${tz.name} (${tz.offset})`;
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className="w-full justify-between text-base font-normal"
        >
          {detecting ? (
            <span className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t('newChart.detectingTimezone', 'Detecting timezone...')}
            </span>
          ) : selectedTimezone ? (
            <span className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-muted-foreground" />
              {formatTimezone(selectedTimezone)}
            </span>
          ) : (
            <span className="text-muted-foreground">
              {placeholder || t('newChart.selectTimezone', 'Select timezone...')}
            </span>
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder={t('newChart.searchTimezone', 'Search timezone...')}
            value={searchQuery}
            onValueChange={setSearchQuery}
          />
          <CommandList className="max-h-[300px]">
            <CommandEmpty>{t('newChart.noTimezoneFound', 'No timezone found.')}</CommandEmpty>

            {/* Show detected timezone suggestion */}
            {detectedTimezone && detectedTimezone !== value && (
              <CommandGroup heading={t('newChart.suggested', 'Suggested')}>
                <CommandItem
                  value={detectedTimezone}
                  onSelect={() => {
                    onChange(detectedTimezone);
                    setOpen(false);
                    setSearchQuery('');
                  }}
                >
                  <Check
                    className={cn(
                      'mr-2 h-4 w-4',
                      value === detectedTimezone ? 'opacity-100' : 'opacity-0'
                    )}
                  />
                  <span className="flex-1">
                    {timezones.find((tz) => tz.id === detectedTimezone)?.name || detectedTimezone}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {t('newChart.detectedFromLocation', 'Detected from location')}
                  </span>
                </CommandItem>
              </CommandGroup>
            )}

            {/* Grouped timezones */}
            {Object.entries(filteredTimezones).map(([region, tzList]) => (
              <CommandGroup key={region} heading={region}>
                {tzList.map((tz) => (
                  <CommandItem
                    key={tz.id}
                    value={tz.id}
                    onSelect={() => {
                      onChange(tz.id);
                      setOpen(false);
                      setSearchQuery('');
                    }}
                  >
                    <Check
                      className={cn(
                        'mr-2 h-4 w-4',
                        value === tz.id ? 'opacity-100' : 'opacity-0'
                      )}
                    />
                    <span className="flex-1">{tz.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {tz.offset}
                      {tz.is_dst && ' (DST)'}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
            ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export default TimezoneSelect;
