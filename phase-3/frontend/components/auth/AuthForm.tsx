'use client';

import { useState } from 'react';
import { signIn, signOut, useSession } from '../../lib/better-auth-client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { useToast } from '../ui';

interface AuthFormProps {
  onAuthChange?: () => void;
}

export default function AuthForm({ onAuthChange }: AuthFormProps) {
  const { data: session, isPending } = useSession();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        // Login
        const result = await signIn('credentials', {
          email,
          password,
          redirect: false,
        });

        if (result?.error) {
          addToast(result.error, 'error');
        } else if (result?.token) {
          localStorage.setItem('token', result.token);
          addToast('Login successful!', 'success');
          onAuthChange?.();
        }
      } else {
        // Register
        const result = await signIn('credentials', {
          email,
          password,
          redirect: false,
        });

        if (result?.error) {
          addToast(result.error, 'error');
        } else if (result?.token) {
          localStorage.setItem('token', result.token);
          addToast('Registration successful!', 'success');
          onAuthChange?.();
        }
      }
    } catch (err) {
      addToast('An error occurred during authentication', 'error');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (session?.user) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Welcome, {session.user.email}</CardTitle>
          <CardDescription>You are signed in</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="destructive"
            fullWidth
            onClick={() => {
              signOut();
              localStorage.removeItem('token');
              addToast('Signed out successfully', 'success');
              onAuthChange?.();
            }}
          >
            Sign Out
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl font-bold">{isLogin ? 'Sign In' : 'Sign Up'}</CardTitle>
        <CardDescription>
          {isLogin ? 'Sign in to your account' : 'Create a new account'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
            minLength={6}
          />

          <Button
            type="submit"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            {isLoading ? (isLogin ? 'Signing In...' : 'Signing Up...') : (isLogin ? 'Sign In' : 'Sign Up')}
          </Button>
        </form>

        <div className="mt-4 text-center text-sm">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
            }}
            className="text-primary hover:underline"
          >
            {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
          </button>
        </div>
      </CardContent>
    </Card>
  );
}