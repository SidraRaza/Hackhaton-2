'use client';

import React from 'react';
import { TaskApiResponse } from '@/frontend/src/lib/types';
import { TaskCard } from './TaskCard';

interface TodoListProps {
  todos: TaskApiResponse[];
  onEdit: (todo: TaskApiResponse) => void;
  onDelete: (id: string) => void;
  onComplete: (id: string, completed: boolean) => void;
}

const TodoList: React.FC<TodoListProps> = ({ todos, onEdit, onDelete, onComplete }) => {
  // Separate completed and pending todos
  const pendingTodos = todos.filter(todo => todo.status !== 'completed');
  const completedTodos = todos.filter(todo => todo.status === 'completed');

  return (
    <div className="space-y-4">
      {/* Pending Todos Section */}
      {pendingTodos.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Pending Tasks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pendingTodos.map(todo => (
              <TaskCard
                key={todo.id}
                task={todo}
                onEdit={() => onEdit(todo)}
                onDelete={() => onDelete(todo.id)}
                onComplete={(completed) => onComplete(todo.id, completed)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Todos Section */}
      {completedTodos.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Completed Tasks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedTodos.map(todo => (
              <TaskCard
                key={todo.id}
                task={todo}
                onEdit={() => onEdit(todo)}
                onDelete={() => onDelete(todo.id)}
                onComplete={(completed) => onComplete(todo.id, completed)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {todos.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No tasks yet. Add your first task!</p>
        </div>
      )}
    </div>
  );
};

export default TodoList;