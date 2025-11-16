/**
 * New Birth Chart creation page
 */

import { useState, FormEvent, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { chartsService, BirthChartCreate } from '../services/charts';

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

export function NewChartPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<BirthChartCreate>({
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
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
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
    setFormData({ ...formData, city: value });

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
    setFormData({
      ...formData,
      city: location.city || location.display_name.split(',')[0],
      country: location.country,
      latitude: location.latitude,
      longitude: location.longitude,
    });
    setShowSuggestions(false);
    setLocationSuggestions([]);
  }

  function validateForm(): boolean {
    const newErrors: Record<string, string> = {};

    if (!formData.person_name) {
      newErrors.person_name = 'Nome é obrigatório';
    }

    if (!formData.birth_datetime) {
      newErrors.birth_datetime = 'Data e hora de nascimento são obrigatórias';
    }

    if (!formData.city) {
      newErrors.city = 'Cidade é obrigatória';
    }

    if (formData.latitude === 0 && formData.longitude === 0) {
      newErrors.location = 'Localização é obrigatória (latitude/longitude)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        navigate('/login');
        return;
      }

      await chartsService.create(formData, token);
      navigate('/charts');
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : 'Erro ao criar mapa natal'
      );
    } finally {
      setIsLoading(false);
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

  function handleCitySelect(e: React.ChangeEvent<HTMLSelectElement>) {
    const cityData = brazilianCities.find(c => c.name === e.target.value);
    if (cityData) {
      setFormData({
        ...formData,
        city: cityData.name.split(',')[0],
        country: 'Brasil',
        latitude: cityData.lat,
        longitude: cityData.lon,
      });
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
          <button
            onClick={() => navigate('/dashboard')}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            ← Voltar
          </button>
        </div>
      </nav>

      {/* Form */}
      <div className="max-w-4xl mx-auto py-8 px-4">
        {generalError && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
            <p className="text-sm text-destructive">{generalError}</p>
          </div>
        )}

        <div className="bg-card border border-border rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Person Information */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-foreground">
                Informações da Pessoa
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Nome Completo *
                  </label>
                  <input
                    type="text"
                    value={formData.person_name}
                    onChange={(e) =>
                      setFormData({ ...formData, person_name: e.target.value })
                    }
                    className={`w-full px-4 py-2 bg-background border ${
                      errors.person_name ? 'border-destructive' : 'border-input'
                    } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                    placeholder="João da Silva"
                  />
                  {errors.person_name && (
                    <p className="mt-1 text-sm text-destructive">
                      {errors.person_name}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Gênero
                  </label>
                  <select
                    value={formData.gender || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, gender: e.target.value })
                    }
                    className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">Selecione</option>
                    <option value="Masculino">Masculino</option>
                    <option value="Feminino">Feminino</option>
                    <option value="Outro">Outro</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Birth Date and Time */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-foreground">
                Data e Hora de Nascimento
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Data e Hora *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.birth_datetime}
                    onChange={(e) =>
                      setFormData({ ...formData, birth_datetime: e.target.value })
                    }
                    className={`w-full px-4 py-2 bg-background border ${
                      errors.birth_datetime ? 'border-destructive' : 'border-input'
                    } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                  />
                  {errors.birth_datetime && (
                    <p className="mt-1 text-sm text-destructive">
                      {errors.birth_datetime}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Fuso Horário
                  </label>
                  <select
                    value={formData.birth_timezone}
                    onChange={(e) =>
                      setFormData({ ...formData, birth_timezone: e.target.value })
                    }
                    className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="America/Sao_Paulo">América/São Paulo (BRT)</option>
                    <option value="America/Manaus">América/Manaus (AMT)</option>
                    <option value="America/Fortaleza">América/Fortaleza (BRT)</option>
                    <option value="America/Recife">América/Recife (BRT)</option>
                    <option value="America/Bahia">América/Bahia (BRT)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Birth Location */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-foreground">
                Local de Nascimento
              </h2>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Cidade Rápida (Capitais Brasileiras)
                </label>
                <select
                  onChange={handleCitySelect}
                  className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Selecione uma capital</option>
                  {brazilianCities.map((city) => (
                    <option key={city.name} value={city.name}>
                      {city.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative" ref={suggestionRef}>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Cidade *
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={formData.city || ''}
                      onChange={(e) => handleCityInputChange(e.target.value)}
                      onFocus={() => {
                        if (locationSuggestions.length > 0) {
                          setShowSuggestions(true);
                        }
                      }}
                      className={`w-full px-4 py-2 bg-background border ${
                        errors.city ? 'border-destructive' : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                      placeholder="Digite o nome da cidade..."
                      autoComplete="off"
                    />
                    {searchingLocation && (
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                      </div>
                    )}
                  </div>

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
                            <span className="text-lg">📍</span>
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

                  {errors.city && (
                    <p className="mt-1 text-sm text-destructive">{errors.city}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    País
                  </label>
                  <input
                    type="text"
                    value={formData.country || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, country: e.target.value })
                    }
                    className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Brasil"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Latitude *
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    value={formData.latitude}
                    onChange={(e) =>
                      setFormData({ ...formData, latitude: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="-23.550520"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Longitude *
                  </label>
                  <input
                    type="number"
                    step="0.000001"
                    value={formData.longitude}
                    onChange={(e) =>
                      setFormData({ ...formData, longitude: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="-46.633308"
                  />
                </div>
              </div>

              {errors.location && (
                <p className="text-sm text-destructive">{errors.location}</p>
              )}
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Anotações
              </label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                rows={3}
                className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Notas adicionais sobre este mapa..."
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-md hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              {isLoading ? 'Calculando mapa natal...' : 'Criar Mapa Natal'}
            </button>
          </form>
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-muted/50 rounded-md">
          <p className="text-sm text-muted-foreground">
            <strong>Dica:</strong> Para melhor precisão, use as coordenadas exatas do
            local de nascimento. Você pode selecionar uma capital brasileira ou inserir
            manualmente as coordenadas.
          </p>
        </div>
      </div>
    </div>
  );
}
