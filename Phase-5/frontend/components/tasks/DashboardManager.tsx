'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { TaskService, RecurrencePatternEnum } from '@/services/taskService';
import { useSearchSuggestions } from '@/hooks/useSearchSuggestions';
import { logout } from '../../utils/Authhelper';
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
import { 
  Search, 
  Filter, 
  X, 
  Bell, 
  MessageCircle, 
  Plus,
  CheckCircle2,
  Circle,
  Calendar,
  Tag,
  TrendingUp,
  Clock,
  AlertCircle,
  ChevronDown,
  BarChart3
} from 'lucide-react';

// Define enums to match backend
enum PriorityEnum {
  low = "low",
  medium = "medium",
  high = "high"
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

export default function ImprovedTaskManager({ user }: TaskManagerProps) {
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

  // UI states
  const [showNotificationPanel, setShowNotificationPanel] = useState(false);
  const [showChatInterface, setShowChatInterface] = useState(false);
  const [showAnalyticsDashboard, setShowAnalyticsDashboard] = useState(false);
  const [showCreateTaskForm, setShowCreateTaskForm] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);

  // Search suggestions hook
  const { suggestions: searchSuggestions, getSuggestions, addSearchToHistory } = useSearchSuggestions();

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

  useEffect(() => {
    applyFilters();
  }, [tasks, filters]);

  const loadTasks = async () => {
    try {
      setLoading(true);
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
      console.error('Failed to load tags:', err);
    }
  };

