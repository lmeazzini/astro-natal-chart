/**
 * AdminLayout - Layout component for admin portal pages
 *
 * Provides a consistent layout with:
 * - Header with logo and user info
 * - Sidebar navigation
 * - Main content area with Outlet
 */

import { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/contexts/AuthContext';
import { NavActions } from '@/components/NavActions';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { LayoutDashboard, Users, FileText, ArrowLeft, Menu, X, Shield } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export function AdminLayout() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems: NavItem[] = [
    {
      label: t('admin.nav.dashboard', { defaultValue: 'Dashboard' }),
      href: '/admin',
      icon: <LayoutDashboard className="h-5 w-5" />,
    },
    {
      label: t('admin.nav.users', { defaultValue: 'Users' }),
      href: '/admin/users',
      icon: <Users className="h-5 w-5" />,
    },
    {
      label: t('admin.nav.auditLogs', { defaultValue: 'Audit Logs' }),
      href: '/admin/audit-logs',
      icon: <FileText className="h-5 w-5" />,
    },
  ];

  const isActive = (href: string) => {
    if (href === '/admin') {
      return location.pathname === '/admin';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card border-b border-border">
        <div className="flex h-16 items-center justify-between px-4 lg:px-6">
          {/* Left: Logo and Title */}
          <div className="flex items-center gap-4">
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>

            <Link to="/admin" className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold text-foreground hidden sm:inline">
                {t('admin.title', { defaultValue: 'Admin Portal' })}
              </span>
            </Link>
          </div>

          {/* Right: User info and actions */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:inline">
              {user?.full_name || user?.email}
            </span>
            <NavActions />
            <Link to="/dashboard">
              <Button variant="outline" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {t('admin.exitAdmin', { defaultValue: 'Exit Admin' })}
                </span>
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 lg:top-16 lg:border-r lg:border-border lg:bg-card">
          <nav className="flex-1 space-y-1 p-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive(item.href)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                {item.icon}
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>

        {/* Sidebar - Mobile (overlay) */}
        {sidebarOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40 bg-black/50 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />

            {/* Sidebar */}
            <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border lg:hidden">
              <div className="flex h-16 items-center justify-between px-4 border-b border-border">
                <span className="text-lg font-semibold">
                  {t('admin.title', { defaultValue: 'Admin Portal' })}
                </span>
                <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <nav className="flex-1 space-y-1 p-4">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    to={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive(item.href)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    {item.icon}
                    {item.label}
                  </Link>
                ))}
              </nav>
            </aside>
          </>
        )}

        {/* Main content */}
        <main className="flex-1 lg:ml-64 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
