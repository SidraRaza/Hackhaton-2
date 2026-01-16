'use client';

import { useSession } from '../lib/better-auth-client';
import AuthComponent from '../components/AuthComponent';
import TaskList from '../components/TaskList';
import { useAuth } from '../lib/auth';

export default function Home() {
  const { data: session, isPending } = useSession();
  const { isAuthenticated } = useAuth();

  if (isPending) {
    return <div className="flex justify-center items-center min-h-screen">
      <p>Loading...</p>
    </div>;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Hackathon Todo App</h1>
        <p className="text-gray-600">A full-stack todo application with authentication</p>
      </header>

      {!isAuthenticated ? (
        <div className="flex justify-center">
          <AuthComponent />
        </div>
      ) : (
        <div>
          <div className="mb-8 p-4 bg-white rounded-lg shadow-sm">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-800">Welcome back!</h2>
              <div className="text-right">
                <p className="text-gray-600">Signed in as:</p>
                <p className="font-medium">{session?.user?.email}</p>
              </div>
            </div>
          </div>

          <TaskList userId={session?.user?.id ? Number(session.user.id) : 0} />
        </div>
      )}
    </div>
  );
}