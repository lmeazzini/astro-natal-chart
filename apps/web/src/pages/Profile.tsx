/**
 * User profile and settings page
 */

import { useState, useEffect } from 'react';
import { useNavigate, Navigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../contexts/AuthContext';
import {
  userService,
  UserStats,
  UserActivity,
  OAuthConnection,
} from '../services/users';
import { ThemeToggle } from '../components/ThemeToggle';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';

// Form schemas
const profileFormSchema = z.object({
  full_name: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres'),
  bio: z.string().max(500, 'Bio deve ter no máximo 500 caracteres').optional(),
  locale: z.string(),
  timezone: z.string(),
  profile_public: z.boolean(),
});

const passwordFormSchema = z.object({
  current_password: z.string().min(1, 'Senha atual é obrigatória'),
  new_password: z.string()
    .min(8, 'Senha deve ter pelo menos 8 caracteres')
    .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiúscula')
    .regex(/[a-z]/, 'Senha deve conter pelo menos uma letra minúscula')
    .regex(/[0-9]/, 'Senha deve conter pelo menos um número')
    .regex(/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/, 'Senha deve conter pelo menos um caractere especial'),
  new_password_confirm: z.string().min(1, 'Confirmação de senha é obrigatória'),
}).refine((data) => data.new_password === data.new_password_confirm, {
  message: 'As senhas não coincidem',
  path: ['new_password_confirm'],
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;
type PasswordFormValues = z.infer<typeof passwordFormSchema>;

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
  { value: 'es-ES', label: 'Español' },
];

export function ProfilePage() {
  const navigate = useNavigate();
  const { user, setUser, logout, isLoading: authLoading } = useAuth();

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
      });
    }
  }, [user, profileForm]);

  // Load stats, activities, and OAuth connections
  useEffect(() => {
    if (user && (activeTab === 'security' || activeTab === 'privacy')) {
      loadSecurityData();
    }
  }, [user, activeTab]);

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

      const updatedUser = await userService.updateProfile(data, token);
      setUser(updatedUser);
      setProfileSuccess('Perfil atualizado com sucesso!');

      setTimeout(() => setProfileSuccess(''), 5000);
    } catch (error) {
      setProfileError(error instanceof Error ? error.message : 'Erro ao atualizar perfil');
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

      setPasswordSuccess('Senha alterada com sucesso!');
      passwordForm.reset();

      setTimeout(() => setPasswordSuccess(''), 5000);
    } catch (error) {
      setPasswordError(error instanceof Error ? error.message : 'Erro ao alterar senha');
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
      a.download = `astro-data-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Erro ao exportar dados');
    }
  }

  // Handle account deletion
  async function handleDeleteAccount() {
    const password = prompt('Digite sua senha para confirmar a exclusão da conta:');
    if (!password) return;

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      await userService.deleteAccount(token);
      logout();
      navigate('/');
    } catch (error) {
      alert('Erro ao excluir conta. Verifique sua senha.');
    }
  }

  // Handle disconnect OAuth
  async function handleDisconnectOAuth(provider: string) {
    const token = localStorage.getItem('astro_access_token');
    if (!token) return;

    try {
      await userService.disconnectOAuth(provider, token);
      setOAuthConnections(
        oauthConnections.filter((conn) => conn.provider !== provider)
      );
    } catch (error) {
      alert('Erro ao desconectar OAuth');
    }
  }

  // Format date
  function formatDate(date: string | Date) {
    return new Date(date).toLocaleDateString('pt-BR', {
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
        <p className="text-muted-foreground">Carregando...</p>
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
            aria-label="Voltar ao Dashboard"
          >
            <img
              src="/logo.png"
              alt="Astro"
              className="h-8 w-8"
            />
            <h1 className="text-2xl font-bold text-foreground">Astro</h1>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
            >
              ← Voltar ao Dashboard
            </Button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-6xl mx-auto py-8 px-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
            <TabsTrigger value="profile">Perfil</TabsTrigger>
            <TabsTrigger value="password">Senha</TabsTrigger>
            <TabsTrigger value="security">Segurança</TabsTrigger>
            <TabsTrigger value="privacy">Privacidade</TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Informações do Perfil</CardTitle>
                <CardDescription>
                  Atualize suas informações pessoais e preferências
                </CardDescription>
              </CardHeader>
              <CardContent>
                {profileSuccess && (
                  <Alert className="mb-4">
                    <AlertDescription className="text-green-600">
                      {profileSuccess}
                    </AlertDescription>
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
                          <FormLabel>Nome Completo *</FormLabel>
                          <FormControl>
                            <Input placeholder="Seu nome completo" {...field} />
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
                          <FormLabel>Bio</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Conte um pouco sobre você..."
                              className="resize-none"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Máximo de 500 caracteres
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
                            <FormLabel>Idioma</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Selecione um idioma" />
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
                            <FormLabel>Fuso Horário</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Selecione seu fuso horário" />
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

                    <FormField
                      control={profileForm.control}
                      name="profile_public"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">
                              Perfil Público
                            </FormLabel>
                            <FormDescription>
                              Permitir que outros usuários visualizem seu perfil
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />

                    <Button type="submit" disabled={profileLoading}>
                      {profileLoading ? 'Salvando...' : 'Salvar Alterações'}
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
                <CardTitle>Alterar Senha</CardTitle>
                <CardDescription>
                  Atualize sua senha para manter sua conta segura
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
                  <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
                    <FormField
                      control={passwordForm.control}
                      name="current_password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Senha Atual</FormLabel>
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
                          <FormLabel>Nova Senha</FormLabel>
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
                          <FormLabel>Confirmar Nova Senha</FormLabel>
                          <FormControl>
                            <Input type="password" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <Alert>
                      <AlertDescription>
                        <p className="font-medium mb-2">Requisitos da senha:</p>
                        <ul className="text-xs space-y-1 list-disc list-inside">
                          <li>Mínimo 8 caracteres</li>
                          <li>Uma letra maiúscula</li>
                          <li>Uma letra minúscula</li>
                          <li>Um número</li>
                          <li>Um caractere especial</li>
                        </ul>
                      </AlertDescription>
                    </Alert>

                    <Button type="submit" disabled={passwordLoading}>
                      {passwordLoading ? 'Alterando...' : 'Alterar Senha'}
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
                        <CardDescription>Dias de Conta</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.account_age_days}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardDescription>Mapas Criados</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{stats.total_charts}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardDescription>Membro Desde</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {new Date(user.created_at).toLocaleDateString('pt-BR', {
                            month: 'short',
                            year: 'numeric'
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
                  <CardTitle>Conexões OAuth</CardTitle>
                  <CardDescription>
                    Gerencie suas conexões com provedores externos
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
                            <Badge variant="secondary">
                              {conn.provider}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              Conectado em {new Date(conn.connected_at).toLocaleDateString('pt-BR')}
                            </span>
                          </div>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="destructive"
                                size="sm"
                                disabled={oauthConnections.length === 1}
                              >
                                Desconectar
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Desconectar {conn.provider}?</DialogTitle>
                                <DialogDescription>
                                  {oauthConnections.length === 1
                                    ? 'Este é seu último provedor OAuth. Certifique-se de ter uma senha configurada antes de desconectar.'
                                    : 'Você poderá reconectar esta conta posteriormente.'}
                                </DialogDescription>
                              </DialogHeader>
                              <DialogFooter>
                                <Button variant="outline">Cancelar</Button>
                                <Button
                                  variant="destructive"
                                  onClick={() => handleDisconnectOAuth(conn.provider)}
                                >
                                  Desconectar
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Nenhuma conexão OAuth configurada
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Activity Log */}
              <Card>
                <CardHeader>
                  <CardTitle>Atividade Recente</CardTitle>
                  <CardDescription>
                    Últimas atividades em sua conta
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
                          <TableHead>Ação</TableHead>
                          <TableHead>IP</TableHead>
                          <TableHead>Data</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {activities.map((activity) => (
                          <TableRow key={activity.id}>
                            <TableCell>
                              <Badge variant={
                                activity.action === 'login' ? 'default' :
                                activity.action === 'logout' ? 'secondary' :
                                'outline'
                              }>
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
                      Nenhuma atividade recente
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
                  <CardTitle>Exportar Dados</CardTitle>
                  <CardDescription>
                    Baixe uma cópia de todos os seus dados (LGPD/GDPR)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Você pode exportar todos os seus dados pessoais a qualquer momento.
                    O arquivo incluirá seu perfil, mapas natais e configurações.
                  </p>
                  <Button onClick={handleExportData} variant="outline">
                    Exportar Meus Dados
                  </Button>
                </CardContent>
              </Card>

              {/* Danger Zone */}
              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive">Zona de Perigo</CardTitle>
                  <CardDescription>
                    Ações irreversíveis em sua conta
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Excluir Conta</h4>
                      <p className="text-sm text-muted-foreground mb-4">
                        Uma vez excluída, sua conta não poderá ser recuperada. Todos os seus dados
                        serão permanentemente removidos após 30 dias.
                      </p>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="destructive">
                            Excluir Minha Conta
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Tem certeza absoluta?</DialogTitle>
                            <DialogDescription>
                              Esta ação não pode ser desfeita. Isso excluirá permanentemente sua
                              conta e removerá todos os seus dados de nossos servidores.
                            </DialogDescription>
                          </DialogHeader>
                          <DialogFooter>
                            <Button variant="outline">Cancelar</Button>
                            <Button
                              variant="destructive"
                              onClick={handleDeleteAccount}
                            >
                              Sim, excluir minha conta
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