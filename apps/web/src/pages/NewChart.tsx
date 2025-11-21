/**
 * New Birth Chart creation page - Multi-step form
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { chartsService, BirthChartCreate } from '../services/charts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProgressIndicator } from '@/components/ui/progress-indicator';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { AlertCircle, ArrowLeft, ArrowRight, Loader2, MapPin, Check } from 'lucide-react';

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

type ChartFormValues = {
  person_name: string;
  gender?: string;
  birth_datetime: string;
  birth_timezone: string;
  latitude: number;
  longitude: number;
  city: string;
  country?: string;
  notes?: string;
  house_system: string;
  zodiac_type: string;
  node_type: string;
};

export function NewChartPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Zod schema inside component to access t()
  const chartFormSchema = z.object({
    person_name: z.string().min(1, t('validation.required')),
    gender: z.string().optional(),
    birth_datetime: z.string().min(1, t('newChart.invalidDate')),
    birth_timezone: z.string().default('America/Sao_Paulo'),
    latitude: z.coerce.number().min(-90).max(90),
    longitude: z.coerce.number().min(-180).max(180),
    city: z.string().min(1, t('newChart.locationRequired')),
    country: z.string().optional(),
    notes: z.string().optional(),
    house_system: z.string().default('placidus'),
    zodiac_type: z.string().default('tropical'),
    node_type: z.string().default('true'),
  });

  const STEPS = [
    { number: 1, title: t('newChart.step1Title', { defaultValue: 'Informações Pessoais' }), description: t('newChart.step1Desc', { defaultValue: 'Nome e gênero' }) },
    { number: 2, title: t('newChart.step2Title', { defaultValue: 'Data e Hora' }), description: t('newChart.step2Desc', { defaultValue: 'Nascimento' }) },
    { number: 3, title: t('newChart.step3Title', { defaultValue: 'Local' }), description: t('newChart.step3Desc', { defaultValue: 'Cidade e coordenadas' }) },
    { number: 4, title: t('newChart.step4Title', { defaultValue: 'Revisão' }), description: t('newChart.step4Desc', { defaultValue: 'Confirmar dados' }) },
  ];
  const [currentStep, setCurrentStep] = useState(1);

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

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

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
        error instanceof Error ? error.message : t('newChart.error')
      );
    }
  }

  async function validateStep(step: number): Promise<boolean> {
    const fieldsToValidate: Record<number, (keyof ChartFormValues)[]> = {
      1: ['person_name'],
      2: ['birth_datetime', 'birth_timezone'],
      3: ['city', 'latitude', 'longitude'],
      4: [],
    };

    const fields = fieldsToValidate[step];
    if (!fields || fields.length === 0) return true;

    const result = await form.trigger(fields);
    return result;
  }

  async function handleNext() {
    const isValid = await validateStep(currentStep);
    if (isValid && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  }

  function handlePrevious() {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label={t('common.back')}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-3">
            <LanguageSelector />
            <ThemeToggle />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t('common.back')}
            </Button>
          </div>
        </div>
      </nav>

      {/* Form */}
      <div className="max-w-4xl mx-auto py-12 px-4">
        {/* Progress Indicators */}
        <div className="flex justify-center items-center gap-4 mb-12">
          {STEPS.map((step, index) => (
            <div key={step.number} className="flex items-center gap-4">
              <div className="flex flex-col items-center gap-2">
                <ProgressIndicator
                  step={step.number}
                  completed={currentStep > step.number}
                  active={currentStep === step.number}
                />
                <div className="text-center">
                  <p className={`text-sm font-medium ${currentStep >= step.number ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {step.title}
                  </p>
                  <p className="text-xs text-muted-foreground hidden sm:block">
                    {step.description}
                  </p>
                </div>
              </div>
              {index < STEPS.length - 1 && (
                <div className={`h-0.5 w-12 hidden sm:block ${currentStep > step.number ? 'bg-primary' : 'bg-border'}`} />
              )}
            </div>
          ))}
        </div>

        {generalError && (
          <Alert variant="destructive" className="mb-6 animate-slide-in-down">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{generalError}</AlertDescription>
          </Alert>
        )}

        <Card className="shadow-xl border-0 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-h2">
              {STEPS[currentStep - 1].title}
            </CardTitle>
            <CardDescription className="text-base">
              {t('newChart.stepOf', { current: currentStep, total: STEPS.length, defaultValue: `Passo ${currentStep} de ${STEPS.length}` })} - {STEPS[currentStep - 1].description}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Step 1: Personal Information */}
                {currentStep === 1 && (
                  <div className="space-y-6 animate-slide-in-up">
                    <FormField
                      control={form.control}
                      name="person_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base">{t('newChart.personName')} *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder={t('newChart.personNamePlaceholder', { defaultValue: 'João da Silva' })}
                              className="text-base"
                              {...field}
                            />
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
                          <FormLabel className="text-base">{t('newChart.gender')} ({t('common.optional')})</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger className="text-base">
                                <SelectValue placeholder={t('newChart.selectGender', { defaultValue: 'Selecione o gênero' })} />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="Masculino">{t('newChart.genderMale')}</SelectItem>
                              <SelectItem value="Feminino">{t('newChart.genderFemale')}</SelectItem>
                              <SelectItem value="Outro">{t('newChart.genderOther')}</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                {/* Step 2: Birth Date and Time */}
                {currentStep === 2 && (
                  <div className="space-y-6 animate-slide-in-up">
                    <FormField
                      control={form.control}
                      name="birth_datetime"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base">{t('newChart.birthDate')} *</FormLabel>
                          <FormControl>
                            <Input
                              type="datetime-local"
                              className="text-base"
                              {...field}
                            />
                          </FormControl>
                          <p className="text-sm text-muted-foreground">
                            {t('newChart.precisionNote', { defaultValue: 'Quanto mais precisa a hora, mais preciso será o mapa natal' })}
                          </p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="birth_timezone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base">{t('newChart.timezone')}</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger className="text-base">
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
                )}

                {/* Step 3: Birth Location */}
                {currentStep === 3 && (
                  <div className="space-y-6 animate-slide-in-up">
                    {/* City with autocomplete */}
                    <FormField
                      control={form.control}
                      name="city"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base">{t('newChart.birthLocation')} *</FormLabel>
                          <FormControl>
                            <div className="relative" ref={suggestionRef}>
                              <Input
                                {...field}
                                placeholder={t('newChart.searchLocation')}
                                className="text-base"
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
                                <div className="absolute z-10 w-full mt-2 bg-card border border-border rounded-astro-md shadow-xl max-h-80 overflow-y-auto animate-slide-in-down">
                                  {locationSuggestions.map((location, index) => (
                                    <button
                                      key={index}
                                      type="button"
                                      onClick={() => selectLocation(location)}
                                      className="w-full text-left px-4 py-4 hover:bg-accent/40 transition-all duration-200 border-b border-border last:border-b-0 first:rounded-t-astro-md last:rounded-b-astro-md"
                                    >
                                      <div className="flex items-start gap-3">
                                        <MapPin className="h-5 w-5 mt-0.5 text-primary flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                          <p className="text-sm font-semibold text-foreground truncate">
                                            {location.city || location.display_name.split(',')[0]}
                                          </p>
                                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                            {location.display_name}
                                          </p>
                                          <p className="text-xs text-primary/80 mt-1.5 font-mono">
                                            {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
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
                          <FormLabel className="text-base">{t('newChart.country', { defaultValue: 'País' })}</FormLabel>
                          <FormControl>
                            <Input placeholder="Brasil" className="text-base" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="latitude"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-base">{t('newChart.latitude')} *</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                step="0.000001"
                                placeholder="-23.550520"
                                className="text-base font-mono"
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
                            <FormLabel className="text-base">{t('newChart.longitude')} *</FormLabel>
                            <FormControl>
                              <Input
                                type="number"
                                step="0.000001"
                                placeholder="-46.633308"
                                className="text-base font-mono"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <Alert className="border-primary/20 bg-primary/5">
                      <AlertCircle className="h-4 w-4 text-primary" />
                      <AlertDescription className="text-sm">
                        <strong>{t('newChart.important', { defaultValue: 'Importante' })}:</strong> {t('newChart.coordinatesNote', { defaultValue: 'As coordenadas são preenchidas automaticamente ao selecionar uma cidade. Para melhor precisão, use a busca ou ajuste manualmente.' })}
                      </AlertDescription>
                    </Alert>
                  </div>
                )}

                {/* Step 4: Review */}
                {currentStep === 4 && (
                  <div className="space-y-6 animate-slide-in-up">
                    <div className="rounded-astro-md bg-muted/30 p-6 space-y-4">
                      <h3 className="text-h4 mb-4 flex items-center gap-2">
                        <Check className="h-5 w-5 text-primary" />
                        {t('newChart.confirmData', { defaultValue: 'Confirme os dados do mapa natal' })}
                      </h3>

                      <div className="grid gap-4">
                        <div className="flex justify-between items-start py-3 border-b border-border">
                          <span className="text-sm text-muted-foreground">{t('newChart.personName')}</span>
                          <span className="text-sm font-semibold text-right">{form.getValues('person_name') || '-'}</span>
                        </div>

                        {form.getValues('gender') && (
                          <div className="flex justify-between items-start py-3 border-b border-border">
                            <span className="text-sm text-muted-foreground">{t('newChart.gender')}</span>
                            <span className="text-sm font-semibold">{form.getValues('gender')}</span>
                          </div>
                        )}

                        <div className="flex justify-between items-start py-3 border-b border-border">
                          <span className="text-sm text-muted-foreground">{t('chartDetail.birthDateTime')}</span>
                          <span className="text-sm font-semibold text-right font-mono">
                            {form.getValues('birth_datetime')
                              ? new Date(form.getValues('birth_datetime')).toLocaleString('pt-BR')
                              : '-'
                            }
                          </span>
                        </div>

                        <div className="flex justify-between items-start py-3 border-b border-border">
                          <span className="text-sm text-muted-foreground">{t('newChart.timezone')}</span>
                          <span className="text-sm font-semibold">{form.getValues('birth_timezone')}</span>
                        </div>

                        <div className="flex justify-between items-start py-3 border-b border-border">
                          <span className="text-sm text-muted-foreground">{t('newChart.birthLocation')}</span>
                          <span className="text-sm font-semibold text-right">{form.getValues('city') || '-'}</span>
                        </div>

                        {form.getValues('country') && (
                          <div className="flex justify-between items-start py-3 border-b border-border">
                            <span className="text-sm text-muted-foreground">{t('newChart.country', { defaultValue: 'País' })}</span>
                            <span className="text-sm font-semibold">{form.getValues('country')}</span>
                          </div>
                        )}

                        <div className="flex justify-between items-start py-3">
                          <span className="text-sm text-muted-foreground">{t('newChart.coordinates', { defaultValue: 'Coordenadas' })}</span>
                          <span className="text-xs font-mono text-primary">
                            {form.getValues('latitude').toFixed(6)}, {form.getValues('longitude').toFixed(6)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <FormField
                      control={form.control}
                      name="notes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base">{t('newChart.notes')} ({t('common.optional')})</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder={t('newChart.notesPlaceholder', { defaultValue: 'Adicione observações, contexto ou informações adicionais sobre este mapa...' })}
                              rows={4}
                              className="text-base resize-none"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between items-center pt-6 border-t border-border">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentStep === 1}
                    className="gap-2"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    {t('common.previous')}
                  </Button>

                  {currentStep < 4 ? (
                    <Button
                      type="button"
                      onClick={handleNext}
                      className="gap-2"
                    >
                      {t('common.next')}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      type="submit"
                      disabled={form.formState.isSubmitting}
                      className="gap-2 min-w-[200px]"
                    >
                      {form.formState.isSubmitting && (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      )}
                      {form.formState.isSubmitting ? t('newChart.calculating') : t('newChart.submit')}
                      {!form.formState.isSubmitting && <Check className="h-4 w-4" />}
                    </Button>
                  )}
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
