'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { AnalyticsService, TaskAnalytics } from '@/services/taskService';


export const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState<TaskAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        // Fetch actual analytics data from the backend
        const data = await AnalyticsService.getTaskAnalytics();
        setAnalyticsData(data);
        setError(null);
      } catch (err: any) {
        console.error('Failed to load analytics:', err);
        setError('Failed to load analytics data');

        // Fallback to mock data if API fails
        const mockData: TaskAnalytics = {
          total_tasks: 127,
          completed_tasks: 89,
          pending_tasks: 38,
          overdue_tasks: 5,
          completion_rate: 70.1,
          priority_distribution: {
            low: 32,
            medium: 56,
            high: 39
          },
          weekly_completion_trend: [
            { week: 'Week 1', completed: 12, pending: 8 },
            { week: 'Week 2', completed: 15, pending: 5 },
            { week: 'Week 3', completed: 18, pending: 7 },
            { week: 'Week 4', completed: 21, pending: 3 }
          ],
          tag_completion_stats: [
            { tag_name: 'Work', completed: 24, total: 28 },
            { tag_name: 'Personal', completed: 32, total: 40 },
            { tag_name: 'Urgent', completed: 18, total: 20 },
            { tag_name: 'Health', completed: 15, total: 19 }
          ]
        };
        setAnalyticsData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
        {error}
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    );
  }

  // Prepare data for charts

const priorityData = [
  { name: 'Low Priority', value: analyticsData.priority_distribution?.low ?? 0 },
  { name: 'Medium Priority', value: analyticsData.priority_distribution?.medium ?? 0 },
  { name: 'High Priority', value: analyticsData.priority_distribution?.high ?? 0 },
];
  const COLORS = ['#10B981', '#FBBF24', '#EF4444'];
  
const weeklyTrendData = analyticsData.weekly_completion_trend ?? [];

const tagCompletionData = analyticsData.tag_completion_stats?.map(tag => ({
  name: tag.tag_name,
  completed: tag.completed,
  total: tag.total,
  completionRate: tag.total > 0 ? Math.round((tag.completed / tag.total) * 100) : 0
})) ?? [];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Task Analytics</h1>
        <p className="text-gray-600">Insights about your task completion patterns and productivity</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Tasks</CardDescription>
            <CardTitle className="text-2xl">{analyticsData.total_tasks}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">
              All tasks created by you
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-2xl">{analyticsData.completed_tasks}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">
              Tasks you've completed
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Pending</CardDescription>
            <CardTitle className="text-2xl">{analyticsData.pending_tasks}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">
              Tasks awaiting completion
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Completion Rate</CardDescription>
            <CardTitle className="text-2xl">{analyticsData.completion_rate}%</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">
              Overall task completion percentage
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Priority Distribution</CardTitle>
            <CardDescription>Breakdown of tasks by priority level</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Tasks']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Weekly Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Completion Trend</CardTitle>
            <CardDescription>Task completion over the past weeks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={weeklyTrendData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="completed" fill="#10B981" name="Completed Tasks" />
                  <Bar dataKey="pending" fill="#3B82F6" name="Pending Tasks" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tag Completion Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Tag Completion Statistics</CardTitle>
          <CardDescription>Completion rates by tag category</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={tagCompletionData}
                margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={60}
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  tickCount={6}
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip formatter={(value, name) =>
                  name === 'completionRate' ? [`${value}%`, 'Completion Rate'] : [value, name]
                } />
                <Legend />
                <Bar
                  dataKey="completionRate"
                  name="Completion Rate (%)"
                  fill="#8B5CF6"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Productivity Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Productivity Insights</CardTitle>
          <CardDescription>Your task management patterns</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900">Completion Efficiency</h3>
              <p className="text-2xl font-bold text-blue-700">
                {analyticsData.completion_rate}%
              </p>
              <p className="text-sm text-blue-600">
                You complete {analyticsData.completion_rate}% of your tasks
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <h3 className="font-medium text-green-900">Priority Balance</h3>
              <p className="text-2xl font-bold text-green-700">
               {analyticsData.priority_distribution?.high ?? 0}/{analyticsData.priority_distribution?.medium ?? 0}/{analyticsData.priority_distribution?.low ?? 0}
              </p>
              <p className="text-sm text-green-600">
                High/Medium/Low priority ratio
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <h3 className="font-medium text-purple-900">Overdue Tasks</h3>
              <p className="text-2xl font-bold text-purple-700">
                {analyticsData.overdue_tasks}
              </p>
              <p className="text-sm text-purple-600">
                {analyticsData.overdue_tasks > 0
                  ? `Try to reduce overdue tasks`
                  : 'Great job staying on top of deadlines!'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};