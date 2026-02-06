'use client';

import React, { useState } from 'react';
import { TaskApiResponse } from '../../lib/types';

interface TodoFormProps {
  onSubmit: (data: Omit<TaskApiResponse, 'id' | 'createdAt' | 'updatedAt' | 'completedAt' | 'user_id'>) => void;
  onCancel?: () => void;
  defaultValue?: Partial<{
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
  }>;
  submitText?: string;
}

const TodoForm: React.FC<TodoFormProps> = ({ onSubmit, onCancel, defaultValue, submitText = 'Add Todo' }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: defaultValue?.title || '',
    description: defaultValue?.description || '',
    priority: defaultValue?.priority || 'medium' as 'low' | 'medium' | 'high',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSubmit({
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        status: 'pending', // Default to pending when creating
      });
      setFormData({ title: '', description: '', priority: 'medium' }); // Reset form after successful submission
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-background">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">Title *</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Enter todo title"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">Description</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Enter todo description"
          rows={3}
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium mb-1">Priority *</label>
        <select
          id="priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="flex space-x-2 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className={`px-4 py-2 rounded-md ${isLoading ? 'bg-gray-400' : 'bg-primary text-white hover:bg-primary/90'} focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2`}
        >
          {isLoading ? 'Submitting...' : submitText}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default TodoForm;