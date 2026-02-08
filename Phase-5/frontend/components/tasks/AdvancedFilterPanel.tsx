import React, { useState, useEffect } from 'react';
import { X, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface AdvancedFilterPanelProps {
  filters: {
    priority?: 'low' | 'medium' | 'high';
    tag_ids?: number[];
    completed?: boolean;
    has_due_date?: boolean;
    overdue?: boolean;
    due_date_from?: string;
    due_date_to?: string;
  };
  onChange: (filters: Partial<AdvancedFilterPanelProps['filters']>) => void;
  onClose?: () => void;
  availableTags?: Tag[];
  className?: string;
  savedFilterControls?: React.ReactNode; // For saved filters functionality
}

export function AdvancedFilterPanel({
  filters = {},
  onChange,
  onClose,
  availableTags = [],
  className,
  savedFilterControls
}: AdvancedFilterPanelProps) {
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
      priority: undefined,
      tag_ids: [],
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
    <div className={cn("space-y-4", className)}>
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Filter size={16} />
          Filters
        </h3>
        <div className="flex gap-2">
          {savedFilterControls}
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Priority
        </label>
        <select
          value={localFilters.priority || ''}
          onChange={(e) => handleFilterChange('priority', e.target.value || undefined)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      {/* Completion Status Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Status
        </label>
        <select
          value={
            localFilters.completed === undefined ? '' : 
            localFilters.completed ? 'completed' : 'incomplete'
          }
          onChange={(e) => {
            const value = e.target.value;
            handleFilterChange(
              'completed', 
              value === '' ? undefined : value === 'completed'
            );
          }}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Tasks</option>
          <option value="incomplete">Incomplete Only</option>
          <option value="completed">Completed Only</option>
        </select>
      </div>

      {/* Tags Filter */}
      {availableTags.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {availableTags.map(tag => (
              <label key={tag.id} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localFilters.tag_ids?.includes(tag.id) || false}
                  onChange={(e) => {
                    const currentTags = localFilters.tag_ids || [];
                    const newTags = e.target.checked
                      ? [...currentTags, tag.id]
                      : currentTags.filter(id => id !== tag.id);
                    handleFilterChange('tag_ids', newTags);
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span 
                  className="text-sm px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: `${tag.color}20`, color: tag.color }}
                >
                  {tag.name}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Due Date Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Due Date
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.has_due_date || false}
              onChange={(e) => handleFilterChange('has_due_date', e.target.checked || undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Has Due Date</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.overdue || false}
              onChange={(e) => handleFilterChange('overdue', e.target.checked || undefined)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-red-600">Overdue Only</span>
          </label>

          {/* Date Range Filter */}
          <div className="pt-2 space-y-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">From Date</label>
              <input
                type="date"
                value={localFilters.due_date_from || ''}
                onChange={(e) => handleFilterChange('due_date_from', e.target.value || undefined)}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">To Date</label>
              <input
                type="date"
                value={localFilters.due_date_to || ''}
                onChange={(e) => handleFilterChange('due_date_to', e.target.value || undefined)}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Close Button */}
      {onClose && (
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm font-medium transition"
          >
            Close Filters
          </button>
        </div>
      )}
    </div>
  );
}

export default AdvancedFilterPanel;