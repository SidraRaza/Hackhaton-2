import { useState, useEffect } from 'react';
import { X, Search, Calendar, Filter, Save, FolderOpen, Trash2 } from 'lucide-react';
import { PrioritySelector } from './PrioritySelector';
import { TagInput } from './TagInput';
import { DateTimePicker } from './DateTimePicker';
import { SavedFilterControls } from './SavedFilterControls';
import { PriorityEnum } from '@/services/taskService';

interface Tag {
  id: number;
  name: string;
  color: string;
}

interface SearchFilterPanelProps {
  filters: {
    search?: string;
    priority?: PriorityEnum;
    tag_ids?: number[];
    completed?: boolean;
    has_due_date?: boolean;
    overdue?: boolean;
    due_date_from?: string;
    due_date_to?: string;
  };
  onChange: (filters: Partial<SearchFilterPanelProps['filters']>) => void;
  onClose?: () => void;
  availableTags?: Tag[];
  savedFilterControls?: React.ReactNode;
}

export const SearchFilterPanel = ({
  filters = {},
  onChange,
  onClose,
  availableTags = [],
  savedFilterControls
}: SearchFilterPanelProps) => {
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (field: string, value: any) => {
    const newFilters = { ...localFilters, [field]: value };
    setLocalFilters(newFilters);
    onChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      search: undefined,
      priority: undefined,
      tag_ids: undefined,
      completed: undefined,
      has_due_date: undefined,
      overdue: undefined,
      due_date_from: undefined,
      due_date_to: undefined,
    };
    setLocalFilters(emptyFilters);
    onChange(emptyFilters);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Filter size={16} />
          Advanced Filters
        </h3>
        <div className="flex gap-2">
          {savedFilterControls}
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear All
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Search Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Search Tasks
        </label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search by title, description..."
            value={localFilters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Priority
        </label>
        <PrioritySelector
          value={localFilters.priority || ''}
          onChange={(value) => handleFilterChange('priority', value)}
        />
      </div>

      {/* Tags Filter */}
      {availableTags.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <TagInput
            value={localFilters.tag_ids || []}
            onChange={(value) => handleFilterChange('tag_ids', value)}
            availableTags={availableTags}
          />
        </div>
      )}

      {/* Completion Status Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Status
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.completed === true}
              onChange={(e) => handleFilterChange('completed', e.target.checked ? true : undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Completed Only</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.completed === false}
              onChange={(e) => handleFilterChange('completed', e.target.checked ? false : undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Incomplete Only</span>
          </label>
        </div>
      </div>

      {/* Due Date Filters */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Due Date
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={!!localFilters.has_due_date}
              onChange={(e) => handleFilterChange('has_due_date', e.target.checked || undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Has Due Date</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={!!localFilters.overdue}
              onChange={(e) => handleFilterChange('overdue', e.target.checked || undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-red-600">Overdue Only</span>
          </label>

          {/* Date Range Filter */}
          <div className="pt-2 space-y-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">From Date</label>
              <DateTimePicker
                value={localFilters.due_date_from || undefined}
                onChange={(date) => handleFilterChange('due_date_from', date || undefined)}
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">To Date</label>
              <DateTimePicker
                value={localFilters.due_date_to || undefined}
                onChange={(date) => handleFilterChange('due_date_to', date || undefined)}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};