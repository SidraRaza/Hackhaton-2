'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { TaskService, RecurrencePatternEnum, AnalyticsService } from '@/services/taskService';
import { useSearchSuggestions } from '@/hooks/useSearchSuggestions';
import { logout } from '../../utils/Authhelper'; // Import auth helper
import { PrioritySelector } from './PrioritySelector';
import { TagInput } from './TagInput';
import { DateTimePicker } from './DateTimePicker';
import { RecurrencePatternSelector } from './RecurrencePatternSelector';
import { SortControls, SortField, SortOrder } from './SortControls';
import { AdvancedFilterPanel } from './AdvancedFilterPanel';
import { SavedFilterControls } from './SavedFilterControls';
import { RecurringTaskCompletionModal } from './RecurringTaskCompletionModal';
import { NotificationPanel } from './NotificationPanel';
import { ChatInterface } from './ChatInterface';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import { Search, Filter, X, Bell, MessageCircle } from 'lucide-react';

// Define enums to match backend
enum PriorityEnum {
  low = "low",
  medium = "medium",
  high = "high"
}

enum RecurrencePatternEnum {
  daily = "daily",
  weekly = "weekly",
  monthly = "monthly",
  yearly = "yearly",
  custom = "custom"
}

interface Task {
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

interface UserProfile {
  user_id: string;
  email: string;
  name: string;
}

interface TaskManagerProps {
  user: UserProfile;
}

interface FilterParams {
  search?: string;
  priority?: PriorityEnum;
  tag_ids?: number[];
  completed?: boolean;
  has_due_date?: boolean;
  overdue?: boolean;
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: SortField | string;
  sort_order?: SortOrder;
  secondary_sort?: SortField | string;
  secondary_order?: SortOrder;
  use_saved_filters?: boolean;
  save_filters?: boolean;
}

export default function TaskManager({ user }: TaskManagerProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<PriorityEnum>(PriorityEnum.medium);
  const [dueDate, setDueDate] = useState<string | null>(null);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePatternEnum | null>(null);
  const [recurrenceConfig, setRecurrenceConfig] = useState<any>(null);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [allTags, setAllTags] = useState<{id: number, name: string, color: string}[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recurringTaskModalOpen, setRecurringTaskModalOpen] = useState(false);
  const [currentRecurringTask, setCurrentRecurringTask] = useState<Task | null>(null);
  const [recurringTaskCompletionLoading, setRecurringTaskCompletionLoading] = useState(false);

  // Notification states
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);

  // Chat interface states
  const [showChatInterface, setShowChatInterface] = useState(false);

  // Analytics dashboard states
  const [showAnalyticsDashboard, setShowAnalyticsDashboard] = useState(false);

  // Search suggestions hook
  const { suggestions: searchSuggestions, getSuggestions, loading: suggestionsLoading, addSearchToHistory } = useSearchSuggestions();

  // Search, Filter, Sort states
  const [searchInput, setSearchInput] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterParams>({
    sort_by: 'created_at',
    sort_order: 'desc',
    use_saved_filters: false,
    save_filters: false
  });
  
  const router = useRouter();

  useEffect(() => {
    loadTasks();
    loadTags();
  }, []);

  // Apply filters whenever tasks or filters change
  useEffect(() => {
    applyFilters();
  }, [tasks, filters]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      // Prepare filter parameters for API call
      const apiFilters = {
        priority: filters.priority ? [filters.priority] : undefined,
        tags: filters.tag_ids,
        search: filters.search,
        due_date_from: filters.due_date_from,
        due_date_to: filters.due_date_to,
        status: filters.completed !== undefined ? (filters.completed ? 'completed' : 'pending') : 'all',
        sort: filters.sort_by as any,
        sort_order: filters.sort_order,
        secondary_sort: filters.secondary_sort as any,
        secondary_sort_order: filters.secondary_order,
        use_saved_filters: filters.use_saved_filters,
        save_filters: filters.save_filters,
      };
      const response = await TaskService.getAllTasks(apiFilters);
      setTasks(response || []);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load tasks:', err);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const loadTags = async () => {
    try {
      const response = await TaskService.getTags();
      setAllTags(response || []);
    } catch (err: any) {
      console.error('❌ Failed to load tags:', err);
    }
  };

