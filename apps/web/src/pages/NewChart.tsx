/**
 * New Birth Chart creation page
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { chartsService, BirthChartCreate } from '../services/charts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, ArrowLeft, Loader2, MapPin } from 'lucide-react';

const TOKEN_KEY = 'astro_access_token';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface LocationSuggestion {
  display_name: string;
  latitude: number;
  longitude: number;
  city: string;
  country: string;
  country_code: string;
}

const chartFormSchema = z.object({
  person_name: z.string().min(1, 'Nome é obrigatório'),
  gender: z.string().optional(),
  birth_datetime: z.string().min(1, 'Data e hora de nascimento são obrigatórias'),
  birth_timezone: z.string().default('America/Sao_Paulo'),
  latitude: z.coerce.number().min(-90).max(90),
  longitude: z.coerce.number().min(-180).max(180),
  city: z.string().min(1, 'Cidade é obrigatória'),
  country: z.string().optional(),
  notes: z.string().optional(),
  house_system: z.string().default('placidus'),
  zodiac_type: z.string().default('tropical'),
  node_type: z.string().default('true'),
});

type ChartFormValues = z.infer<typeof chartFormSchema>;

export function NewChartPage() {
  const navigate = useNavigate();

  const form = useForm<ChartFormValues>({
    resolver: zodResolver(chartFormSchema),
    defaultValues: {
      person_name: '',
      gender: '',
      birth_datetime: '',
      birth_timezone: 'America/Sao_Paulo',
      latitude: 0,
      longitude: 0,
      city: '',
      country: '',
      notes: '',
      house_system: 'placidus',
      zodiac_type: 'tropical',
      node_type: 'true',
    },
  });

  const [generalError, setGeneralError] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState<LocationSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchingLocation, setSearchingLocation] = useState(false);
  const searchTimeoutRef = useRef<number | null>(null);
  const suggestionRef = useRef<HTMLDivElement>(null);

  // Close suggestions when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (suggestionRef.current && !suggestionRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  async function searchLocation(query: string) {
    if (query.length < 3) {
      setLocationSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setSearchingLocation(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geocoding/search?q=${encodeURIComponent(query)}&limit=5`
      );

      if (response.ok) {
        const suggestions: LocationSuggestion[] = await response.json();
        setLocationSuggestions(suggestions);
        setShowSuggestions(suggestions.length > 0);
      }
    } catch (error) {
      console.error('Error searching location:', error);
    } finally {
      setSearchingLocation(false);
    }
  }

  function handleCityInputChange(value: string) {
    form.setValue('city', value);

    // Clear timeout if exists
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Debounce search
    searchTimeoutRef.current = setTimeout(() => {
      searchLocation(value);
    }, 500);
  }

  function selectLocation(location: LocationSuggestion) {
    form.setValue('city', location.city || location.display_name.split(',')[0]);
    form.setValue('country', location.country);
    form.setValue('latitude', location.latitude);
    form.setValue('longitude', location.longitude);
    setShowSuggestions(false);
    setLocationSuggestions([]);
  }

  async function onSubmit(values: ChartFormValues) {
    setGeneralError('');

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        navigate('/login');
        return;
      }

      await chartsService.create(values as BirthChartCreate, token);
      navigate('/charts');
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : 'Erro ao criar mapa natal'
      );
    }
  }

  // Brazilian state capitals for quick selection
  const brazilianCities = [
    { name: 'São Paulo, SP', lat: -23.550520, lon: -46.633308 },
    { name: 'Rio de Janeiro, RJ', lat: -22.906847, lon: -43.172896 },
    { name: 'Brasília, DF', lat: -15.826691, lon: -47.921822 },
    { name: 'Salvador, BA', lat: -12.971598, lon: -38.501297 },
    { name: 'Fortaleza, CE', lat: -3.731862, lon: -38.526669 },
    { name: 'Belo Horizonte, MG', lat: -19.916681, lon: -43.934493 },
    { name: 'Curitiba, PR', lat: -25.428954, lon: -49.267137 },
    { name: 'Recife, PE', lat: -8.047562, lon: -34.877001 },
    { name: 'Porto Alegre, RS', lat: -30.034647, lon: -51.217659 },
  ];

  function handleCitySelect(value: string) {
    const cityData = brazilianCities.find(c => c.name === value);
    if (cityData) {
      form.setValue('city', cityData.name.split(',')[0]);
      form.setValue('country', 'Brasil');
      form.setValue('latitude', cityData.lat);
      form.setValue('longitude', cityData.lon);
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label="Voltar ao Dashboard"
          >
            <img
              src="/logo.png"
              alt="Astro"
              className="h-8 w-8"
            />
            <h1 className="text-2xl font-bold text-foreground">Astro</h1>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar
          </Button>
        </div>
      </nav>

      {/* Form */}
      <div className="max-w-4xl mx-auto py-8 px-4">
        {generalError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{generalError}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Criar Novo Mapa Natal</CardTitle>
            <CardDescription>
              Preencha os dados abaixo para calcular um novo mapa natal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Person Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Informações da Pessoa</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="person_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Nome Completo *</FormLabel>
                          <FormControl>
                            <Input placeholder="João da Silva" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="gender"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Gênero</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="Masculino">Masculino</SelectItem>
                              <SelectItem value="Feminino">Feminino</SelectItem>
                              <SelectItem value="Outro">Outro</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Birth Date and Time */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Data e Hora de Nascimento</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="birth_datetime"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Data e Hora *</FormLabel>
                          <FormControl>
                            <Input type="datetime-local" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="birth_timezone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Fuso Horário</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="America/Sao_Paulo">América/São Paulo (BRT)</SelectItem>
                              <SelectItem value="America/Manaus">América/Manaus (AMT)</SelectItem>
                              <SelectItem value="America/Fortaleza">América/Fortaleza (BRT)</SelectItem>
                              <SelectItem value="America/Recife">América/Recife (BRT)</SelectItem>
                              <SelectItem value="America/Bahia">América/Bahia (BRT)</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Birth Location */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Local de Nascimento</h3>

                  {/* Quick City Select */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      Cidade Rápida (Capitais Brasileiras)
                    </label>
                    <Select onValueChange={handleCitySelect}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma capital" />
                      </SelectTrigger>
                      <SelectContent>
                        {brazilianCities.map((city) => (
                          <SelectItem key={city.name} value={city.name}>
                            {city.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* City with autocomplete */}
                    <FormField
                      control={form.control}
                      name="city"
                      render={({ field }) => (
                        <FormItem className="relative">
                          <FormLabel>Cidade *</FormLabel>
                          <FormControl>
                            <div className="relative" ref={suggestionRef}>
                              <Input
                                {...field}
                                placeholder="Digite o nome da cidade..."
                                onChange={(e) => {
                                  field.onChange(e);
                                  handleCityInputChange(e.target.value);
                                }}
                                onFocus={() => {
                                  if (locationSuggestions.length > 0) {
                                    setShowSuggestions(true);
                                  }
                                }}
                                autoComplete="off"
                              />
                              {searchingLocation && (
                                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                </div>
                              )}

                              {/* Location Suggestions Dropdown */}
                              {showSuggestions && locationSuggestions.length > 0 && (
                                <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg max-h-60 overflow-y-auto">
                                  {locationSuggestions.map((location, index) => (
                                    <button
                                      key={index}
                                      type="button"
                                      onClick={() => selectLocation(location)}
                                      className="w-full text-left px-4 py-3 hover:bg-muted transition-colors border-b border-border last:border-b-0"
                                    >
                                      <div className="flex items-start gap-2">
                                        <MapPin className="h-4 w-4 mt-1 text-muted-foreground" />
                                        <div className="flex-1">
                                          <p className="text-sm font-medium text-foreground">
                                            {location.city || location.display_name.split(',')[0]}
                                          </p>
                                          <p className="text-xs text-muted-foreground mt-0.5">
                                            {location.display_name}
                                          </p>
                                          <p className="text-xs text-muted-foreground mt-1">
                                            📌 {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                                          </p>
                                        </div>
                                      </div>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="country"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>País</FormLabel>
                          <FormControl>
                            <Input placeholder="Brasil" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="latitude"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Latitude *</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              step="0.000001"
                              placeholder="-23.550520"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="longitude"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Longitude *</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              step="0.000001"
                              placeholder="-46.633308"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Notes */}
                <FormField
                  control={form.control}
                  name="notes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Anotações</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Notas adicionais sobre este mapa..."
                          rows={3}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={form.formState.isSubmitting}
                >
                  {form.formState.isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {form.formState.isSubmitting ? 'Calculando mapa natal...' : 'Criar Mapa Natal'}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        {/* Info Box */}
        <Alert className="mt-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Dica:</strong> Para melhor precisão, use as coordenadas exatas do
            local de nascimento. Você pode selecionar uma capital brasileira ou inserir
            manualmente as coordenadas.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}
