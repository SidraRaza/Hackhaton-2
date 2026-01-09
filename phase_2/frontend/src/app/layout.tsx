import { AuthProvider } from '../lib/auth';
import { TasksProvider } from '../lib/tasks';
import '../styles/globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <AuthProvider>
          <TasksProvider>
            <div className="min-h-screen bg-gray-50">
              {children}
            </div>
          </TasksProvider>
        </AuthProvider>
      </body>
    </html>
  );
}