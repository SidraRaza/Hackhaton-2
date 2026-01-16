/**
 * Frontend integration tests for task management UI
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act } from 'react-dom/test-utils';

// Mock the API calls
vi.mock('../lib/api', () => ({
  getTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  toggleTaskCompletion: vi.fn(),
}));

import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';
import TaskItem from '../components/TaskItem';

// Sample test data
const mockTasks = [
  {
    id: 1,
    title: 'Test Task 1',
    description: 'Test Description 1',
    completed: false,
    user_id: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'Test Task 2',
    description: 'Test Description 2',
    completed: true,
    user_id: 1,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
];

describe('Task Management UI Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  describe('TaskList Component', () => {
    it('should render tasks correctly', async () => {
      const { getTasks } = await import('../lib/api');
      (getTasks as jest.MockedFunction<any>).mockResolvedValue(mockTasks);

      await act(async () => {
        render(<TaskList userId={1} />);
      });

      // Verify tasks are displayed
      expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      expect(screen.getByText('Test Task 2')).toBeInTheDocument();

      // Verify completed task is marked as completed
      const completedTask = screen.getByText('Test Task 2');
      expect(completedTask).toHaveClass('line-through');
    });

    it('should handle loading state', async () => {
      const { getTasks } = await import('../lib/api');
      (getTasks as jest.MockedFunction<any>).mockImplementation(() => new Promise(() => {})); // Never resolves

      await act(async () => {
        render(<TaskList userId={1} />);
      });

      // Verify loading state is shown
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('should handle error state', async () => {
      const { getTasks } = await import('../lib/api');
      (getTasks as jest.MockedFunction<any>).mockRejectedValue(new Error('Failed to fetch'));

      await act(async () => {
        render(<TaskList userId={1} />);
      });

      // Verify error state is shown
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  describe('TaskForm Component', () => {
    it('should allow creating new tasks', async () => {
      const { createTask } = await import('../lib/api');
      const mockCreateTask = (createTask as jest.MockedFunction<any>);
      mockCreateTask.mockResolvedValue({
        id: 3,
        title: 'New Task',
        description: 'New Description',
        completed: false,
        user_id: 1,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });

      const onTaskAdded = vi.fn();
      const { getByLabelText, getByRole, getByText } = render(
        <TaskForm onTaskAdded={onTaskAdded} />
      );

      // Fill in form fields
      fireEvent.change(getByLabelText(/title/i), { target: { value: 'New Task' } });
      fireEvent.change(getByLabelText(/description/i), { target: { value: 'New Description' } });

      // Submit form
      fireEvent.click(getByRole('button', { name: /add task/i }));

      // Wait for the API call to complete
      await waitFor(() => {
        expect(createTask).toHaveBeenCalledWith({
          title: 'New Task',
          description: 'New Description',
          user_id: 1,
        });
        expect(onTaskAdded).toHaveBeenCalled();
      });
    });

    it('should show validation errors', async () => {
      const { getByRole } = render(<TaskForm onTaskAdded={() => {}} />);

      // Submit form without filling in required fields
      fireEvent.click(getByRole('button', { name: /add task/i }));

      // Verify validation error is shown
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('TaskItem Component', () => {
    it('should display task information correctly', () => {
      const mockTask = mockTasks[0];
      const { getByText } = render(<TaskItem task={mockTask} />);

      expect(getByText('Test Task 1')).toBeInTheDocument();
      expect(getByText('Test Description 1')).toBeInTheDocument();
    });

    it('should handle task completion toggle', async () => {
      const { toggleTaskCompletion } = await import('../lib/api');
      (toggleTaskCompletion as jest.MockedFunction<any>).mockResolvedValue({
        ...mockTasks[0],
        completed: true,
      });

      const mockOnToggle = vi.fn();
      const { getByRole } = render(
        <TaskItem task={mockTasks[0]} onToggleCompletion={mockOnToggle} />
      );

      // Click the completion toggle
      fireEvent.click(getByRole('checkbox'));

      // Wait for the API call to complete
      await waitFor(() => {
        expect(toggleTaskCompletion).toHaveBeenCalledWith(mockTasks[0].id);
        expect(mockOnToggle).toHaveBeenCalledWith(mockTasks[0].id, true);
      });
    });

    it('should handle task deletion', async () => {
      const { deleteTask } = await import('../lib/api');
      (deleteTask as jest.MockedFunction<any>).mockResolvedValue(undefined);

      const mockOnDelete = vi.fn();
      const { getByRole } = render(
        <TaskItem task={mockTasks[0]} onDelete={mockOnDelete} />
      );

      // Click the delete button
      fireEvent.click(getByRole('button', { name: /delete/i }));

      // Wait for the API call to complete
      await waitFor(() => {
        expect(deleteTask).toHaveBeenCalledWith(mockTasks[0].id);
        expect(mockOnDelete).toHaveBeenCalledWith(mockTasks[0].id);
      });
    });

    it('should show completed tasks with strikethrough', () => {
      const completedTask = mockTasks[1]; // This task is completed
      const { getByText } = render(<TaskItem task={completedTask} />);

      const taskElement = getByText('Test Task 2');
      expect(taskElement).toHaveStyle('text-decoration: line-through');
    });
  });

  describe('Integration Tests', () => {
    it('should create, update, and delete tasks in sequence', async () => {
      // Mock all API calls
      const { getTasks, createTask, updateTask, deleteTask, toggleTaskCompletion } = await import('../lib/api');

      (getTasks as jest.MockedFunction<any>).mockResolvedValue([]);
      (createTask as jest.MockedFunction<any>).mockResolvedValue({
        id: 1,
        title: 'Integration Test Task',
        description: 'Integration test description',
        completed: false,
        user_id: 1,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });
      (updateTask as jest.MockedFunction<any>).mockResolvedValue({
        id: 1,
        title: 'Updated Integration Test Task',
        description: 'Updated integration test description',
        completed: false,
        user_id: 1,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });
      (deleteTask as jest.MockedFunction<any>).mockResolvedValue(undefined);
      (toggleTaskCompletion as jest.MockedFunction<any>).mockResolvedValue({
        id: 1,
        title: 'Updated Integration Test Task',
        description: 'Updated integration test description',
        completed: true,
        user_id: 1,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });

      // Render the components
      const onTaskAdded = vi.fn();
      const onTaskUpdated = vi.fn();
      const onTaskDeleted = vi.fn();
      const onTaskToggled = vi.fn();

      // First, add a task
      const { getByLabelText, getByRole, rerender } = render(
        <TaskForm onTaskAdded={onTaskAdded} />
      );

      fireEvent.change(getByLabelText(/title/i), { target: { value: 'Integration Test Task' } });
      fireEvent.change(getByLabelText(/description/i), { target: { value: 'Integration test description' } });
      fireEvent.click(getByRole('button', { name: /add task/i }));

      await waitFor(() => {
        expect(createTask).toHaveBeenCalled();
        expect(onTaskAdded).toHaveBeenCalled();
      });

      // Then, render the task item to test update/delete
      const taskItem = render(
        <TaskItem
          task={{
            id: 1,
            title: 'Integration Test Task',
            description: 'Integration test description',
            completed: false,
            user_id: 1,
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z'
          }}
          onUpdate={onTaskUpdated}
          onDelete={onTaskDeleted}
          onToggleCompletion={onTaskToggled}
        />
      );

      // Test completion toggle
      fireEvent.click(taskItem.getByRole('checkbox'));
      await waitFor(() => {
        expect(toggleTaskCompletion).toHaveBeenCalledWith(1);
        expect(onTaskToggled).toHaveBeenCalledWith(1, true);
      });

      // Test deletion
      fireEvent.click(taskItem.getByRole('button', { name: /delete/i }));
      await waitFor(() => {
        expect(deleteTask).toHaveBeenCalledWith(1);
        expect(onTaskDeleted).toHaveBeenCalledWith(1);
      });
    });
  });
});