/**
 * Frontend authentication flow tests
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act } from 'react-dom/test-utils';

// Mock the auth context and API calls
vi.mock('../lib/auth', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('../lib/api', () => ({
  signIn: vi.fn(),
  signOut: vi.fn(),
  signUp: vi.fn(),
}));

import AuthComponent from '../components/AuthComponent';

describe('Authentication Flow Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Mock useAuth hook
    const { useAuth } = require('../lib/auth');
    (useAuth as jest.MockedFunction<any>).mockReturnValue({
      user: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      isAuthenticated: false,
    });
  });

  describe('Registration Flow', () => {
    it('should allow new user registration', async () => {
      const { signUp } = await import('../lib/api');
      const mockSignUp = (signUp as jest.MockedFunction<any>);
      mockSignUp.mockResolvedValue({
        user: { email: 'newuser@example.com' },
        token: 'mock-token',
      });

      const mockOnAuthChange = vi.fn();

      const { getByLabelText, getByRole } = render(
        <AuthComponent onAuthChange={mockOnAuthChange} />
      );

      // Switch to sign up mode
      fireEvent.click(screen.getByText(/don't have an account\? sign up/i));

      // Fill in registration form
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'newuser@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'SecurePassword123!' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /sign up/i }));

      // Wait for the registration to complete
      await waitFor(() => {
        expect(signUp).toHaveBeenCalledWith({
          email: 'newuser@example.com',
          password: 'SecurePassword123!',
        });
        expect(mockOnAuthChange).toHaveBeenCalled();
      });
    });

    it('should show validation errors for weak passwords', async () => {
      const { getByLabelText, getByRole } = render(<AuthComponent onAuthChange={() => {}} />);

      // Switch to sign up mode
      fireEvent.click(screen.getByText(/don't have an account\? sign up/i));

      // Fill in with weak password
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'user@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'weak' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /sign up/i }));

      // Wait for validation error
      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    it('should show error for duplicate email registration', async () => {
      const { signUp } = await import('../lib/api');
      (signUp as jest.MockedFunction<any>).mockRejectedValue(
        new Error('Email already exists')
      );

      const { getByLabelText, getByRole } = render(<AuthComponent onAuthChange={() => {}} />);

      // Switch to sign up mode
      fireEvent.click(screen.getByText(/don't have an account\? sign up/i));

      // Fill in form
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'existing@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'SecurePassword123!' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /sign up/i }));

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
      });
    });
  });

  describe('Login Flow', () => {
    it('should allow existing user login', async () => {
      const { signIn } = await import('../lib/api');
      (signIn as jest.MockedFunction<any>).mockResolvedValue({
        user: { email: 'existing@example.com' },
        token: 'mock-token',
      });

      const mockOnAuthChange = vi.fn();

      const { getByLabelText, getByRole } = render(
        <AuthComponent onAuthChange={mockOnAuthChange} />
      );

      // Fill in login form
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'existing@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'ValidPassword123!' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /sign in/i }));

      // Wait for login to complete
      await waitFor(() => {
        expect(signIn).toHaveBeenCalledWith({
          email: 'existing@example.com',
          password: 'ValidPassword123!',
        });
        expect(mockOnAuthChange).toHaveBeenCalled();
      });
    });

    it('should show error for invalid credentials', async () => {
      const { signIn } = await import('../lib/api');
      (signIn as jest.MockedFunction<any>).mockRejectedValue(
        new Error('Invalid credentials')
      );

      const { getByLabelText, getByRole } = render(<AuthComponent onAuthChange={() => {}} />);

      // Fill in with invalid credentials
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'nonexistent@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'WrongPassword!' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /sign in/i }));

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('should show validation errors for empty fields', async () => {
      const { getByRole } = render(<AuthComponent onAuthChange={() => {}} />);

      // Submit form without filling in fields
      fireEvent.click(getByRole('button', { name: /sign in/i }));

      // Wait for validation errors
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Logout Flow', () => {
    beforeEach(() => {
      // Mock authenticated user
      const { useAuth } = require('../lib/auth');
      (useAuth as jest.MockedFunction<any>).mockReturnValue({
        user: { email: 'loggedin@example.com' },
        signIn: vi.fn(),
        signOut: vi.fn(),
        isAuthenticated: true,
      });
    });

    it('should allow user logout', async () => {
      const { signOut } = await import('../lib/api');
      (signOut as jest.MockedFunction<any>).mockResolvedValue(undefined);

      const mockOnAuthChange = vi.fn();

      const { getByText } = render(
        <AuthComponent onAuthChange={mockOnAuthChange} />
      );

      // Click logout button
      fireEvent.click(getByText(/sign out/i));

      // Wait for logout to complete
      await waitFor(() => {
        expect(signOut).toHaveBeenCalled();
        expect(mockOnAuthChange).toHaveBeenCalled();
      });
    });
  });

  describe('UI State Transitions', () => {
    it('should switch between login and registration forms', () => {
      const { getByText } = render(<AuthComponent onAuthChange={() => {}} />);

      // Verify initial state is login
      expect(getByText(/sign in/i)).toBeInTheDocument();
      expect(getByText(/don't have an account\? sign up/i)).toBeInTheDocument();

      // Click to switch to registration
      fireEvent.click(getByText(/don't have an account\? sign up/i));

      // Verify switched to registration state
      expect(getByText(/sign up/i)).toBeInTheDocument();
      expect(getByText(/already have an account\? sign in/i)).toBeInTheDocument();

      // Click to switch back to login
      fireEvent.click(getByText(/already have an account\? sign in/i));

      // Verify switched back to login state
      expect(getByText(/sign in/i)).toBeInTheDocument();
      expect(getByText(/don't have an account\? sign up/i)).toBeInTheDocument();
    });

    it('should show welcome message when authenticated', () => {
      // Mock authenticated user
      const { useAuth } = require('../lib/auth');
      (useAuth as jest.MockedFunction<any>).mockReturnValue({
        user: { email: 'welcome@example.com' },
        signIn: vi.fn(),
        signOut: vi.fn(),
        isAuthenticated: true,
      });

      const { getByText } = render(<AuthComponent onAuthChange={() => {}} />);

      // Verify welcome message is shown
      expect(getByText(/welcome, welcome@example.com/i)).toBeInTheDocument();
      expect(getByText(/sign out/i)).toBeInTheDocument();
    });

    it('should show loading state during authentication', () => {
      // Mock loading state
      const { useAuth } = require('../lib/auth');
      (useAuth as jest.MockedFunction<any>).mockReturnValue({
        user: null,
        signIn: vi.fn(),
        signOut: vi.fn(),
        isAuthenticated: false,
        isLoading: true,
      });

      const { getByText } = render(<AuthComponent onAuthChange={() => {}} />);

      // Verify loading state is shown
      expect(getByText(/loading\.\.\./i)).toBeInTheDocument();
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete authentication flow: register -> login -> logout', async () => {
      const { signUp, signIn, signOut } = await import('../lib/api');

      // Mock all API calls
      (signUp as jest.MockedFunction<any>).mockResolvedValue({
        user: { email: 'integration@example.com' },
        token: 'mock-token-1',
      });
      (signIn as jest.MockedFunction<any>).mockResolvedValue({
        user: { email: 'integration@example.com' },
        token: 'mock-token-2',
      });
      (signOut as jest.MockedFunction<any>).mockResolvedValue(undefined);

      const mockOnAuthChange = vi.fn();

      // Step 1: Register new user
      const { getByLabelText, getByRole, rerender } = render(
        <AuthComponent onAuthChange={mockOnAuthChange} />
      );

      // Switch to registration
      fireEvent.click(screen.getByText(/don't have an account\? sign up/i));

      // Fill registration form
      fireEvent.change(getByLabelText(/email/i), { target: { value: 'integration@example.com' } });
      fireEvent.change(getByLabelText(/password/i), { target: { value: 'SecurePassword123!' } });
      fireEvent.click(getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(signUp).toHaveBeenCalledWith({
          email: 'integration@example.com',
          password: 'SecurePassword123!',
        });
        expect(mockOnAuthChange).toHaveBeenCalled();
      });

      // Step 2: Simulate successful registration by updating the mock
      const { useAuth } = require('../lib/auth');
      (useAuth as jest.MockedFunction<any>).mockReturnValue({
        user: { email: 'integration@example.com' },
        signIn: vi.fn(),
        signOut: vi.fn(),
        isAuthenticated: true,
      });

      // Re-render to reflect authenticated state
      rerender(<AuthComponent onAuthChange={mockOnAuthChange} />);

      // Verify authenticated state
      expect(screen.getByText(/welcome, integration@example.com/i)).toBeInTheDocument();

      // Step 3: Logout
      fireEvent.click(screen.getByText(/sign out/i));

      await waitFor(() => {
        expect(signOut).toHaveBeenCalled();
        expect(mockOnAuthChange).toHaveBeenCalledTimes(2);
      });
    });
  });
});