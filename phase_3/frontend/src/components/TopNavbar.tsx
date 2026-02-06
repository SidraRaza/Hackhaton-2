'use client';

import React from 'react';
import { Search, Bell, User } from 'lucide-react';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { ThemeToggle } from './ThemeToggle';
import { cn } from '../lib/utils';
import { useAuth } from '../lib/auth';
import Link from 'next/link';

const TopNavbar: React.FC = () => {
  const { user, loading, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 w-full bg-background border-b border-border shadow-none">
      <div className="flex h-14 items-center justify-between px-4 md:px-6">
        {/* Left side - Search */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2 h-4 w-4 text-text-muted" />
            <input
              type="search"
              placeholder="Search..."
              className="h-8 w-32 md:w-48 lg:w-64 pl-8 pr-3 rounded-md border border-border bg-background text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        {/* Right side - User controls */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative h-8 w-8 p-0 hover:bg-muted">
            <Bell className="h-4 w-4 text-foreground" />
            <span className="absolute top-0.5 right-0.5 h-1.5 w-1.5 rounded-full bg-destructive"></span>
          </Button>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Conditional rendering based on authentication */}
          {user ? (
            /* User Avatar Dropdown */
            <div className="flex items-center gap-2">
              <div className="hidden md:block text-right">
                <p className="text-sm font-medium text-foreground">{user.name || user.email}</p>
                <p className="text-xs text-text-muted">{user.email}</p>
              </div>
              <Avatar className="h-8 w-8 border border-border">
                <AvatarImage src={user.avatar} alt={user.name || user.email} />
                <AvatarFallback className="text-xs bg-muted text-foreground">
                  {(user.name || user.email)?.charAt(0)?.toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <Button
                variant="outline"
                size="sm"
                onClick={logout}
                className="ml-1 h-8 px-3 text-xs hover:bg-destructive hover:text-destructive-foreground"
              >
                Logout
              </Button>
            </div>
          ) : (
            /* Login button when not authenticated */
            <Link href="/auth/login">
              <Button variant="outline" size="sm" className="h-8 px-3 text-xs">
                Login
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopNavbar;