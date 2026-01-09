'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl">
        <div className="p-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Todo App</h1>
            <p className="text-gray-600 mb-8">Manage your tasks efficiently and boost productivity</p>

            <div className="space-y-4">
              <Link href="/auth/login" className="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition duration-300 ease-in-out transform hover:scale-105">
                Sign In
              </Link>

              <Link href="/auth/register" className="block w-full py-3 px-4 bg-white border border-gray-300 hover:bg-gray-50 text-gray-800 font-medium rounded-lg transition duration-300">
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}