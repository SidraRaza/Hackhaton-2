'use client';

import React, { useState } from 'react';
import Sidebar from '../../components/Sidebar';
import TopNavbar from '../../components/TopNavbar';
import { TaskCard } from '../../components/TaskCard';
import { Button } from '../../components/ui/button';
import { Plus } from 'lucide-react';
import { TaskApiResponse } from '../../lib/types';

// Mock data for completed tasks
const mockCompletedTasks: TaskApiResponse[] = [
  {
    id: '1',
    title: 'Review documentation',
    priority: 'low',
    status: 'completed',
    dueDate: '2024-01-24',
    createdAt: '2024-01-24T14:20:00Z',
    updatedAt: '2024-01-24T14:20:00Z',
  },
  {
    id: '2',
    title: 'Submit monthly report',
    description: 'Submit the monthly progress report to management',
    priority: 'medium',
    status: 'completed',
    dueDate: '2024-01-20',
    createdAt: '2024-01-20T09:15:00Z',
    updatedAt: '2024-01-20T09:15:00Z',
  },
];

export default function CompletedPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [tasks, setTasks] = useState<TaskApiResponse[]>(mockCompletedTasks);

  const handleAddTask = () => {
    // Mock adding a new task
    const newTask: TaskApiResponse = {
      id: (tasks.length + 1).toString(),
      title: 'New task',
      description: 'Description for new task',
      priority: 'medium',
      status: 'todo',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // In 7 days
    };
    setTasks([...tasks, newTask]);
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onCollapseToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main content */}
      <main className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        {/* Top Navbar */}
        <TopNavbar
          user={{
            name: 'John Doe',
            email: 'john@example.com',
            avatar: '/placeholder-avatar.jpg',
          }}
        />

        {/* Completed tasks content */}
        <div className="p-6">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-foreground">Completed Tasks</h1>
            <Button onClick={handleAddTask}>
              <Plus className="mr-2 h-4 w-4" /> Add Task
            </Button>
          </div>

          {tasks.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No completed tasks yet. Keep going!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {tasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}