/**
 * AdminDashboard - Main admin dashboard page
 *
 * Displays system statistics and quick links to admin sections.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { adminService } from '@/services/admin';
import type { SystemStats } from '@/types/admin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Users, FileText, UserCheck, Mail, Crown, Shield, ChevronRight } from 'lucide-react';

export function AdminDashboard() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem('astro_access_token');
      if (!token || !user) return;

      try {
        setLoading(true);
        setError(null);
        const data = await adminService.getStats(token);
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch admin stats:', err);
        setError(t('admin.errors.fetchStats', { defaultValue: 'Failed to load statistics' }));
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, t]);

  const statCards = [
    {
      title: t('admin.stats.totalUsers', { defaultValue: 'Total Users' }),
      value: stats?.total_users ?? 0,
      icon: <Users className="h-5 w-5" />,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: t('admin.stats.totalCharts', { defaultValue: 'Total Charts' }),
      value: stats?.total_charts ?? 0,
      icon: <FileText className="h-5 w-5" />,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      title: t('admin.stats.activeUsers', { defaultValue: 'Active Users' }),
      value: stats?.active_users ?? 0,
      icon: <UserCheck className="h-5 w-5" />,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      title: t('admin.stats.verifiedUsers', { defaultValue: 'Verified Users' }),
      value: stats?.verified_users ?? 0,
      icon: <Mail className="h-5 w-5" />,
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
    },
  ];

  const roleCards = [
    {
      role: 'free',
      label: t('admin.roles.free', { defaultValue: 'Free' }),
      icon: <Users className="h-4 w-4" />,
      count: stats?.users_by_role?.free ?? 0,
    },
    {
      role: 'premium',
      label: t('admin.roles.premium', { defaultValue: 'Premium' }),
      icon: <Crown className="h-4 w-4" />,
      count: stats?.users_by_role?.premium ?? 0,
    },
    {
      role: 'admin',
      label: t('admin.roles.admin', { defaultValue: 'Admin' }),
      icon: <Shield className="h-4 w-4" />,
      count: stats?.users_by_role?.admin ?? 0,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">
          {t('admin.dashboard.title', { defaultValue: 'Dashboard' })}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t('admin.dashboard.subtitle', { defaultValue: 'Overview of your system statistics' })}
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor} ${stat.color}`}>{stat.icon}</div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-3xl font-bold">{stat.value.toLocaleString()}</div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Users by Role */}
      <Card>
        <CardHeader>
          <CardTitle>
            {t('admin.dashboard.usersByRole', { defaultValue: 'Users by Role' })}
          </CardTitle>
          <CardDescription>
            {t('admin.dashboard.usersByRoleDesc', {
              defaultValue: 'Distribution of users across different roles',
            })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {roleCards.map((role) => (
              <div
                key={role.role}
                className="flex items-center gap-3 p-4 rounded-lg border bg-card"
              >
                <div className="p-2 rounded-full bg-primary/10 text-primary">{role.icon}</div>
                <div>
                  <p className="text-sm font-medium">{role.label}</p>
                  {loading ? (
                    <Skeleton className="h-6 w-12 mt-1" />
                  ) : (
                    <p className="text-2xl font-bold">{role.count.toLocaleString()}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Links */}
      <Card>
        <CardHeader>
          <CardTitle>{t('admin.dashboard.quickLinks', { defaultValue: 'Quick Links' })}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              to="/admin/users"
              className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
            >
              <div className="flex items-center gap-3">
                <Users className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">
                  {t('admin.nav.users', { defaultValue: 'Manage Users' })}
                </span>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </Link>
            <Link
              to="/admin/audit-logs"
              className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">
                  {t('admin.nav.auditLogs', { defaultValue: 'View Audit Logs' })}
                </span>
                <Badge variant="secondary">
                  {t('admin.comingSoon', { defaultValue: 'Coming Soon' })}
                </Badge>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
