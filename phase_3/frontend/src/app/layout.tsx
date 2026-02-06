import { AuthProvider } from '../lib/auth';
import { TasksProvider } from '../lib/tasks';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from '../contexts/ThemeContext';
import '../styles/globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background antialiased">
        <ThemeProvider>
          <AuthProvider>
            <TasksProvider>
              <div className="min-h-screen bg-background">
                {children}
              </div>
              <Toaster position="top-right" toastOptions={{
                style: {
                  background: 'hsl(var(--background))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: 'var(--radius)',
                  padding: '0.75rem',
                  color: 'hsl(var(--foreground))',
                  boxShadow: 'var(--radius)', // Reduced shadow
                },
                success: {
                  style: {
                    background: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--border))',
                    color: 'hsl(var(--primary))',
                  },
                },
                error: {
                  style: {
                    background: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--destructive))',
                    color: 'hsl(var(--destructive))',
                  },
                },
              }} />
            </TasksProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}