  // Apply filters and sorting
  const applyFilters = () => {
    let result = [...tasks];

    // Search filter - only if search has actual text
    if (filters.search && filters.search.trim()) {
      const searchLower = filters.search.toLowerCase().trim();
      result = result.filter(task =>
        task.title.toLowerCase().includes(searchLower) ||
        (task.description?.toLowerCase() || '').includes(searchLower)
      );
    }

    // Priority filter - only if priority is actually selected (not empty string)
    if (filters.priority && filters.priority !== '') {
      result = result.filter(task => task.priority === filters.priority);
    }

    // Tags filter - only if tags array has items
    if (filters.tag_ids && filters.tag_ids.length > 0) {
      result = result.filter(task =>
        filters.tag_ids!.some(filterTagId =>
          task.tag_ids?.includes(filterTagId)
        )
      );
    }

    // Completed filter - only if explicitly set
    if (filters.completed !== undefined && filters.completed !== null) {
      result = result.filter(task => task.completed === filters.completed);
    }

    // Has due date filter
    if (filters.has_due_date !== undefined && filters.has_due_date !== null) {
      result = result.filter(task =>
        filters.has_due_date ? !!task.due_date : !task.due_date
      );
    }

    // Overdue filter
    if (filters.overdue) {
      const now = new Date();
      result = result.filter(task => {
        if (!task.due_date || task.completed) return false;
        return new Date(task.due_date) < now;
      });
    }

    // Date range filter - only if both dates are set
    if (filters.due_date_from && filters.due_date_to) {
      const fromDate = new Date(filters.due_date_from);
      const toDate = new Date(filters.due_date_to);
      result = result.filter(task => {
        if (!task.due_date) return false;
        const taskDate = new Date(task.due_date);
        return taskDate >= fromDate && taskDate <= toDate;
      });
    } else if (filters.due_date_from) {
      const fromDate = new Date(filters.due_date_from);
      result = result.filter(task => {
        if (!task.due_date) return false;
        const taskDate = new Date(task.due_date);
        return taskDate >= fromDate;
      });
    } else if (filters.due_date_to) {
      const toDate = new Date(filters.due_date_to);
      result = result.filter(task => {
        if (!task.due_date) return false;
        const taskDate = new Date(task.due_date);
        return taskDate <= toDate;
      });
    }

    // Sorting
    if (filters.sort_by) {
      result.sort((a, b) => {
        const aValue = getSortValue(a, filters.sort_by!);
        const bValue = getSortValue(b, filters.sort_by!);

        const comparison = compareValues(aValue, bValue);
        return filters.sort_order === 'desc' ? -comparison : comparison;
      });
    }

    setFilteredTasks(result);
  };

  const getSortValue = (task: Task, field: string): any => {
    switch (field) {
      case 'title':
        return task.title.toLowerCase();
      case 'priority':
        const priorityMap = { low: 1, medium: 2, high: 3 };
        return priorityMap[task.priority];
      case 'due_date':
        return task.due_date ? new Date(task.due_date).getTime() : 0;
      case 'created_at':
        return new Date(task.created_at).getTime();
      case 'updated_at':
        return new Date(task.updated_at).getTime();
      default:
        return task[field as keyof Task];
    }
  };

