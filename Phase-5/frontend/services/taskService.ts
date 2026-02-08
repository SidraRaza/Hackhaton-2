import { apiClient } from '../lib/api';

// Define enums to match backend
export enum PriorityEnum {
  low = "low",
  medium = "medium",
  high = "high"
}

export enum RecurrencePatternEnum {
  daily = "daily",
  weekly = "weekly",
  monthly = "monthly",
  yearly = "yearly",
  custom = "custom"
}

// Define interfaces to match backend models
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: PriorityEnum;
  due_date?: string;
  recurrence_pattern?: RecurrencePatternEnum;
  recurrence_config?: any;
  tag_ids?: number[];
  parent_task_id?: number;
  next_occurrence?: string;
  occurrences_remaining?: number;
  reminder_times?: string[];
  last_reminder_sent?: string;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface TaskFilters {
  priority?: PriorityEnum[];
  tags?: number[];
  search?: string;
  due_date_from?: string;
  due_date_to?: string;
  recurrence_pattern?: RecurrencePatternEnum;
  status_filter?: 'pending' | 'completed' | 'all';
  sort?: 'priority' | 'due_date' | 'created_at' | 'title' | 'completed';
  sort_order?: 'asc' | 'desc';
  secondary_sort?: 'priority' | 'due_date' | 'created_at' | 'title' | 'completed';
  secondary_sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
  use_saved_filters?: boolean;
  save_filters?: boolean;
  // Additional parameters for advanced search functionality
  completed?: boolean;
  has_due_date?: boolean;
  overdue?: boolean;
}

export interface TaskCreationData {
  title: string;
  description?: string;
  priority?: PriorityEnum;
  due_date?: string;
  recurrence_pattern?: RecurrencePatternEnum;
  recurrence_config?: any;
  tag_ids?: number[];
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: PriorityEnum;
  due_date?: string;
  recurrence_pattern?: RecurrencePatternEnum;
  recurrence_config?: any;
  tag_ids?: number[];
}

export class TaskService {
  /**
   * Get all tasks for the current user with advanced filtering and sorting
   */
  static async getAllTasks(filters?: TaskFilters): Promise<Task[]> {
    // Build query parameters from filters
    const queryParams = new URLSearchParams();

    if (filters) {
      if (filters.priority) {
        filters.priority.forEach(p => queryParams.append('priority', p));
      }
      if (filters.tags) {
        filters.tags.forEach(t => queryParams.append('tags', t.toString()));
      }
      if (filters.search) {
        queryParams.set('search', filters.search);
      }
      if (filters.due_date_from) {
        queryParams.set('due_date_from', filters.due_date_from);
      }
      if (filters.due_date_to) {
        queryParams.set('due_date_to', filters.due_date_to);
      }
      if (filters.recurrence_pattern) {
        queryParams.set('recurrence_pattern', filters.recurrence_pattern);
      }
      if (filters.status_filter) {
        queryParams.set('status_filter', filters.status_filter);
      }
      if (filters.sort) {
        queryParams.set('sort', filters.sort);
      }
      if (filters.sort_order) {
        queryParams.set('sort_order', filters.sort_order);
      }
      if (filters.secondary_sort) {
        queryParams.set('secondary_sort', filters.secondary_sort);
      }
      if (filters.secondary_sort_order) {
        queryParams.set('secondary_sort_order', filters.secondary_sort_order);
      }
      if (filters.limit) {
        queryParams.set('limit', filters.limit.toString());
      }
      if (filters.offset) {
        queryParams.set('offset', filters.offset.toString());
      }
      if (filters.use_saved_filters !== undefined) {
        queryParams.set('use_saved_filters', filters.use_saved_filters.toString());
      }
      if (filters.save_filters !== undefined) {
        queryParams.set('save_filters', filters.save_filters.toString());
      }
      if (filters.completed !== undefined) {
        queryParams.set('completed', filters.completed.toString());
      }
      if (filters.has_due_date !== undefined) {
        queryParams.set('has_due_date', filters.has_due_date.toString());
      }
      if (filters.overdue !== undefined) {
        queryParams.set('overdue', filters.overdue.toString());
      }
    }

    const queryString = queryParams.toString();
    const endpoint = `/tasks${queryString ? '?' + queryString : ''}`;

    return await apiClient.get<Task[]>(endpoint);
  }

