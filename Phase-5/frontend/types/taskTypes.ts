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

export interface RecurringTaskCompletionOptions {
  mark_series_complete?: boolean;
  modify_future_occurrences?: boolean;
  skip_next_occurrence?: boolean;
  recurrence_action?: string;
  create_next_occurrence?: boolean;
}

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

export interface SavedFilter {
  id: string;
  name: string;
  filters: TaskFilters;
  createdAt: Date;
  updatedAt: Date;
}

export interface NotificationMessage {
  id: string;
  type: 'reminder' | 'task_update' | 'system' | 'recurring_task';
  title: string;
  message: string;
  task_id?: number;
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
}

export interface TaskUpdateMessage {
  id: number;
  action: 'created' | 'updated' | 'deleted' | 'completed';
  task: Task;
  timestamp: string;
}

export interface WebSocketServiceConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}