  const applyFilters = () => {
    let result = [...tasks];

    if (filters.search && filters.search.trim()) {
      const searchLower = filters.search.toLowerCase().trim();
      result = result.filter(task =>
        task.title.toLowerCase().includes(searchLower) ||
        (task.description?.toLowerCase() || '').includes(searchLower)
      );
    }

    if (filters.priority && filters.priority !== '') {
      result = result.filter(task => task.priority === filters.priority);
    }

    if (filters.tag_ids && filters.tag_ids.length > 0) {
      result = result.filter(task =>
        filters.tag_ids!.some(filterTagId =>
          task.tag_ids?.includes(filterTagId)
        )
      );
    }

    if (filters.completed !== undefined && filters.completed !== null) {
      result = result.filter(task => task.completed === filters.completed);
    }

    if (filters.has_due_date !== undefined && filters.has_due_date !== null) {
      result = result.filter(task =>
        filters.has_due_date ? !!task.due_date : !task.due_date
      );
    }

    if (filters.overdue) {
      const now = new Date();
      result = result.filter(task => {
        if (!task.due_date || task.completed) return false;
        return new Date(task.due_date) < now;
      });
    }

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
        return new Date(task.due_date) >= fromDate;
      });
    } else if (filters.due_date_to) {
      const toDate = new Date(filters.due_date_to);
      result = result.filter(task => {
        if (!task.due_date) return false;
        return new Date(task.due_date) <= toDate;
      });
    }

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

      await TaskService.createTask(taskData);
      await loadTasks();
      
      // Reset form and close
      setTitle('');
      setDescription('');
      setPriority(PriorityEnum.medium);
      setDueDate(null);
      setRecurrencePattern(null);
      setRecurrenceConfig(null);
      setSelectedTagIds([]);
      setShowCreateTaskForm(false);
      setError(null);
    } catch (err: any) {
      console.error('Failed to add task:', err);
      setError(err.message || 'Failed to add task');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (task: Task) => {
    if (task.recurrence_pattern && !task.completed) {
      setCurrentRecurringTask(task);
      setRecurringTaskModalOpen(true);
    } else {
      try {
        setLoading(true);
        await TaskService.toggleTaskCompletion(task.id, !task.completed);
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
      await TaskService.completeRecurringTask(currentRecurringTask.id, options);
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
      await loadTasks();
      setError(null);
    } catch (err: any) {
      console.error('Failed to delete task:', err);
      setError('Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const getTagNames = (tagIds: number[] = []) => {
    return tagIds
      .map(id => allTags.find(tag => tag.id === id)?.name)
      .filter(Boolean)
      .join(', ');
  };

  const getPriorityColor = (priority: PriorityEnum) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityIcon = (priority: PriorityEnum) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  const isTaskOverdue = (task: Task) => {
    if (!task.due_date || task.completed) return false;
    return new Date(task.due_date) < new Date();
  };

  const activeFilterCount = countActiveFilters();
  const completedTasks = tasks.filter(t => t.completed).length;
  const pendingTasks = tasks.filter(t => !t.completed).length;
  const overdueTasks = tasks.filter(t => isTaskOverdue(t)).length;
  const completionRate = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Modern Header */}
      <header className="bg-white/80 backdrop-blur-lg shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-2 rounded-lg">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Task Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  Welcome back, <span className="font-medium text-indigo-600">{user.name}</span>
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* AI Assistant Button */}
              <button
                onClick={() => setShowChatInterface(true)}
                className="relative p-2.5 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200"
                title="AI Task Assistant"
              >
                <MessageCircle className="h-5 w-5" />
              </button>

              {/* Notifications Button */}
              <button
                onClick={() => setShowNotificationPanel(true)}
                className="relative p-2.5 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200"
                title="Notifications"
              >
                <Bell className="h-5 w-5" />
                {notificationCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium animate-pulse">
                    {notificationCount}
                  </span>
                )}
              </button>

              {/* Analytics Button */}
              <button
                onClick={() => setShowAnalyticsDashboard(true)}
                className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <BarChart3 className="h-4 w-4" />
                <span className="font-medium">Analytics</span>
              </button>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="px-4 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all duration-200 font-medium shadow-md hover:shadow-lg"
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
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-6 shadow-sm animate-slideDown">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5" />
                <span className="font-medium">{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-800 hover:text-red-900"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Enhanced Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{tasks.length}</p>
              </div>
              <div className="bg-indigo-100 p-3 rounded-lg">
                <CheckCircle2 className="h-8 w-8 text-indigo-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{completedTasks}</p>
                <p className="text-xs text-gray-500 mt-1">{completionRate}% completion</p>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-3xl font-bold text-yellow-600 mt-2">{pendingTasks}</p>
              </div>
              <div className="bg-yellow-100 p-3 rounded-lg">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overdue</p>
                <p className="text-3xl font-bold text-red-600 mt-2">{overdueTasks}</p>
              </div>
              <div className="bg-red-100 p-3 rounded-lg">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filters Section */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6 border border-gray-100">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchInput}
                onChange={handleSearchInput}
                onKeyPress={handleSearchKeyPress}
                className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              {searchInput && (
                <button
                  onClick={handleClearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              )}

              {/* Search Suggestions */}
              {searchInput.length >= 2 && searchSuggestions.length > 0 && (
                <div className="absolute z-10 mt-2 w-full bg-white shadow-lg rounded-lg border border-gray-200 max-h-60 overflow-y-auto">
                  {searchSuggestions.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className="px-4 py-3 hover:bg-indigo-50 cursor-pointer text-sm transition-colors"
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
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-medium shadow-md hover:shadow-lg"
            >
              Search
            </button>
          </div>

          <div className="flex gap-3 items-center justify-between flex-wrap">
            <div className="flex gap-3 items-center">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 font-medium ${
                  showFilters 
                    ? 'bg-indigo-600 text-white shadow-md' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Filter className="h-4 w-4" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="bg-white text-indigo-600 rounded-full px-2 py-0.5 text-xs font-bold">
                    {activeFilterCount}
                  </span>
                )}
              </button>

              {activeFilterCount > 0 && (
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all font-medium"
                >
                  Clear All
                </button>
              )}
            </div>

            <div className="flex gap-3">
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

              <button
                onClick={() => setShowCreateTaskForm(!showCreateTaskForm)}
                className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-medium shadow-md hover:shadow-lg flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                New Task
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-gray-200 animate-slideDown">
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
                <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs flex items-center gap-2 font-medium">
                  Priority: {filters.priority}
                  <button onClick={() => handleFilterChange({ priority: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              
              {filters.tag_ids && filters.tag_ids.map(tagId => {
                const tag = allTags.find(t => t.id === tagId);
                return tag ? (
                  <span key={tagId} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs flex items-center gap-2 font-medium">
                    {tag.name}
                    <button onClick={() => handleFilterChange({ 
                      tag_ids: filters.tag_ids?.filter(id => id !== tagId) 
                    })}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ) : null;
              })}
              
              {filters.completed !== undefined && (
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs flex items-center gap-2 font-medium">
                  {filters.completed ? 'Completed' : 'Incomplete'}
                  <button onClick={() => handleFilterChange({ completed: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              
              {filters.overdue && (
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs flex items-center gap-2 font-medium">
                  Overdue
                  <button onClick={() => handleFilterChange({ overdue: undefined })}>
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
            </div>
          )}

          <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600 font-medium">
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                Loading tasks...
              </span>
            ) : (
              <span>{filteredTasks.length} task{filteredTasks.length !== 1 ? 's' : ''} found</span>
            )}
          </div>
        </div>

        {/* Create Task Form (Collapsible) */}
        {showCreateTaskForm && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-6 border border-gray-100 animate-slideDown">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Create New Task</h2>
              <button
                onClick={() => setShowCreateTaskForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleAddTask} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    placeholder="Enter task title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority
                  </label>
                  <PrioritySelector value={priority} onChange={setPriority} />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                  placeholder="Enter task description"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Due Date & Time
                  </label>
                  <DateTimePicker
                    value={dueDate || undefined}
                    onChange={(date) => setDueDate(date || null)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tags
                </label>
                <TagInput
                  value={selectedTagIds}
                  onChange={setSelectedTagIds}
                  availableTags={allTags}
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-medium shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Adding...
                    </>
                  ) : (
                    <>
                      <Plus className="h-5 w-5" />
                      Add Task
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateTaskForm(false)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Tasks List */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-600" />
            Your Tasks ({filteredTasks.length})
          </h2>

          {loading ? (
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto"></div>
              <p className="mt-6 text-gray-600 font-medium">Loading tasks...</p>
            </div>
          ) : filteredTasks.length === 0 ? (
            <div className="text-center py-16">
              <div className="bg-gray-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                <CheckCircle2 className="h-12 w-12 text-gray-400" />
              </div>
              <p className="text-gray-500 text-lg font-medium">
                {activeFilterCount > 0 
                  ? 'No tasks match your filters'
                  : 'No tasks yet. Create your first task!'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className={`group border-2 rounded-lg p-5 transition-all duration-200 hover:shadow-md ${
                    task.completed 
                      ? 'bg-gray-50 border-gray-200' 
                      : isTaskOverdue(task)
                      ? 'bg-red-50 border-red-200'
                      : 'bg-white border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <button
                      onClick={() => handleToggleTask(task)}
                      className="mt-1 flex-shrink-0"
                    >
                      {task.completed ? (
                        <CheckCircle2 className="h-6 w-6 text-green-600" />
                      ) : (
                        <Circle className="h-6 w-6 text-gray-400 group-hover:text-indigo-600 transition-colors" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className={`text-base font-semibold ${
                            task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                          }`}>
                            {task.title}
                          </h3>

                          {task.description && (
                            <p className="mt-1 text-sm text-gray-600">
                              {task.description}
                            </p>
                          )}

                          <div className="mt-3 flex flex-wrap gap-2">
                            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${getPriorityColor(task.priority)}`}>
                              <span>{getPriorityIcon(task.priority)}</span>
                              {task.priority}
                            </span>

                            {task.due_date && (
                              <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                                isTaskOverdue(task)
                                  ? 'bg-red-100 text-red-700 border border-red-200'
                                  : 'bg-blue-100 text-blue-700 border border-blue-200'
                              }`}>
                                <Calendar className="h-3 w-3" />
                                {new Date(task.due_date).toLocaleDateString()}
                              </span>
                            )}

                            {task.recurrence_pattern && (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 border border-purple-200">
                                🔄 {task.recurrence_pattern}
                              </span>
                            )}

                            {task.tag_ids && task.tag_ids.length > 0 && (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">
                                <Tag className="h-3 w-3" />
                                {getTagNames(task.tag_ids)}
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleToggleTask(task)}
                            className="px-3 py-1.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          >
                            {task.completed ? 'Undo' : 'Complete'}
                          </button>
                          <button
                            onClick={() => handleDeleteTask(task.id)}
                            className="px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modals and Panels */}
      {recurringTaskModalOpen && currentRecurringTask && (
        <RecurringTaskCompletionModal
          task={currentRecurringTask}
          isOpen={recurringTaskModalOpen}
          onClose={() => setRecurringTaskModalOpen(false)}
          onComplete={handleCompleteRecurringTask}
          isLoading={recurringTaskCompletionLoading}
        />
      )}

      {showNotificationPanel && (
        <NotificationPanel
          userId={user.user_id}
          onClose={() => setShowNotificationPanel(false)}
          onNotificationClick={(notification) => {
            if (notification.task_id) {
              console.log('Notification clicked for task:', notification.task_id);
            }
          }}
        />
      )}

      {showChatInterface && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] animate-slideUp">
            <ChatInterface
              userId={user.user_id}
              onClose={() => setShowChatInterface(false)}
              onTaskOperation={(operation) => {
                console.log('AI assistant task operation:', operation);
                loadTasks();
              }}
            />
          </div>
        </div>
      )}

      {showAnalyticsDashboard && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden animate-slideUp">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center z-10">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-indigo-600" />
                Task Analytics
              </h2>
              <button
                onClick={() => setShowAnalyticsDashboard(false)}
                className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition-all"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-5rem)]">
              <AnalyticsDashboard />
            </div>
          </div>
        </div>
      )}

      {/* Add custom animations in your global CSS */}
      <style jsx global>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
        
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out;
        }
      `}</style>
    </div>
  );
}