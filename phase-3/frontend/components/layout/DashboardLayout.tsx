'use client';

import { useState, ReactNode } from 'react';
import { useSession } from '../../lib/better-auth-client';
import { useAuth } from '../../lib/auth';
import Header from './Header';
import Sidebar from './Sidebar';
import { Button } from '../ui';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export default function DashboardLayout({ children, title = "Dashboard" }: LayoutProps) {
  const { data: session } = useSession();
  const { isAuthenticated, signOut: handleSignOut } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSignOutClick = () => {
    handleSignOut();
    localStorage.removeItem('token');
  };

  if (!isAuthenticated) {
    // If not authenticated, just render children without layout
    return <div className="min-h-screen bg-background">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="md:pl-64 flex flex-col flex-1">
        <Sidebar />

        <main className="flex-1 pb-8">
          <div className="pt-6">
            <div className="mx-auto px-4 sm:px-6 md:px-8">
              <div className="pb-5">
                <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
              </div>
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}