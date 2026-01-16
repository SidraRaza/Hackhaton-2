'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { signIn as betterSignIn, signOut as betterSignOut, useSession } from './better-auth-client';

interface AuthContextType {
  user: any;
  signIn: (email: string, password: string) => Promise<any>;
  signOut: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  signIn: async () => {},
  signOut: async () => {},
  isAuthenticated: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending } = useSession();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  const handleSignIn = async (email: string, password: string) => {
    try {
      const result = await betterSignIn('credentials', {
        email,
        password,
        redirect: false,
      });

      if (result?.token) {
        localStorage.setItem('token', result.token);
        setIsAuthenticated(true);
      }

      return result;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const handleSignOut = async () => {
    try {
      await betterSignOut({ redirect: false });
      localStorage.removeItem('token');
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{
      user: session?.user || null,
      signIn: handleSignIn,
      signOut: handleSignOut,
      isAuthenticated
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}