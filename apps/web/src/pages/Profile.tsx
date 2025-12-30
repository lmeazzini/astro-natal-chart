/**
 * User profile and settings page
 */

import { useState, useEffect } from 'react';
import { useNavigate, Navigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { amplitudeService } from '../services/amplitude';
import {
  userService,
  UserStats,
  UserActivity,
  OAuthConnection,
  UserUpdate,
  UserType,
} from '../services/users';
import { NavActions } from '../components/NavActions';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';

// User type options - values only, labels from translation
const USER_TYPE_VALUES = ['professional', 'student', 'curious'] as const;

// Type definitions (outside component to maintain type consistency)
type ProfileFormValues = {
  full_name: string;
  bio?: string;
  locale: string;
  timezone: string;
  profile_public: boolean;
  user_type?: string;
  website?: string;
  instagram?: string;
  twitter?: string;
  location?: string;
  professional_since?: number | null;
  specializations?: string[];
};

type PasswordFormValues = {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
};

// Available timezones
const TIMEZONES = [
  { value: 'America/Sao_Paulo', label: 'São Paulo (GMT-3)' },
  { value: 'America/New_York', label: 'New York (GMT-5)' },
  { value: 'Europe/London', label: 'London (GMT+0)' },
  { value: 'Europe/Paris', label: 'Paris (GMT+1)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (GMT+9)' },
  { value: 'Australia/Sydney', label: 'Sydney (GMT+11)' },
];

const LOCALES = [
  { value: 'pt-BR', label: 'Português (Brasil)' },
  { value: 'en-US', label: 'English (US)' },
];

export function ProfilePage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, setUser, logout, isLoading: authLoading } = useAuth();

  // Form schemas (inside component to access t())
  const profileFormSchema = z.object({
    full_name: z.string().min(3, t('validation.minLength', { min: 3 })),
    bio: z
      .string()
      .max(500, t('validation.maxLength', { max: 500 }))
      .optional(),
    locale: z.string(),
    timezone: z.string(),
    profile_public: z.boolean(),
  });

  const passwordFormSchema = z
    .object({
      current_password: z.string().min(1, t('validation.required')),
      new_password: z
        .string()
        .min(8, t('auth.register.passwordMinLength'))
        .regex(
          /[A-Z]/,
          t('validation.passwordUppercase', {
            defaultValue: 'Password must contain at least one uppercase letter',
          })
        )
        .regex(
          /[a-z]/,
          t('validation.passwordLowercase', {
            defaultValue: 'Password must contain at least one lowercase letter',
          })
        )
        .regex(
          /[0-9]/,
          t('validation.passwordNumber', {
            defaultValue: 'Password must contain at least one number',
          })
        )
        .regex(
          /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/,
          t('validation.passwordSpecial', {
            defaultValue: 'Password must contain at least one special character',
          })
        ),
      new_password_confirm: z.string().min(1, t('validation.required')),
    })
    .refine((data) => data.new_password === data.new_password_confirm, {
      message: t('validation.passwordMismatch'),
      path: ['new_password_confirm'],
    });

  const [activeTab, setActiveTab] = useState<string>('profile');
  const [stats, setStats] = useState<UserStats | null>(null);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [oauthConnections, setOAuthConnections] = useState<OAuthConnection[]>([]);
  const [dataLoading, setDataLoading] = useState(false);

  // Form states
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState('');
  const [profileError, setProfileError] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // Profile form
  const profileForm = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      full_name: '',
      bio: '',
      locale: 'pt-BR',
      timezone: 'America/Sao_Paulo',
      profile_public: false,
      user_type: 'curious',
      website: '',
      instagram: '',
      twitter: '',
      location: '',
      professional_since: null,
      specializations: [],
    },
  });

  // Password form
  const passwordForm = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      new_password_confirm: '',
    },
  });

  // Load user data
  useEffect(() => {
    if (user) {
      profileForm.reset({
        full_name: user.full_name || '',
        bio: user.bio || '',
        locale: user.locale || 'pt-BR',
        timezone: user.timezone || 'America/Sao_Paulo',
        profile_public: user.profile_public || false,
        user_type: user.user_type || 'curious',
        website: user.website || '',
        instagram: user.instagram || '',
        twitter: user.twitter || '',
        location: user.location || '',
        professional_since: user.professional_since || null,
        specializations: user.specializations || [],
      });
    }
  }, [user, profileForm]);

  // Load stats, activities, and OAuth connections
  useEffect(() => {
    if (user && (activeTab === 'security' || activeTab === 'privacy')) {
      loadSecurityData();
    }
  }, [user, activeTab]);

  // Track profile page view
  useEffect(() => {
    amplitudeService.track('profile_viewed', { source: 'profile_page' });
  }, []);

  async function loadSecurityData() {
    const token = localStorage.getItem('astro_access_token');
    if (!token) return;

    setDataLoading(true);
    try {
      const [statsData, activitiesData, oauthData] = await Promise.all([
        userService.getStats(token),
        userService.getActivity(token, 20, 0),
        userService.getOAuthConnections(token),
      ]);

      setStats(statsData);
      setActivities(activitiesData.activities);
      setOAuthConnections(oauthData);
    } catch (error) {
      console.error('Failed to load security data:', error);
    } finally {
      setDataLoading(false);
    }
  }

  // Handle profile submit
  async function onProfileSubmit(data: ProfileFormValues) {
    setProfileError('');
    setProfileSuccess('');
    setProfileLoading(true);

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) throw new Error('Not authenticated');

      // Cast user_type from string to UserType for type safety
      const updateData: UserUpdate = {
        ...data,
        user_type: data.user_type as UserType | undefined,
      };

      const updatedUser = await userService.updateProfile(updateData, token);

      // Sync i18n if locale changed
      if (data.locale && data.locale !== i18n.language) {
        await i18n.changeLanguage(data.locale);
        localStorage.setItem('astro_language', data.locale);
      }

      setUser(updatedUser);
      setProfileSuccess(t('profile.success'));
      // Note: profile_updated event is tracked by backend API

      setTimeout(() => setProfileSuccess(''), 5000);
    } catch (error) {
      setProfileError(error instanceof Error ? error.message : t('profile.error'));
    } finally {
      setProfileLoading(false);
    }
  }

  // Handle password change
  async function onPasswordSubmit(data: PasswordFormValues) {
    setPasswordError('');
    setPasswordSuccess('');
    setPasswordLoading(true);

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) throw new Error('Not authenticated');

      await userService.changePassword(
        {
          current_password: data.current_password,
          new_password: data.new_password,
          new_password_confirm: data.new_password_confirm,
        },
        token
      );

      setPasswordSuccess(t('profile.passwordSuccess'));
      passwordForm.reset();
      // Note: profile_password_changed event is tracked by backend API

      setTimeout(() => setPasswordSuccess(''), 5000);
    } catch (error) {
      // Note: profile_password_change_failed event is tracked by backend API
      setPasswordError(error instanceof Error ? error.message : t('profile.passwordError'));
    } finally {
      setPasswordLoading(false);
    }
  }

  // Handle data export
  async function handleExportData() {
    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      const data = await userService.exportData(token);
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `real-astrology-data-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      alert(t('profile.privacy.exportError', { defaultValue: 'Error exporting data' }));
    }
  }

  // Handle account deletion
  async function handleDeleteAccount() {
    const password = prompt(
      t('profile.privacy.confirmPasswordPrompt', {
        defaultValue: 'Enter your password to confirm account deletion:',
      })
    );
    if (!password) return;

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      await userService.deleteAccount(token);
      // Note: account_deletion_requested event is tracked by backend API

      logout();
      navigate('/');
    } catch (error) {
      alert(t('profile.deleteError'));
    }
  }

  // Handle disconnect OAuth
  async function handleDisconnectOAuth(provider: string) {
    const token = localStorage.getItem('astro_access_token');
    if (!token) return;

    try {
      await userService.disconnectOAuth(provider, token);
      setOAuthConnections(oauthConnections.filter((conn) => conn.provider !== provider));
      // Note: oauth_connection_removed event is tracked by backend API
    } catch (error) {
      alert(t('profile.security.disconnectError', { defaultValue: 'Error disconnecting OAuth' }));
    }
  }

  // Format date based on current locale
  function formatDate(date: string | Date) {
    const locale = i18n.language || 'pt-BR';
    return new Date(date).toLocaleDateString(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">{t('common.loading')}</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label={t('common.back')}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">{t('profile.title')}</h1>
          </Link>
          <div className="flex items-center gap-3">
            <NavActions />
            <Button variant="ghost" onClick={() => navigate('/dashboard')}>
              ← {t('profile.backToDashboard', { defaultValue: 'Back to Dashboard' })}
            </Button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-6xl mx-auto py-8 px-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
            <TabsTrigger value="profile">
              {t('profile.tabs.profile', { defaultValue: 'Profile' })}
            </TabsTrigger>
            <TabsTrigger value="password">
              {t('profile.tabs.password', { defaultValue: 'Password' })}
            </TabsTrigger>
            <TabsTrigger value="security">
              {t('profile.tabs.security', { defaultValue: 'Security' })}
            </TabsTrigger>
            <TabsTrigger value="privacy">
              {t('profile.tabs.privacy', { defaultValue: 'Privacy' })}
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>{t('profile.personalInfo')}</CardTitle>
                <CardDescription>{t('profile.subtitle')}</CardDescription>
              </CardHeader>
              <CardContent>
                {profileSuccess && (
                  <Alert className="mb-4">
                    <AlertDescription className="text-green-600">{profileSuccess}</AlertDescription>
                  </Alert>
                )}

                {profileError && (
                  <Alert variant="destructive" className="mb-4">
                    <AlertDescription>{profileError}</AlertDescription>
                  </Alert>
                )}

                <Form {...profileForm}>
                  <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-4">
                    <FormField
                      control={profileForm.control}
                      name="full_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t('profile.name')} *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder={t('profile.namePlaceholder', {
                                defaultValue: 'Your full name',
                              })}
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={profileForm.control}
                      name="bio"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t('profile.bio', { defaultValue: 'Bio' })}</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder={t('profile.bioPlaceholder', {
                                defaultValue: 'Tell us a little about yourself...',
                              })}
                              className="resize-none"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            {t('profile.bioMaxLength', { defaultValue: 'Maximum 500 characters' })}
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={profileForm.control}
                        name="locale"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t('profile.locale')}</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue
                                    placeholder={t('profile.selectLocale', {
                                      defaultValue: 'Select a language',
                                    })}
                                  />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {LOCALES.map((locale) => (
                                  <SelectItem key={locale.value} value={locale.value}>
                                    {locale.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={profileForm.control}
                        name="timezone"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{t('profile.timezone')}</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue
                                    placeholder={t('profile.selectTimezone', {
                                      defaultValue: 'Select your timezone',
                                    })}
                                  />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {TIMEZONES.map((tz) => (
                                  <SelectItem key={tz.value} value={tz.value}>
                                    {tz.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    {/* User Type */}
                    <FormField
                      control={profileForm.control}
                      name="user_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Tipo de Usuário</FormLabel>
                          <Select onValueChange={field.onChange} value={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione seu tipo de usuário" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {USER_TYPE_VALUES.map((typeValue) => (
                                <SelectItem key={typeValue} value={typeValue}>
                                  {t(`profile.userTypes.${typeValue}`)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Location */}
                    <FormField
                      control={profileForm.control}
                      name="location"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Localização</FormLabel>
                          <FormControl>
                            <Input placeholder="São Paulo, Brasil" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Social Links */}
                    <div className="space-y-4">
                      <h3 className="text-sm font-medium">Redes Sociais</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <FormField
                          control={profileForm.control}
                          name="website"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Website</FormLabel>
                              <FormControl>
                                <Input placeholder="https://seusite.com" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={profileForm.control}
                          name="instagram"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Instagram</FormLabel>
                              <FormControl>
                                <Input placeholder="@seuperfil" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={profileForm.control}
                          name="twitter"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Twitter/X</FormLabel>
                              <FormControl>
                                <Input placeholder="@seuperfil" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                    </div>

                    {/* Professional Fields - Only show for professionals */}
                    {profileForm.watch('user_type') === 'professional' && (
                      <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
                        <h3 className="text-sm font-medium">Informações Profissionais</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <FormField
                            control={profileForm.control}
                            name="professional_since"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Profissional desde</FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    placeholder="2020"
                                    min={1900}
                                    max={new Date().getFullYear()}
                                    {...field}
                                    value={field.value || ''}
                                    onChange={(e) =>
                                      field.onChange(
                                        e.target.value ? parseInt(e.target.value) : null
                                      )
                                    }
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={profileForm.control}
                            name="specializations"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Especializações</FormLabel>
                                <FormControl>
                                  <Input
                                    placeholder="Mapas Natais, Sinastria, Trânsitos"
                                    value={field.value?.join(', ') || ''}
                                    onChange={(e) =>
                                      field.onChange(
                                        e.target.value
                                          .split(',')
                                          .map((s) => s.trim())
                                          .filter(Boolean)
                                      )
                                    }
                                  />
                                </FormControl>
                                <FormDescription>Separe por vírgula</FormDescription>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                      </div>
                    )}

                    <FormField
                      control={profileForm.control}
                      name="profile_public"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">
                              {t('profile.publicProfile', { defaultValue: 'Public Profile' })}
                            </FormLabel>
                            <FormDescription>
                              {t('profile.publicProfileDesc', {
                                defaultValue: 'Allow other users to view your profile',
                              })}
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch checked={field.value} onCheckedChange={field.onChange} />
                          </FormControl>
                        </FormItem>
                      )}
                    />

                    <Button type="submit" disabled={profileLoading}>
                      {profileLoading
                        ? t('profile.saving', { defaultValue: 'Saving...' })
                        : t('profile.updateProfile')}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Password Tab */}
          <TabsContent value="password">
            <Card>
              <CardHeader>
                <CardTitle>{t('profile.changePassword')}</CardTitle>
                <CardDescription>
                  {t('profile.changePasswordDesc', {
                    defaultValue: 'Update your password to keep your account secure',
                  })}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {passwordSuccess && (
                  <Alert className="mb-4">
                    <AlertDescription className="text-green-600">
                      {passwordSuccess}
                    </AlertDescription>
                  </Alert>
                )}

                {passwordError && (
                  <Alert variant="destructive" className="mb-4">
                    <AlertDescription>{passwordError}</AlertDescription>
                  </Alert>
                )}

                <Form {...passwordForm}>
                  <form
                    onSubmit={passwordForm.handleSubmit(onPasswordSubmit)}
                    className="space-y-4"
                  >
                    <FormField
                      control={passwordForm.control}
                      name="current_password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t('profile.currentPassword')}</FormLabel>
                          <FormControl>
                            <Input type="password" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={passwordForm.control}
                      name="new_password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t('profile.newPassword')}</FormLabel>
                          <FormControl>
                            <Input type="password" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={passwordForm.control}
                      name="new_password_confirm"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>{t('profile.confirmPassword')}</FormLabel>
                          <FormControl>
                            <Input type="password" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <Alert>
                      <AlertDescription>
                        <p className="font-medium mb-2">
                          {t('profile.passwordRequirements', {
                            defaultValue: 'Password requirements:',
                          })}
                        </p>
                        <ul className="text-xs space-y-1 list-disc list-inside">
                          <li>
                            {t('profile.passwordReqMin', { defaultValue: 'Minimum 8 characters' })}
                          </li>
                          <li>
                            {t('profile.passwordReqUpper', {
                              defaultValue: 'One uppercase letter',
                            })}
                          </li>
                          <li>
                            {t('profile.passwordReqLower', {
                              defaultValue: 'One lowercase letter',
                            })}
                          </li>
                          <li>{t('profile.passwordReqNumber', { defaultValue: 'One number' })}</li>
                          <li>
                            {t('profile.passwordReqSpecial', {
                              defaultValue: 'One special character',
                            })}
                          </li>
                        </ul>
                      </AlertDescription>
                    </Alert>

                    <Button type="submit" disabled={passwordLoading}>
                      {passwordLoading
                        ? t('profile.changing', { defaultValue: 'Changing...' })
                        : t('profile.updatePassword')}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <div className="space-y-6">
              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {dataLoading ? (
                  <>
                    <Card>
                      <CardHeader className="pb-2">
                        <Skeleton className="h-4 w-20" />
                      </CardHeader>
                      <CardContent>
                        <Skeleton className="h-8 w-16" />
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <Skeleton className="h-4 w-20" />
                      </CardHeader>
                      <CardContent>
                        <Skeleton className="h-8 w-16" />
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <Skeleton className="h-4 w-20" />
                      </CardHeader>
                      <CardContent>
                        <Skeleton className="h-8 w-16" />
                      </CardContent>
                    </Card>
                  </>
                ) : stats ? (
                  <>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardDescription>
                          {t('profile.security.accountDays', {
                            defaultValue: 'Account Age (days)',
                          })}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.account_age_days}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardDescription>
                          {t('profile.security.chartsCreated', { defaultValue: 'Charts Created' })}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.total_charts}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardDescription>
                          {t('profile.security.memberSince', { defaultValue: 'Member Since' })}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {new Date(user.created_at).toLocaleDateString(i18n.language || 'pt-BR', {
                            month: 'short',
                            year: 'numeric',
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  </>
                ) : null}
              </div>

              {/* OAuth Connections */}
              <Card>
                <CardHeader>
                  <CardTitle>
                    {t('profile.security.oauthConnections', { defaultValue: 'OAuth Connections' })}
                  </CardTitle>
                  <CardDescription>
                    {t('profile.security.oauthDesc', {
                      defaultValue: 'Manage your connections with external providers',
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {dataLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                    </div>
                  ) : oauthConnections.length > 0 ? (
                    <div className="space-y-2">
                      {oauthConnections.map((conn) => (
                        <div
                          key={conn.provider}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <Badge variant="secondary">{conn.provider}</Badge>
                            <span className="text-sm text-muted-foreground">
                              {t('profile.security.connectedOn', { defaultValue: 'Connected on' })}{' '}
                              {new Date(conn.connected_at).toLocaleDateString(
                                i18n.language || 'pt-BR'
                              )}
                            </span>
                          </div>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="destructive"
                                size="sm"
                                disabled={oauthConnections.length === 1}
                              >
                                {t('profile.security.disconnect', { defaultValue: 'Disconnect' })}
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>
                                  {t('profile.security.disconnectTitle', {
                                    defaultValue: 'Disconnect',
                                  })}{' '}
                                  {conn.provider}?
                                </DialogTitle>
                                <DialogDescription>
                                  {oauthConnections.length === 1
                                    ? t('profile.security.lastProviderWarning', {
                                        defaultValue:
                                          'This is your last OAuth provider. Make sure you have a password set before disconnecting.',
                                      })
                                    : t('profile.security.reconnectInfo', {
                                        defaultValue: 'You can reconnect this account later.',
                                      })}
                                </DialogDescription>
                              </DialogHeader>
                              <DialogFooter>
                                <Button variant="outline">{t('common.cancel')}</Button>
                                <Button
                                  variant="destructive"
                                  onClick={() => handleDisconnectOAuth(conn.provider)}
                                >
                                  {t('profile.security.disconnect', { defaultValue: 'Disconnect' })}
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {t('profile.security.noOauthConnections', {
                        defaultValue: 'No OAuth connections configured',
                      })}
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Activity Log */}
              <Card>
                <CardHeader>
                  <CardTitle>
                    {t('profile.security.recentActivity', { defaultValue: 'Recent Activity' })}
                  </CardTitle>
                  <CardDescription>
                    {t('profile.security.recentActivityDesc', {
                      defaultValue: 'Latest activities on your account',
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {dataLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                    </div>
                  ) : activities.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>
                            {t('profile.security.action', { defaultValue: 'Action' })}
                          </TableHead>
                          <TableHead>{t('profile.security.ip', { defaultValue: 'IP' })}</TableHead>
                          <TableHead>
                            {t('profile.security.date', { defaultValue: 'Date' })}
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {activities.map((activity) => (
                          <TableRow key={activity.id}>
                            <TableCell>
                              <Badge
                                variant={
                                  activity.action === 'login'
                                    ? 'default'
                                    : activity.action === 'logout'
                                      ? 'secondary'
                                      : 'outline'
                                }
                              >
                                {activity.action}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-xs">
                              {activity.ip_address}
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {formatDate(activity.created_at)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {t('profile.security.noActivity', { defaultValue: 'No recent activity' })}
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Privacy Tab */}
          <TabsContent value="privacy">
            <div className="space-y-6">
              {/* Data Export */}
              <Card>
                <CardHeader>
                  <CardTitle>
                    {t('profile.privacy.exportTitle', { defaultValue: 'Export Data' })}
                  </CardTitle>
                  <CardDescription>
                    {t('profile.privacy.exportDesc', {
                      defaultValue: 'Download a copy of all your data (LGPD/GDPR)',
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    {t('profile.privacy.exportInfo', {
                      defaultValue:
                        'You can export all your personal data at any time. The file will include your profile, birth charts, and settings.',
                    })}
                  </p>
                  <Button onClick={handleExportData} variant="outline">
                    {t('profile.privacy.exportButton', { defaultValue: 'Export My Data' })}
                  </Button>
                </CardContent>
              </Card>

              {/* Danger Zone */}
              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive">
                    {t('profile.privacy.dangerZone', { defaultValue: 'Danger Zone' })}
                  </CardTitle>
                  <CardDescription>
                    {t('profile.privacy.dangerZoneDesc', {
                      defaultValue: 'Irreversible actions on your account',
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">{t('profile.deleteAccount')}</h4>
                      <p className="text-sm text-muted-foreground mb-4">
                        {t('profile.deleteAccountWarning')}
                      </p>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="destructive">
                            {t('profile.privacy.deleteMyAccount', {
                              defaultValue: 'Delete My Account',
                            })}
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>
                              {t('profile.privacy.confirmDeleteTitle', {
                                defaultValue: 'Are you absolutely sure?',
                              })}
                            </DialogTitle>
                            <DialogDescription>
                              {t('profile.privacy.confirmDeleteDesc', {
                                defaultValue:
                                  'This action cannot be undone. This will permanently delete your account and remove all your data from our servers.',
                              })}
                            </DialogDescription>
                          </DialogHeader>
                          <DialogFooter>
                            <Button variant="outline">{t('common.cancel')}</Button>
                            <Button variant="destructive" onClick={handleDeleteAccount}>
                              {t('profile.privacy.yesDeleteAccount', {
                                defaultValue: 'Yes, delete my account',
                              })}
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
