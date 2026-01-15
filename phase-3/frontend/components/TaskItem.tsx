import { useState } from 'react';
import { Task } from '../types';

interface TaskItemProps {
  task: Task;
  onTaskUpdated: (updatedTask: Task) => void;
  onTaskDeleted: (taskId: number) => void;
}

export default function TaskItem({ task, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggleComplete = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`/api/tasks/${task.id}/complete`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to update task: ${response.statusText}`);
      }

      const updatedTask: Task = await response.json();
      onTaskUpdated(updatedTask);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      setTimeout(() => setError(null), 3000); // Clear error after 3 seconds
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: editTitle,
          description: editDescription,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update task: ${response.statusText}`);
      }

      const updatedTask: Task = await response.json();
      onTaskUpdated(updatedTask);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      setTimeout(() => setError(null), 3000); // Clear error after 3 seconds
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete task: ${response.statusText}`);
      }

      onTaskDeleted(task.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      setTimeout(() => setError(null), 3000); // Clear error after 3 seconds
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <li className={`border rounded-lg p-4 ${task.completed ? 'bg-green-50' : 'bg-white'}`}>
      {isEditing ? (
        <form onSubmit={handleEditSubmit} className="space-y-3">
          <div>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded mb-2"
              required
            />
          </div>
          <div>
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded mb-2"
              placeholder="Description (optional)"
            />
          </div>
          <div className="flex space-x-2">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                setEditTitle(task.title);
                setEditDescription(task.description || '');
              }}
              className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={handleToggleComplete}
              disabled={isLoading}
              className="mt-1 h-4 w-4 text-blue-600 rounded"
            />
            <div>
              <h3 className={`${task.completed ? 'line-through text-gray-500' : ''}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`text-sm mt-1 ${task.completed ? 'line-through text-gray-500' : 'text-gray-600'}`}>
                  {task.description}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">
                Created: {new Date(task.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              className="text-blue-500 hover:text-blue-700 text-sm px-2 py-1 rounded disabled:opacity-50"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="text-red-500 hover:text-red-700 text-sm px-2 py-1 rounded disabled:opacity-50"
            >
              Delete
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-2 p-2 bg-red-100 text-red-700 text-sm rounded">
          {error}
        </div>
      )}
    </li>
  );
}