  const compareValues = (a: any, b: any): number => {
    if (a === null || a === undefined) return 1;
    if (b === null || b === undefined) return -1;
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
  };

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, search: searchInput }));
    // Add search term to history
    if (searchInput.trim()) {
      addSearchToHistory(searchInput.trim());
    }
  };

  const handleSearchKeyPress = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleSearchInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchInput(value);

    // Get search suggestions when user types
    if (value.length >= 2) {
      await getSuggestions(value);
    }
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setFilters(prev => ({ ...prev, search: '' }));
  };

  const handleFilterChange = useCallback((newFilters: Partial<FilterParams>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const saveCurrentFilters = (name: string) => {
    // Save current filters to localStorage
    const currentFilterSettings = {
      ...filters,
      name: name,
      saved_at: new Date().toISOString()
    };

    // Get existing saved filters
    const savedFiltersStr = localStorage.getItem('taskFilters');
    const savedFilters = savedFiltersStr ? JSON.parse(savedFiltersStr) : {};

    // Add new filter
    savedFilters[name] = currentFilterSettings;

    // Save back to localStorage
    localStorage.setItem('taskFilters', JSON.stringify(savedFilters));
  };

  const loadSavedFilters = (name: string) => {
    // Load filters from localStorage
    const savedFiltersStr = localStorage.getItem('taskFilters');
    if (savedFiltersStr) {
      const savedFilters = JSON.parse(savedFiltersStr);
      const savedFilter = savedFilters[name];
      if (savedFilter) {
        // Remove the name and saved_at fields when loading
        const { name: _, saved_at: __, ...filterSettings } = savedFilter;
        setFilters(prev => ({ ...prev, ...filterSettings }));
        loadTasks(); // Reload tasks with new filters
      }
    }
  };

  const deleteSavedFilters = (name: string) => {
    // Delete saved filter from localStorage
    const savedFiltersStr = localStorage.getItem('taskFilters');
    if (savedFiltersStr) {
      const savedFilters = JSON.parse(savedFiltersStr);
      delete savedFilters[name];
      localStorage.setItem('taskFilters', JSON.stringify(savedFilters));
    }
  };

  const getSavedFilterNames = (): string[] => {
    // Get all saved filter names
    const savedFiltersStr = localStorage.getItem('taskFilters');
    if (savedFiltersStr) {
      const savedFilters = JSON.parse(savedFiltersStr);
      return Object.keys(savedFilters);
    }
    return [];
  };

  const handleSortChange = useCallback((sortConfig: {
    primary: { field: SortField; order: SortOrder };
    secondary: { field: SortField; order: SortOrder };
  }) => {
    setFilters(prev => ({
      ...prev,
      sort_by: sortConfig.primary.field,
      sort_order: sortConfig.primary.order,
      secondary_sort: sortConfig.secondary.field,
      secondary_order: sortConfig.secondary.order,
    }));
  }, []);

  const clearFilters = () => {
    setFilters({
      search: '',
      priority: undefined,
      tag_ids: undefined,
      completed: undefined,
      has_due_date: undefined,
      overdue: undefined,
      sort_by: 'created_at',
      sort_order: 'desc'
    });
    setSearchInput('');
  };

  const countActiveFilters = (): number => {
    let count = 0;
    if (filters.search && filters.search.trim()) count++;
    if (filters.priority) count++;
    if (filters.tag_ids && filters.tag_ids.length > 0) count++;
    if (filters.completed !== undefined) count++;
    if (filters.has_due_date) count++;
    if (filters.overdue) count++;
    if (filters.due_date_from) count++;
    if (filters.due_date_to) count++;
    return count;
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (recurrencePattern && !dueDate) {
      setError('Due date is required for recurring tasks');
      return;
    }

    if (recurrencePattern === RecurrencePatternEnum.custom && !recurrenceConfig) {
      setError('Recurrence configuration is required for custom patterns');
      return;
    }

    try {
      setLoading(true);
      const taskData = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined,
        recurrence_pattern: recurrencePattern || undefined,
        recurrence_config: recurrenceConfig,
        tag_ids: selectedTagIds.length > 0 ? selectedTagIds : undefined,
      };

      const newTask = await TaskService.createTask(taskData);
      
      // **FIX 1: Reload tasks from server to get fresh data**
      await loadTasks();
      
      // Reset form
      setTitle('');
      setDescription('');
      setPriority(PriorityEnum.medium);
      setDueDate(null);
      setRecurrencePattern(null);
      setRecurrenceConfig(null);
      setSelectedTagIds([]);
      setError(null);
    } catch (err: any) {
      console.error('Failed to add task:', err);
      setError(err.message || 'Failed to add task');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (task: Task) => {
    // Check if the task is recurring and not completed yet
    if (task.recurrence_pattern && !task.completed) {
      // Show the recurring task completion modal
      setCurrentRecurringTask(task);
      setRecurringTaskModalOpen(true);
    } else {
      // For non-recurring tasks or completing a completed recurring task, use normal toggle
      try {
        setLoading(true);
        await TaskService.toggleTaskCompletion(task.id, !task.completed);
        // **FIX: Reload tasks from server instead of manual update**
        await loadTasks();
        setError(null);
      } catch (err: any) {
        console.error('Failed to update task:', err);
        setError('Failed to update task');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleCompleteRecurringTask = async (options: {
    mark_series_complete?: boolean;
    skip_next_occurrence?: boolean;
    recurrence_action?: string;
    create_next_occurrence?: boolean;
  }) => {
    if (!currentRecurringTask) return;

    setRecurringTaskCompletionLoading(true);

    try {
      const updatedTask = await TaskService.completeRecurringTask(currentRecurringTask.id, options);
      // **FIX 2: Reload all tasks to get updated list**
      await loadTasks();
      setError(null);
    } catch (err: any) {
      console.error('Failed to complete recurring task:', err);
      setError(err.message || 'Failed to complete recurring task');
    } finally {
      setRecurringTaskCompletionLoading(false);
      setRecurringTaskModalOpen(false);
      setCurrentRecurringTask(null);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      setLoading(true);
      await TaskService.deleteTask(taskId);
      // **FIX: Reload tasks from server instead of manual filter**
      await loadTasks();
      setError(null);
    } catch (err: any) {
      console.error('Failed to delete task:', err);
      setError('Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  // **FIX 4: Use AuthHelper for consistent logout**
  const handleLogout = () => {
    logout(); // This will clear both localStorage and cookie, then redirect
  };

  const getTagNames = (tagIds: number[] = []) => {
    return tagIds
      .map(id => allTags.find(tag => tag.id === id)?.name)
      .filter(Boolean)
      .join(', ');
  };

  const getPriorityColor = (priority: PriorityEnum) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const activeFilterCount = countActiveFilters();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Task Manager</h1>
              <p className="text-sm text-gray-600 mt-1">
                Welcome, {user.name}! ({user.email})
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-4">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-800 hover:text-red-900 font-medium"
            >
              ✕
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Total Tasks</h3>
                <p className="text-2xl font-semibold text-gray-900">{tasks.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Completed</h3>
                <p className="text-2xl font-semibold text-gray-900">
                  {tasks.filter(t => t.completed).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Pending</h3>
                <p className="text-2xl font-semibold text-gray-900">
                  {tasks.filter(t => !t.completed).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search, Filter, Sort Controls */}
        <div className="bg-white shadow rounded-lg p-4 mb-6">
          {/* Search Bar */}
          <div className="mb-4 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search tasks by title or description..."
                value={searchInput}
                onChange={handleSearchInput}
                onKeyPress={handleSearchKeyPress}
                className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              {searchInput && (
                <button
                  onClick={handleClearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}

              {/* Search Suggestions Dropdown */}
              {searchInput.length >= 2 && searchSuggestions.length > 0 && (
                <div className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-y-auto">
                  {searchSuggestions.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                      onClick={() => {
                        setSearchInput(suggestion.text);
                        setFilters(prev => ({ ...prev, search: suggestion.text }));
                      }}
                    >
                      {suggestion.text}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
            >
              Search
            </button>
          </div>

          {/* Filter and Sort Row */}
          <div className="flex gap-2 items-center justify-between flex-wrap">
            <div className="flex gap-2 items-center">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 rounded-md transition flex items-center gap-2 ${
                  showFilters ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Filter className="h-4 w-4" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="bg-white text-indigo-600 rounded-full px-2 py-0.5 text-xs font-medium">
                    {activeFilterCount}
                  </span>
                )}
              </button>

              {activeFilterCount > 0 && (
                <button
                  onClick={clearFilters}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition"
                >
                  Clear All
                </button>
              )}
            </div>

            <SortControls
              value={{
                primary: { 
                  field: (filters.sort_by || 'created_at') as any, 
                  order: (filters.sort_order || 'desc') as 'asc' | 'desc'
                },
                secondary: { 
                  field: (filters.secondary_sort || 'title') as any, 
                  order: (filters.secondary_order || 'asc') as 'asc' | 'desc'
                }
              }}
              onChange={handleSortChange}
            />
          </div>

          {/* Advanced Filter Panel */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <AdvancedFilterPanel
                filters={filters}
                onChange={handleFilterChange}
                onClose={() => setShowFilters(false)}
                availableTags={allTags}
                savedFilterControls={
                  <SavedFilterControls
                    currentFilters={filters}
                    onLoadFilter={(loadedFilters) => setFilters(prev => ({ ...prev, ...loadedFilters }))}
                    onApplyFilters={loadTasks}
                  />
                }
              />
            </div>
          )}

          {/* Active Filters Display */}
          {activeFilterCount > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2 flex-wrap items-center">
              <span className="text-sm font-medium text-gray-700">Active filters:</span>
              
              {filters.priority && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  Priority: {filters.priority}
                  <button onClick={() => handleFilterChange({ priority: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              
              {filters.tag_ids && filters.tag_ids.map(tagId => {
                const tag = allTags.find(t => t.id === tagId);
                return tag ? (
                  <span key={tagId} className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                    Tag: {tag.name}
                    <button onClick={() => handleFilterChange({ 
                      tag_ids: filters.tag_ids?.filter(id => id !== tagId) 
                    })}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ) : null;
              })}
              
              {filters.completed !== undefined && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  {filters.completed ? 'Completed' : 'Incomplete'}
                  <button onClick={() => handleFilterChange({ completed: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              
              {filters.has_due_date && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  Has due date
                  <button onClick={() => handleFilterChange({ has_due_date: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              
              {filters.overdue && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  Overdue
                  <button onClick={() => handleFilterChange({ overdue: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {filters.due_date_from && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  From: {new Date(filters.due_date_from).toLocaleDateString()}
                  <button onClick={() => handleFilterChange({ due_date_from: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}

              {filters.due_date_to && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs flex items-center gap-1">
                  To: {new Date(filters.due_date_to).toLocaleDateString()}
                  <button onClick={() => handleFilterChange({ due_date_to: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
            </div>
          )}

          {/* Task Count */}
          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
            {loading ? 'Loading...' : `${filteredTasks.length} task${filteredTasks.length !== 1 ? 's' : ''} found`}
          </div>
        </div>

        {/* Task Form */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Create New Task</h2>
          <form onSubmit={handleAddTask} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Title *
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  className="mt-1 block w-full p-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter task title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Priority
                </label>
                <PrioritySelector
                  value={priority}
                  onChange={setPriority}
                />
              </div>
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description (optional)
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="mt-1 block w-full p-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Enter task description"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Due Date & Time
                </label>
                <DateTimePicker
                  value={dueDate || undefined}
                  onChange={(date) => setDueDate(date || null)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Recurrence Pattern
                </label>
                <RecurrencePatternSelector
                  value={recurrencePattern}
                  onChange={(pattern) => setRecurrencePattern(pattern)}
                  onConfigChange={setRecurrenceConfig}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Tags
              </label>
              <TagInput
                value={selectedTagIds}
                onChange={setSelectedTagIds}
                availableTags={allTags}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {loading ? 'Adding...' : 'Add Task'}
            </button>
          </form>
        </div>

        {/* Task List */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Your Tasks ({filteredTasks.length})
          </h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading tasks...</p>
            </div>
          ) : filteredTasks.length === 0 ? (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="mt-2 text-gray-500">
                {activeFilterCount > 0 
                  ? 'No tasks match your filters. Try adjusting your search or filters.'
                  : 'No tasks yet. Create your first task above!'}
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredTasks.map((task) => (
                <li key={task.id} className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start flex-1">
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => handleToggleTask(task)}
                        className="h-4 w-4 mt-1 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                      />
                      <div className="ml-3 flex-1">
                        <div className="flex items-center">
                          <span
                            className={`text-sm font-medium ${
                              task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                            }`}
                          >
                            {task.title}
                          </span>
                          <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </div>

                        {task.description && (
                          <p className="mt-1 text-sm text-gray-500">
                            {task.description}
                          </p>
                        )}

                        <div className="mt-2 flex flex-wrap gap-2">
                          {task.due_date && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              📅 {new Date(task.due_date).toLocaleString()}
                            </span>
                          )}

                          {task.recurrence_pattern && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                              🔄 {task.recurrence_pattern}
                            </span>
                          )}

                          {task.tag_ids && task.tag_ids.length > 0 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              🏷️ {getTagNames(task.tag_ids)}
                            </span>
                          )}
                        </div>

                        <p className="mt-1 text-xs text-gray-400">
                          Created: {new Date(task.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleToggleTask(task)}
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
                      >
                        {task.completed ? 'Undo' : 'Complete'}
                      </button>
                      <button
                        onClick={() => handleDeleteTask(task.id)}
                        className="text-sm font-medium text-red-600 hover:text-red-500"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>

      {/* Recurring Task Completion Modal */}
      {recurringTaskModalOpen && currentRecurringTask && (
        <RecurringTaskCompletionModal
          task={currentRecurringTask}
          isOpen={recurringTaskModalOpen}
          onClose={() => setRecurringTaskModalOpen(false)}
          onComplete={handleCompleteRecurringTask}
          isLoading={recurringTaskCompletionLoading}
        />
      )}

      {/* Notification Panel */}
      {showNotificationPanel && (
        <NotificationPanel
          userId={user.user_id}
          onClose={() => setShowNotificationPanel(false)}
          onNotificationClick={(notification) => {
            // Handle notification click - maybe navigate to the relevant task
            if (notification.task_id) {
              // Scroll to the task or show details
              console.log('Notification clicked for task:', notification.task_id);
            }
          }}
        />
      )}

      {/* Chat Interface */}
      {showChatInterface && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh]">
            <ChatInterface
              userId={user.user_id}
              onClose={() => setShowChatInterface(false)}
              onTaskOperation={(operation) => {
                // Handle task operations from the AI assistant
                console.log('AI assistant task operation:', operation);
                // Refresh tasks after AI operations
                loadTasks();
              }}
            />
          </div>
        </div>
      )}

      {/* Analytics Dashboard */}
      {showAnalyticsDashboard && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center z-10">
              <h2 className="text-xl font-bold text-gray-900">Task Analytics</h2>
              <button
                onClick={() => setShowAnalyticsDashboard(false)}
                className="text-gray-400 hover:text-gray-500"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="p-4">
              <AnalyticsDashboard />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}