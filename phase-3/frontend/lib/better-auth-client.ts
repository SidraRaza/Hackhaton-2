import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  // Add any client configuration here if needed
});

export const { useSession, signIn, signOut } = authClient;