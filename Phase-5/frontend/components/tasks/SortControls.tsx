import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ChevronsUpDown, ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/tasks/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/tasks/ui/select';
import { Label } from '@/components/tasks/ui/label';

export type SortField = 'priority' | 'due_date' | 'created_at' | 'title' | 'completed';
export type SortOrder = 'asc' | 'desc';

export interface SortOption {
  value: SortField;
  label: string;
  icon: React.ReactNode;
}

export interface SortControlsProps {
  value: {
    primary: { field: SortField; order: SortOrder };
    secondary: { field: SortField; order: SortOrder };
  };
  onChange: (sort: {
    primary: { field: SortField; order: SortOrder };
    secondary: { field: SortField; order: SortOrder };
  }) => void;
  disabled?: boolean;
  className?: string;
}

export function SortControls({
  value,
  onChange,
  disabled = false,
  className
}: SortControlsProps) {
  const [primaryField, setPrimaryField] = useState<SortField>(value.primary.field);
  const [primaryOrder, setPrimaryOrder] = useState<SortOrder>(value.primary.order);
  const [secondaryField, setSecondaryField] = useState<SortField>(value.secondary.field);
  const [secondaryOrder, setSecondaryOrder] = useState<SortOrder>(value.secondary.order);

  // Update local state when value prop changes
  useEffect(() => {
    setPrimaryField(value.primary.field);
    setPrimaryOrder(value.primary.order);
    setSecondaryField(value.secondary.field);
    setSecondaryOrder(value.secondary.order);
  }, [value.primary.field, value.primary.order, value.secondary.field, value.secondary.order]);

  // Memoize the current sort config to prevent unnecessary onChange calls
  const currentConfig = useMemo(() => ({
    primary: { field: primaryField, order: primaryOrder },
    secondary: { field: secondaryField, order: secondaryOrder }
  }), [primaryField, primaryOrder, secondaryField, secondaryOrder]);

  // Only call onChange when config actually changes
  useEffect(() => {
    // Check if config has actually changed
    const hasChanged = 
      currentConfig.primary.field !== value.primary.field ||
      currentConfig.primary.order !== value.primary.order ||
      currentConfig.secondary.field !== value.secondary.field ||
      currentConfig.secondary.order !== value.secondary.order;

    if (hasChanged) {
      onChange(currentConfig);
    }
  }, [currentConfig, onChange, value]);

  const sortFields: SortOption[] = useMemo(() => [
    { value: 'priority', label: 'Priority', icon: <ChevronsUpDown size={16} /> },
    { value: 'due_date', label: 'Due Date', icon: <ArrowUpDown size={16} /> },
    { value: 'created_at', label: 'Created Date', icon: <ArrowUp size={16} /> },
    { value: 'title', label: 'Title', icon: <ArrowUpDown size={16} /> },
    { value: 'completed', label: 'Completion', icon: <ArrowDown size={16} /> }
  ], []);

  const getSortIcon = useCallback((field: SortField, order: SortOrder) => {
    if (order === 'desc') return <ArrowDown size={16} />;
    if (order === 'asc') return <ArrowUp size={16} />;
    return <ChevronsUpDown size={16} />;
  }, []);

  const getSortFieldLabel = useCallback((field: SortField) => {
    return sortFields.find(f => f.value === field)?.label || field;
  }, [sortFields]);

  return (
    <div className={cn("flex flex-col gap-4 p-4 border rounded-lg bg-white", className)}>
      <h3 className="font-medium text-lg">Sort Tasks</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Primary Sort */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="primary-sort-field" className="text-sm font-medium">
              Primary Sort
            </Label>
            <div className="flex gap-2 mt-2">
              <Select
                value={primaryField}
                onValueChange={(val: SortField) => setPrimaryField(val)}
                disabled={disabled}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select field" />
                </SelectTrigger>
                <SelectContent>
                  {sortFields.map(field => (
                    <SelectItem key={field.value} value={field.value}>
                      {field.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setPrimaryOrder(primaryOrder === 'asc' ? 'desc' : 'asc')}
                disabled={disabled}
                className="flex items-center gap-2"
              >
                {primaryOrder === 'asc' ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                <span className="capitalize">{primaryOrder}</span>
              </Button>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            <span className="font-medium">Current:</span> {getSortFieldLabel(primaryField)} ({primaryOrder})
          </div>
        </div>

        {/* Secondary Sort */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="secondary-sort-field" className="text-sm font-medium">
              Secondary Sort
            </Label>
            <div className="flex gap-2 mt-2">
              <Select
                value={secondaryField}
                onValueChange={(val: SortField) => setSecondaryField(val)}
                disabled={disabled}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select field" />
                </SelectTrigger>
                <SelectContent>
                  {sortFields.map(field => (
                    <SelectItem
                      key={field.value}
                      value={field.value}
                      disabled={field.value === primaryField}
                    >
                      {field.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setSecondaryOrder(secondaryOrder === 'asc' ? 'desc' : 'asc')}
                disabled={disabled}
                className="flex items-center gap-2"
              >
                {secondaryOrder === 'asc' ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                <span className="capitalize">{secondaryOrder}</span>
              </Button>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            <span className="font-medium">Current:</span> {getSortFieldLabel(secondaryField)} ({secondaryOrder})
          </div>
        </div>
      </div>

      {/* Combined sort indicator */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg border">
        <div className="flex items-center gap-2">
          {getSortIcon(primaryField, primaryOrder)}
          <span className="font-medium">
            {getSortFieldLabel(primaryField)} <span className="lowercase">({primaryOrder})</span>
          </span>
          <span className="mx-2 text-gray-400">then by</span>
          {getSortIcon(secondaryField, secondaryOrder)}
          <span className="font-medium">
            {getSortFieldLabel(secondaryField)} <span className="lowercase">({secondaryOrder})</span>
          </span>
        </div>
      </div>
    </div>
  );
}

// Sort Indicator Component - shows current sort state
export interface SortIndicatorProps {
  field: SortField;
  order: SortOrder;
  isActive: boolean;
  onClick?: () => void;
  className?: string;
}

export function SortIndicator({
  field,
  order,
  isActive,
  onClick,
  className
}: SortIndicatorProps) {
  const getIcon = () => {
    if (!isActive) return <ChevronsUpDown size={16} />;
    return order === 'asc' ? <ArrowUp size={16} /> : <ArrowDown size={16} />;
  };

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 px-2 py-1 rounded text-sm font-medium transition-colors",
        isActive
          ? "bg-blue-100 text-blue-800 hover:bg-blue-200"
          : "text-gray-600 hover:bg-gray-100",
        className
      )}
      aria-label={`Sort by ${field} ${order}`}
    >
      {getIcon()}
      <span className="capitalize">{field.replace('_', ' ')}</span>
      {isActive && <span>({order})</span>}
    </button>
  );
}

// Simple Sort Selector Component - for use in headers
export interface SimpleSortSelectorProps {
  currentField: SortField;
  currentOrder: SortOrder;
  onSortChange: (field: SortField, order: SortOrder) => void;
  availableFields?: SortField[];
  className?: string;
}

export function SimpleSortSelector({
  currentField,
  currentOrder,
  onSortChange,
  availableFields = ['priority', 'due_date', 'created_at', 'title', 'completed'],
  className
}: SimpleSortSelectorProps) {
  const cycleSortOrder = () => {
    if (currentOrder === 'asc') {
      onSortChange(currentField, 'desc');
    } else if (currentOrder === 'desc') {
      onSortChange('created_at', 'desc');
    } else {
      onSortChange(currentField, 'asc');
    }
  };

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Select
        value={currentField}
        onValueChange={(val: SortField) => onSortChange(val, currentOrder)}
      >
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          {availableFields.map(field => (
            <SelectItem key={field} value={field}>
              {field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ')}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        variant="ghost"
        size="sm"
        onClick={cycleSortOrder}
        className="p-1.5"
      >
        {currentOrder === 'asc' ? (
          <ArrowUp size={16} className="text-gray-600" />
        ) : currentOrder === 'desc' ? (
          <ArrowDown size={16} className="text-gray-600" />
        ) : (
          <ChevronsUpDown size={16} className="text-gray-400" />
        )}
      </Button>
    </div>
  );
}