/**
 * AdminUsers - User management page
 *
 * Displays a paginated list of users with search and filter capabilities.
 */

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { adminService } from '@/services/admin';
import type { AdminUserSummary, AdminUserList, UserRole } from '@/types/admin';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  User,
  Crown,
  Shield,
  CheckCircle,
  XCircle,
  Mail,
  MailX,
} from 'lucide-react';

const USERS_PER_PAGE = 20;

export function AdminUsers() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  // State
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters from URL params
  const page = parseInt(searchParams.get('page') || '1', 10);
  const search = searchParams.get('search') || '';
  const roleFilter = (searchParams.get('role') as UserRole | null) || undefined;

  // Local state for search input (debounced)
  const [searchInput, setSearchInput] = useState(search);

  // Fetch users
  const fetchUsers = useCallback(async () => {
    const token = localStorage.getItem('astro_access_token');
    if (!token || !user) return;

    try {
      setLoading(true);
      setError(null);

      const skip = (page - 1) * USERS_PER_PAGE;
      const data: AdminUserList = await adminService.getUsers(token, {
        skip,
        limit: USERS_PER_PAGE,
        search: search || undefined,
        role: roleFilter,
      });

      setUsers(data.users);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(t('admin.errors.fetchUsers', { defaultValue: 'Failed to load users' }));
    } finally {
      setLoading(false);
    }
  }, [user, page, search, roleFilter, t]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== search) {
        const newParams = new URLSearchParams(searchParams);
        if (searchInput) {
          newParams.set('search', searchInput);
        } else {
          newParams.delete('search');
        }
        newParams.set('page', '1'); // Reset to first page on search
        setSearchParams(newParams);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchInput, search, searchParams, setSearchParams]);

  // Handlers
  const handleRoleFilter = (value: string) => {
    const newParams = new URLSearchParams(searchParams);
    if (value === 'all') {
      newParams.delete('role');
    } else {
      newParams.set('role', value);
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', String(newPage));
    setSearchParams(newParams);
  };

  // Pagination
  const totalPages = Math.ceil(total / USERS_PER_PAGE);
  const canGoBack = page > 1;
  const canGoForward = page < totalPages;

  // Role badge helper
  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'admin':
        return (
          <Badge variant="default" className="gap-1">
            <Shield className="h-3 w-3" />
            {t('admin.roles.admin', { defaultValue: 'Admin' })}
          </Badge>
        );
      case 'premium':
        return (
          <Badge
            variant="secondary"
            className="gap-1 bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200"
          >
            <Crown className="h-3 w-3" />
            {t('admin.roles.premium', { defaultValue: 'Premium' })}
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="gap-1">
            <User className="h-3 w-3" />
            {t('admin.roles.free', { defaultValue: 'Free' })}
          </Badge>
        );
    }
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">
          {t('admin.users.title', { defaultValue: 'Users' })}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t('admin.users.subtitle', { defaultValue: 'Manage user accounts and permissions' })}
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            {t('admin.users.filters', { defaultValue: 'Filters' })}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={t('admin.users.searchPlaceholder', {
                  defaultValue: 'Search by name or email...',
                })}
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Role Filter */}
            <Select value={roleFilter || 'all'} onValueChange={handleRoleFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue
                  placeholder={t('admin.users.filterByRole', { defaultValue: 'Filter by role' })}
                />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  {t('admin.users.allRoles', { defaultValue: 'All Roles' })}
                </SelectItem>
                <SelectItem value="free">
                  {t('admin.roles.free', { defaultValue: 'Free' })}
                </SelectItem>
                <SelectItem value="premium">
                  {t('admin.roles.premium', { defaultValue: 'Premium' })}
                </SelectItem>
                <SelectItem value="admin">
                  {t('admin.roles.admin', { defaultValue: 'Admin' })}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Users Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('admin.users.name', { defaultValue: 'Name' })}</TableHead>
                <TableHead>{t('admin.users.email', { defaultValue: 'Email' })}</TableHead>
                <TableHead>{t('admin.users.role', { defaultValue: 'Role' })}</TableHead>
                <TableHead>{t('admin.users.status', { defaultValue: 'Status' })}</TableHead>
                <TableHead>{t('admin.users.verified', { defaultValue: 'Verified' })}</TableHead>
                <TableHead>{t('admin.users.created', { defaultValue: 'Created' })}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                // Loading skeleton
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Skeleton className="h-5 w-32" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-5 w-48" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-5 w-20" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-5 w-16" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-5 w-16" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-5 w-24" />
                    </TableCell>
                  </TableRow>
                ))
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    {t('admin.users.noUsers', { defaultValue: 'No users found' })}
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">
                      {user.full_name || (
                        <span className="text-muted-foreground italic">
                          {t('admin.users.noName', { defaultValue: 'No name' })}
                        </span>
                      )}
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{getRoleBadge(user.role)}</TableCell>
                    <TableCell>
                      {user.is_active ? (
                        <Badge variant="outline" className="gap-1 text-green-600 border-green-600">
                          <CheckCircle className="h-3 w-3" />
                          {t('admin.users.active', { defaultValue: 'Active' })}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="gap-1 text-red-600 border-red-600">
                          <XCircle className="h-3 w-3" />
                          {t('admin.users.inactive', { defaultValue: 'Inactive' })}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {user.email_verified ? (
                        <Mail className="h-4 w-4 text-green-600" />
                      ) : (
                        <MailX className="h-4 w-4 text-muted-foreground" />
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(user.created_at)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {t('admin.users.showing', {
              defaultValue: 'Showing {{from}}-{{to}} of {{total}} users',
              from: (page - 1) * USERS_PER_PAGE + 1,
              to: Math.min(page * USERS_PER_PAGE, total),
              total,
            })}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page - 1)}
              disabled={!canGoBack}
            >
              <ChevronLeft className="h-4 w-4" />
              {t('common.previous', { defaultValue: 'Previous' })}
            </Button>
            <span className="text-sm text-muted-foreground">
              {t('admin.users.page', {
                defaultValue: 'Page {{page}} of {{total}}',
                page,
                total: totalPages,
              })}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page + 1)}
              disabled={!canGoForward}
            >
              {t('common.next', { defaultValue: 'Next' })}
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