  /**
   * Get a specific task by ID
   */
  static async getTaskById(taskId: number): Promise<Task> {
    return await apiClient.get<Task>(`/tasks/${taskId}`);
  }

  /**
   * Create a new task with advanced features
   */
  static async createTask(taskData: TaskCreationData): Promise<Task> {
    return await apiClient.post<Task>('/tasks', taskData);
  }

  /**
   * Update an existing task with advanced features
   */
  static async updateTask(taskId: number, taskData: TaskUpdateData): Promise<Task> {
    return await apiClient.put<Task>(`/tasks/${taskId}`, taskData);
  }

  /**
   * Delete a task
   */
  static async deleteTask(taskId: number): Promise<any> {
    return await apiClient.delete(`/tasks/${taskId}`);
  }

  /**
   * Toggle task completion status
   */
  static async toggleTaskCompletion(taskId: number, completed: boolean): Promise<Task> {
    return await apiClient.patch<Task>(`/tasks/${taskId}/complete`, { completed });
  }

  /**
   * Complete a recurring task with advanced options
   */
  static async completeRecurringTask(taskId: number, options: {
    mark_series_complete?: boolean;
    modify_future_occurrences?: boolean;
    skip_next_occurrence?: boolean;
    recurrence_action?: string;
    create_next_occurrence?: boolean;
  }): Promise<Task> {
    return await apiClient.post<Task>(`/tasks/${taskId}/complete-recurrence`, options);
  }

  /**
   * Get all tags for the current user
   */
  static async getTags(): Promise<Tag[]> {
    return await apiClient.get<Tag[]>('/tags');
  }

  /**
   * Get a specific tag by ID
   */
  static async getTagById(tagId: number): Promise<Tag> {
    return await apiClient.get<Tag>(`/tags/${tagId}`);
  }

  /**
   * Create a new tag
   */
  static async createTag(tagData: Partial<Tag>): Promise<Tag> {
    return await apiClient.post<Tag>('/tags', tagData);
  }

  /**
   * Update an existing tag
   */
  static async updateTag(tagId: number, tagData: Partial<Tag>): Promise<Tag> {
    return await apiClient.put<Tag>(`/tags/${tagId}`, tagData);
  }

  /**
   * Delete a tag
   */
  static async deleteTag(tagId: number): Promise<any> {
    return await apiClient.delete(`/tags/${tagId}`);
  }
}

// Define interface for analytics data
export interface TaskAnalytics {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  priority_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  weekly_completion_trend: Array<{
    week: string;
    completed: number;
    pending: number;
  }>;
  tag_completion_stats: Array<{
    tag_name: string;
    completed: number;
    total: number;
  }>;
}

/**
 * Additional service methods for analytics
 */
export class AnalyticsService {
  /**
   * Get task analytics and insights
   */
  static async getTaskAnalytics(params?: {
    period?: 'week' | 'month' | 'quarter' | 'year';
    start_date?: string;
    end_date?: string;
  }): Promise<TaskAnalytics> {
    const queryParams = new URLSearchParams();

    if (params) {
      if (params.period) {
        queryParams.set('period', params.period);
      }
      if (params.start_date) {
        queryParams.set('start_date', params.start_date);
      }
      if (params.end_date) {
        queryParams.set('end_date', params.end_date);
      }
    }

    const queryString = queryParams.toString();
    const endpoint = `/tasks/analytics${queryString ? '?' + queryString : ''}`;

    return await apiClient.get<TaskAnalytics>(endpoint);
  }

  /**
   * Get search suggestions based on partial query
   */
  static async getSearchSuggestions(query: string): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>(`/tasks/search/suggestions?q=${encodeURIComponent(query)}`);
      return response || [];
    } catch (error) {
      console.error('Failed to get search suggestions:', error);
      // Return empty array if API fails, the hook will provide fallback
      return [];
    }
  }
}