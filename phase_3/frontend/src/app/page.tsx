'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopNavbar from '../components/TopNavbar';
import { Button } from '../components/ui/button';
import { Plus } from 'lucide-react';
import { TaskApiResponse } from '../lib/types';
import type { Task as TaskType } from '../lib/tasks';
import { FloatingChatButton } from '../components/FloatingChatButton';
import { ChatPanel } from '../components/ChatPanel';
import TodoForm from '../components/TodoForm';
import TodoList from '../components/TodoList';
import { useTasks } from '../lib/tasks';
import { useAuth } from '../lib/auth';

type TodoFormData = Omit<
  TaskType,
  'id' | 'createdAt' | 'updatedAt' | 'completedAt' | 'userId'
>;

export default function DashboardPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskType | null>(null);

  const { tasks, isLoading: loading, addTask, updateTask, deleteTask } = useTasks();

  // ✅ CREATE
  const handleAddTodo = async (data: TodoFormData) => {
    try {
      await addTask(data);
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to add task:', error);
    }
  };

  // ✅ UPDATE (merge form data with existing task)
  const handleUpdateTodo = async (data: TodoFormData) => {
    if (!editingTask) return;

    try {
      await updateTask(editingTask.id, data);
      setEditingTask(null);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDeleteTodo = async (id: string) => {
    try {
      await deleteTask(id);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleToggleStatus = async (id: string, completed: boolean) => {
    try {
      const task = tasks.find(t => t.id === id);
      if (!task) return;

      await updateTask(id, {
        status: completed ? 'completed' : 'pending',
      });
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onCollapseToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      <main
        className={`flex-1 transition-all duration-300 bg-background ${
          isSidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}
      >
        <TopNavbar />

        <div className="p-xl">
          <div className="mb-lg flex justify-between items-center">
            <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>

            {showAddForm ? (
              <Button variant="outline" onClick={() => setShowAddForm(false)} className="bg-background text-foreground border-border hover:bg-muted">
                Cancel
              </Button>
            ) : (
              <Button
                onClick={() => setShowAddForm(true)}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Plus className="mr-2 h-4 w-4" /> Add Task
              </Button>
            )}
          </div>

          {loading ? (
            <div className="h-64 flex items-center justify-center bg-background rounded-lg border border-border">
              Loading tasks...
            </div>
          ) : (
            <>
              {showAddForm && !editingTask && (
                <div className="mb-lg bg-background rounded-lg border border-border p-lg shadow-none">
                  <TodoForm
                    onSubmit={handleAddTodo}
                    onCancel={() => setShowAddForm(false)}
                    submitText="Add Task"
                  />
                </div>
              )}

              {editingTask && (
                <div className="mb-lg bg-background rounded-lg border border-border p-lg shadow-none">
                  <TodoForm
                    onSubmit={handleUpdateTodo}
                    onCancel={() => setEditingTask(null)}
                    submitText="Update Task"
                    defaultValue={{
                      title: editingTask.title,
                      description: editingTask.description ?? '',
                      priority: editingTask.priority,
                    }}
                  />
                </div>
              )}

              <div className="bg-background rounded-lg border border-border p-lg shadow-none">
                <TodoList
                  todos={tasks}
                  onEdit={setEditingTask}
                  onDelete={handleDeleteTodo}
                  onComplete={handleToggleStatus}
                />
              </div>
            </>
          )}
        </div>

        <FloatingChatButton
          isOpen={isChatOpen}
          onToggle={() => setIsChatOpen(!isChatOpen)}
        />

        <ChatPanel
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />
      </main>
    </div>
  );
}
