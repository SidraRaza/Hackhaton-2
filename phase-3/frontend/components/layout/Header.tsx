'use client';

import { useState, useEffect } from 'react';
import { useSession } from '../../lib/better-auth-client';
import { useAuth } from '../../lib/auth';
import { MoonIcon, SunIcon, Bars3Icon, XMarkIcon, UserCircleIcon, ArrowLeftOnRectangleIcon } from '@heroicons/react/24/outline';
import { useTheme } from './ThemeProvider';
import { Button } from '../ui';

export default function Header() {
  const { data: session } = useSession();
  const { isAuthenticated, signOut: handleSignOut } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignOutClick = () => {
    handleSignOut();
    localStorage.removeItem('token');
  };

  return (
    <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-primary">TodoApp</h1>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated && session?.user && (
              <>
                <span className="text-sm text-foreground/80 hidden sm:block">
                  Welcome, <span className="font-medium">{session.user.email}</span>
                </span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleSignOutClick}
                >
                  <ArrowLeftOnRectangleIcon className="h-4 w-4 mr-2" />
                  Sign out
                </Button>
              </>
            )}

            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={theme === 'dark' ? "Switch to light mode" : "Switch to dark mode"}
            >
              {theme === 'dark' ? (
                <SunIcon className="h-5 w-5" aria-hidden="true" />
              ) : (
                <MoonIcon className="h-5 w-5" aria-hidden="true" />
              )}
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            {isAuthenticated && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleSignOutClick}
              >
                Sign out
              </Button>
            )}

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-border">
            {isAuthenticated && session?.user && (
              <div className="px-3 py-2 text-sm text-foreground/80">
                Signed in as: <span className="font-medium">{session.user.email}</span>
              </div>
            )}
            <div className="flex justify-center py-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                aria-label={theme === 'dark' ? "Switch to light mode" : "Switch to dark mode"}
              >
                {theme === 'dark' ? (
                  <SunIcon className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <MoonIcon className="h-5 w-5" aria-hidden="true" />
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}