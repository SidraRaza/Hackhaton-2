'use client';

import { AnalyticsDashboard } from '@/components/tasks/AnalyticsDashboard';

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">Task Analytics</h1>
          <p className="text-sm text-gray-600 mt-1">
            Insights about your task completion patterns and productivity
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <AnalyticsDashboard />
      </main>
    </div>
  );
}