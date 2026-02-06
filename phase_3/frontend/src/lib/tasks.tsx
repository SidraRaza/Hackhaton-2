'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './auth';
import toast from 'react-hot-toast';
import { taskApi } from './api';

// Utility function to convert snake_case to camelCase
function snakeToCamel(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(snakeToCamel);
  }

  const camelObj: any = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      camelObj[camelKey] = snakeToCamel(obj[key]);
    }
  }
  return camelObj;
}

// Utility function to convert camelCase to snake_case
function camelToSnake(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(camelToSnake);
  }

  const snakeObj: any = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const snakeKey = key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
      snakeObj[snakeKey] = camelToSnake(obj[key]);
    }
  }
  return snakeObj;
}

interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
  userId: string;
}

interface TaskCreateData {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

interface TaskUpdateData {
  title?: string;
  description?: string;
  status?: 'pending' | 'in-progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

interface TasksContextType {
  tasks: Task[];
  addTask: (data: TaskCreateData) => Promise<void>;
  updateTask: (id: string, data: TaskUpdateData) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const TasksContext = createContext<TasksContextType | undefined>(undefined);

export function TasksProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user]);

  const fetchTasks = async () => {
    if (!user) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await taskApi.getAll();
      const tasksData = Array.isArray(response.data) ? response.data : [];
      const camelCaseTasks = tasksData.map(snakeToCamel);
      setTasks(camelCaseTasks);
    } catch (err: any) {
      console.error('Error fetching tasks:', err);
      let errorMessage = 'Network error occurred while fetching tasks';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const addTask = async (data: TaskCreateData) => {
    try {
      const snakeCaseData = camelToSnake(data);
      const response = await taskApi.create(snakeCaseData);
      const newTask = snakeToCamel(response.data);
      setTasks(prev => [newTask, ...prev]);
      toast.success('Task added successfully!');
      return newTask;
    } catch (error: any) {
      console.error('Error adding task:', error);
      let errorMessage = 'Failed to add task';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const updateTask = async (id: string, data: TaskUpdateData) => {
    try {
      const snakeCaseData = camelToSnake(data);
      const response = await taskApi.update(id, snakeCaseData);
      const updatedTask = snakeToCamel(response.data);
      setTasks(prev => prev.map(task => task.id === id ? updatedTask : task));
      toast.success('Task updated successfully!');
      return updatedTask;
    } catch (error: any) {
      console.error('Error updating task:', error);
      let errorMessage = 'Failed to update task';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const deleteTask = async (id: string) => {
    try {
      const response = await taskApi.delete(id);
      setTasks(prev => prev.filter(task => task.id !== id));
      toast.success('Task deleted successfully!');
    } catch (error: any) {
      console.error('Error deleting task:', error);
      let errorMessage = 'Failed to delete task';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const value = {
    tasks,
    addTask,
    updateTask,
    deleteTask,
    isLoading,
    error,
  };

  return <TasksContext.Provider value={value}>{children}</TasksContext.Provider>;
};

export function useTasks() {
  const context = useContext(TasksContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within a TasksProvider');
  }
  return context;
}