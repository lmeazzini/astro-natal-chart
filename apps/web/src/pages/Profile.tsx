/**
 * User profile and settings page
 */

import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  userService,
  UserStats,
  UserActivity,
  OAuthConnection,
} from '../services/users';

type TabType = 'profile' | 'password' | 'security' | 'privacy';

export function ProfilePage() {
  const navigate = useNavigate();
  const { user, setUser, logout, isLoading: authLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [stats, setStats] = useState<UserStats | null>(null);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [oauthConnections, setOAuthConnections] = useState<OAuthConnection[]>(
    []
  );

  // Profile form
  const [profileData, setProfileData] = useState({
    full_name: '',
    bio: '',
    locale: 'pt-BR',
    timezone: '',
    profile_public: false,
  });
  const [profileErrors, setProfileErrors] = useState<Record<string, string>>(
    {}
  );
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState('');
  const [profileError, setProfileError] = useState('');

  // Password form
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    new_password_confirm: '',
  });
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string>>(
    {}
  );
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // Load user data
  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        bio: user.bio || '',
        locale: user.locale || 'pt-BR',
        timezone: user.timezone || '',
        profile_public: user.profile_public || false,
      });
    }
  }, [user]);

  // Load stats, activities, and OAuth connections
  useEffect(() => {
    if (user && activeTab !== 'profile' && activeTab !== 'password') {
      loadSecurityData();
    }
  }, [user, activeTab]);

  async function loadSecurityData() {
    const token = localStorage.getItem('astro_access_token');
    if (!token) return;

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
    }
  }

  // Profile validation
  function validateProfile(): boolean {
    const errors: Record<string, string> = {};

    if (!profileData.full_name || profileData.full_name.length < 3) {
      errors.full_name = 'Nome deve ter pelo menos 3 caracteres';
    }

    if (profileData.bio && profileData.bio.length > 500) {
      errors.bio = 'Bio deve ter no máximo 500 caracteres';
    }

    setProfileErrors(errors);
    return Object.keys(errors).length === 0;
  }

  // Password validation
  function validatePassword(): boolean {
    const errors: Record<string, string> = {};

    if (!passwordData.current_password) {
      errors.current_password = 'Senha atual é obrigatória';
    }

    if (!passwordData.new_password) {
      errors.new_password = 'Nova senha é obrigatória';
    } else if (passwordData.new_password.length < 8) {
      errors.new_password = 'Senha deve ter pelo menos 8 caracteres';
    } else {
      if (!/[A-Z]/.test(passwordData.new_password)) {
        errors.new_password =
          'Senha deve conter pelo menos uma letra maiúscula';
      } else if (!/[a-z]/.test(passwordData.new_password)) {
        errors.new_password =
          'Senha deve conter pelo menos uma letra minúscula';
      } else if (!/[0-9]/.test(passwordData.new_password)) {
        errors.new_password = 'Senha deve conter pelo menos um número';
      } else if (
        !/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(passwordData.new_password)
      ) {
        errors.new_password =
          'Senha deve conter pelo menos um caractere especial';
      }
    }

    if (!passwordData.new_password_confirm) {
      errors.new_password_confirm = 'Confirmação de senha é obrigatória';
    } else if (passwordData.new_password !== passwordData.new_password_confirm) {
      errors.new_password_confirm = 'As senhas não coincidem';
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  }

  // Handle profile submit
  async function handleProfileSubmit(e: FormEvent) {
    e.preventDefault();
    setProfileError('');
    setProfileSuccess('');

    if (!validateProfile()) return;

    setProfileLoading(true);
    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) throw new Error('Não autenticado');

      const updatedUser = await userService.updateProfile(profileData, token);
      setUser(updatedUser);
      setProfileSuccess('Perfil atualizado com sucesso!');
    } catch (error) {
      setProfileError(
        error instanceof Error ? error.message : 'Erro ao atualizar perfil'
      );
    } finally {
      setProfileLoading(false);
    }
  }

  // Handle password submit
  async function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (!validatePassword()) return;

    setPasswordLoading(true);
    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) throw new Error('Não autenticado');

      await userService.changePassword(passwordData, token);
      setPasswordSuccess('Senha alterada com sucesso!');
      setPasswordData({
        current_password: '',
        new_password: '',
        new_password_confirm: '',
      });
    } catch (error) {
      setPasswordError(
        error instanceof Error ? error.message : 'Erro ao alterar senha'
      );
    } finally {
      setPasswordLoading(false);
    }
  }

  // Handle export data
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
      a.download = `astro-data-${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Erro ao exportar dados');
    }
  }

  // Handle delete account
  async function handleDeleteAccount() {
    const confirmation = prompt(
      'Digite "DELETAR" em letras maiúsculas para confirmar a exclusão da sua conta:'
    );
    if (confirmation !== 'DELETAR') return;

    if (
      !confirm(
        'Tem certeza? Esta ação excluirá sua conta em 30 dias. Você receberá um email de confirmação.'
      )
    ) {
      return;
    }

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      await userService.deleteAccount(token);
      logout();
      navigate('/');
    } catch (error) {
      alert('Erro ao deletar conta');
    }
  }

  // Handle disconnect OAuth
  async function handleDisconnectOAuth(provider: string) {
    // Warn if disconnecting last provider
    if (oauthConnections.length <= 1) {
      const proceed = confirm(
        'Este é seu último provedor OAuth. Certifique-se de ter uma senha configurada antes de desconectar. Deseja continuar?'
      );
      if (!proceed) return;
    }

    if (!confirm(`Deseja desconectar ${provider}?`)) return;

    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      await userService.disconnectOAuth(provider, token);
      setOAuthConnections(
        oauthConnections.filter((conn) => conn.provider !== provider)
      );
    } catch (error) {
      alert('Erro ao desconectar OAuth');
    }
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
          <h1 className="text-2xl font-bold text-foreground">Meu Perfil</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Voltar ao Dashboard
          </button>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="md:col-span-1">
            <div className="bg-card border border-border rounded-lg p-4 space-y-2">
              <button
                onClick={() => setActiveTab('profile')}
                className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'profile'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-secondary'
                }`}
              >
                Perfil
              </button>
              <button
                onClick={() => setActiveTab('password')}
                className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'password'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-secondary'
                }`}
              >
                Senha
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'security'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-secondary'
                }`}
              >
                Segurança
              </button>
              <button
                onClick={() => setActiveTab('privacy')}
                className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'privacy'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-secondary'
                }`}
              >
                Privacidade
              </button>
            </div>
          </div>

          {/* Main content */}
          <div className="md:col-span-3">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="bg-card border border-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-foreground mb-4">
                  Informações do Perfil
                </h2>

                {profileSuccess && (
                  <div className="mb-4 p-4 bg-green-500/10 border border-green-500/20 rounded-md">
                    <p className="text-sm text-green-700 dark:text-green-400">
                      {profileSuccess}
                    </p>
                  </div>
                )}

                {profileError && (
                  <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
                    <p className="text-sm text-destructive">{profileError}</p>
                  </div>
                )}

                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Nome Completo *
                    </label>
                    <input
                      type="text"
                      value={profileData.full_name}
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          full_name: e.target.value,
                        })
                      }
                      className={`w-full px-4 py-2 bg-background border ${
                        profileErrors.full_name
                          ? 'border-destructive'
                          : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                    />
                    {profileErrors.full_name && (
                      <p className="mt-1 text-sm text-destructive">
                        {profileErrors.full_name}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={user.email}
                      disabled
                      className="w-full px-4 py-2 bg-muted border border-input rounded-md text-muted-foreground cursor-not-allowed"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      O email não pode ser alterado
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Bio
                    </label>
                    <textarea
                      value={profileData.bio}
                      onChange={(e) =>
                        setProfileData({ ...profileData, bio: e.target.value })
                      }
                      rows={4}
                      maxLength={500}
                      className={`w-full px-4 py-2 bg-background border ${
                        profileErrors.bio
                          ? 'border-destructive'
                          : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                      placeholder="Conte um pouco sobre você..."
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      {profileData.bio.length}/500 caracteres
                    </p>
                    {profileErrors.bio && (
                      <p className="mt-1 text-sm text-destructive">
                        {profileErrors.bio}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Idioma
                    </label>
                    <select
                      value={profileData.locale}
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          locale: e.target.value,
                        })
                      }
                      className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="pt-BR">Português (Brasil)</option>
                      <option value="en-US">English (US)</option>
                      <option value="es-ES">Español</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Fuso Horário
                    </label>
                    <input
                      type="text"
                      value={profileData.timezone}
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          timezone: e.target.value,
                        })
                      }
                      placeholder="America/Sao_Paulo"
                      className="w-full px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Formato IANA (ex: America/Sao_Paulo)
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="profile_public"
                      checked={profileData.profile_public}
                      onChange={(e) =>
                        setProfileData({
                          ...profileData,
                          profile_public: e.target.checked,
                        })
                      }
                      className="w-4 h-4 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                    />
                    <label
                      htmlFor="profile_public"
                      className="text-sm text-foreground cursor-pointer"
                    >
                      Tornar perfil público
                    </label>
                  </div>

                  <button
                    type="submit"
                    disabled={profileLoading}
                    className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-md hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                  >
                    {profileLoading ? 'Salvando...' : 'Salvar Alterações'}
                  </button>
                </form>
              </div>
            )}

            {/* Password Tab */}
            {activeTab === 'password' && (
              <div className="bg-card border border-border rounded-lg p-6">
                <h2 className="text-xl font-bold text-foreground mb-4">
                  Alterar Senha
                </h2>

                {passwordSuccess && (
                  <div className="mb-4 p-4 bg-green-500/10 border border-green-500/20 rounded-md">
                    <p className="text-sm text-green-700 dark:text-green-400">
                      {passwordSuccess}
                    </p>
                  </div>
                )}

                {passwordError && (
                  <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
                    <p className="text-sm text-destructive">{passwordError}</p>
                  </div>
                )}

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Senha Atual *
                    </label>
                    <input
                      type="password"
                      value={passwordData.current_password}
                      onChange={(e) =>
                        setPasswordData({
                          ...passwordData,
                          current_password: e.target.value,
                        })
                      }
                      className={`w-full px-4 py-2 bg-background border ${
                        passwordErrors.current_password
                          ? 'border-destructive'
                          : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                    />
                    {passwordErrors.current_password && (
                      <p className="mt-1 text-sm text-destructive">
                        {passwordErrors.current_password}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Nova Senha *
                    </label>
                    <input
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) =>
                        setPasswordData({
                          ...passwordData,
                          new_password: e.target.value,
                        })
                      }
                      className={`w-full px-4 py-2 bg-background border ${
                        passwordErrors.new_password
                          ? 'border-destructive'
                          : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                    />
                    {passwordErrors.new_password && (
                      <p className="mt-1 text-sm text-destructive">
                        {passwordErrors.new_password}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Confirmar Nova Senha *
                    </label>
                    <input
                      type="password"
                      value={passwordData.new_password_confirm}
                      onChange={(e) =>
                        setPasswordData({
                          ...passwordData,
                          new_password_confirm: e.target.value,
                        })
                      }
                      className={`w-full px-4 py-2 bg-background border ${
                        passwordErrors.new_password_confirm
                          ? 'border-destructive'
                          : 'border-input'
                      } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                    />
                    {passwordErrors.new_password_confirm && (
                      <p className="mt-1 text-sm text-destructive">
                        {passwordErrors.new_password_confirm}
                      </p>
                    )}
                  </div>

                  <div className="p-4 bg-muted/50 rounded-md">
                    <p className="text-xs text-muted-foreground font-medium mb-2">
                      A senha deve conter:
                    </p>
                    <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                      <li>Pelo menos 8 caracteres</li>
                      <li>Uma letra maiúscula</li>
                      <li>Uma letra minúscula</li>
                      <li>Um número</li>
                      <li>Um caractere especial (!@#$%^&*...)</li>
                    </ul>
                  </div>

                  <button
                    type="submit"
                    disabled={passwordLoading}
                    className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-md hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                  >
                    {passwordLoading ? 'Alterando...' : 'Alterar Senha'}
                  </button>
                </form>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                {/* Stats */}
                <div className="bg-card border border-border rounded-lg p-6">
                  <h2 className="text-xl font-bold text-foreground mb-4">
                    Estatísticas
                  </h2>
                  {stats ? (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Mapas Criados
                        </p>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.total_charts}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Idade da Conta
                        </p>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.account_age_days} dias
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Último Login
                        </p>
                        <p className="text-sm text-foreground">
                          {stats.last_login_at
                            ? new Date(stats.last_login_at).toLocaleString(
                                'pt-BR'
                              )
                            : 'Nunca'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Última Atividade
                        </p>
                        <p className="text-sm text-foreground">
                          {stats.last_activity_at
                            ? new Date(stats.last_activity_at).toLocaleString(
                                'pt-BR'
                              )
                            : 'Nunca'}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Carregando...
                    </p>
                  )}
                </div>

                {/* OAuth Connections */}
                <div className="bg-card border border-border rounded-lg p-6">
                  <h2 className="text-xl font-bold text-foreground mb-4">
                    Conexões OAuth
                  </h2>
                  {oauthConnections.length > 0 ? (
                    <div className="space-y-3">
                      {oauthConnections.map((conn) => (
                        <div
                          key={conn.provider}
                          className="flex items-center justify-between p-3 border border-border rounded-md"
                        >
                          <div>
                            <p className="font-medium text-foreground capitalize">
                              {conn.provider}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Conectado em{' '}
                              {new Date(conn.connected_at).toLocaleDateString(
                                'pt-BR'
                              )}
                            </p>
                          </div>
                          <button
                            onClick={() => handleDisconnectOAuth(conn.provider)}
                            className="px-3 py-1 text-sm text-destructive hover:bg-destructive/10 border border-destructive/20 rounded-md transition-colors"
                          >
                            Desconectar
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Nenhuma conexão OAuth
                    </p>
                  )}
                </div>

                {/* Activity Log */}
                <div className="bg-card border border-border rounded-lg p-6">
                  <h2 className="text-xl font-bold text-foreground mb-4">
                    Atividades Recentes
                  </h2>
                  {activities.length > 0 ? (
                    <div className="space-y-2">
                      {activities.map((activity) => (
                        <div
                          key={activity.id}
                          className="flex items-start justify-between p-3 border border-border rounded-md"
                        >
                          <div className="flex-1">
                            <p className="text-sm font-medium text-foreground">
                              {activity.action.replace(/_/g, ' ')}
                            </p>
                            {activity.resource_type && (
                              <p className="text-xs text-muted-foreground">
                                Tipo: {activity.resource_type}
                              </p>
                            )}
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">
                              {new Date(activity.created_at).toLocaleString(
                                'pt-BR'
                              )}
                            </p>
                            {activity.ip_address && (
                              <p className="text-xs text-muted-foreground">
                                IP: {activity.ip_address}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Nenhuma atividade registrada
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                {/* Export Data */}
                <div className="bg-card border border-border rounded-lg p-6">
                  <h2 className="text-xl font-bold text-foreground mb-2">
                    Exportar Dados
                  </h2>
                  <p className="text-sm text-muted-foreground mb-4">
                    Baixe todos os seus dados em formato JSON (LGPD/GDPR)
                  </p>
                  <button
                    onClick={handleExportData}
                    className="px-4 py-2 bg-secondary text-secondary-foreground font-medium rounded-md hover:opacity-90 transition-opacity"
                  >
                    Exportar Dados
                  </button>
                </div>

                {/* Delete Account */}
                <div className="bg-card border border-destructive/20 rounded-lg p-6">
                  <h2 className="text-xl font-bold text-destructive mb-2">
                    Zona de Perigo
                  </h2>
                  <p className="text-sm text-muted-foreground mb-4">
                    Deletar sua conta removerá todos os seus dados
                    permanentemente após 30 dias. Esta ação não pode ser
                    desfeita.
                  </p>
                  <button
                    onClick={handleDeleteAccount}
                    className="px-4 py-2 bg-destructive text-destructive-foreground font-medium rounded-md hover:opacity-90 transition-opacity"
                  >
                    Deletar Conta
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
