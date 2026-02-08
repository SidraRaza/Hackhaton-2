import React, { useState, useEffect } from 'react';
import { Clock, Repeat, Calendar, Settings, X, Plus, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/tasks/ui/button';
import { Input } from '@/components/tasks/ui/input';
import { Label } from '@/components/tasks/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/tasks/ui/select';
import { Badge } from '@/components/tasks/ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/tasks/ui/popover';
import { Checkbox } from '@/components/tasks/ui/checkbox';

export type RecurrencePattern = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

export interface RecurrenceConfig {
  pattern: RecurrencePattern;
  interval?: number;
  days_of_week?: number[]; // 0=Monday, 6=Sunday
  day_of_month?: number;
  end_condition?: {
    type: 'never' | 'after_occurrences' | 'until_date';
    value?: string | number;
  };
  cron_expression?: string;
}

export interface RecurrencePatternSelectorProps {
  value: RecurrenceConfig | null;
  onChange: (config: RecurrenceConfig | null) => void;
  disabled?: boolean;
  className?: string;
}

export function RecurrencePatternSelector({
  value,
  onChange,
  disabled = false,
  className
}: RecurrencePatternSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [localConfig, setLocalConfig] = useState<RecurrenceConfig>({
    pattern: 'daily',
    interval: 1,
    end_condition: { type: 'never' }
  });

  useEffect(() => {
    if (value) {
      setLocalConfig(value);
    } else {
      setLocalConfig({
        pattern: 'daily',
        interval: 1,
        end_condition: { type: 'never' }
      });
    }
  }, [value]);

  const handlePatternChange = (pattern: RecurrencePattern) => {
    const newConfig = { ...localConfig, pattern };

    // Set default configuration based on pattern
    switch (pattern) {
      case 'daily':
        newConfig.interval = 1;
        break;
      case 'weekly':
        newConfig.interval = 1;
        newConfig.days_of_week = [0]; // Default to Monday
        break;
      case 'monthly':
        newConfig.interval = 1;
        newConfig.day_of_month = new Date().getDate(); // Default to current day
        break;
      case 'yearly':
        newConfig.interval = 1;
        break;
      case 'custom':
        newConfig.cron_expression = '0 9 * * *'; // Default to daily at 9 AM
        break;
    }

    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const handleIntervalChange = (interval: number) => {
    const newConfig = { ...localConfig, interval };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const toggleDayOfWeek = (day: number) => {
    if (localConfig.pattern !== 'weekly') return;

    const days = localConfig.days_of_week || [];
    const newDays = days.includes(day)
      ? days.filter(d => d !== day)
      : [...days, day];

    const newConfig = { ...localConfig, days_of_week: newDays };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const handleDayOfMonthChange = (day: number) => {
    if (localConfig.pattern !== 'monthly') return;

    const newConfig = { ...localConfig, day_of_month: day };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const handleEndConditionChange = (type: 'never' | 'after_occurrences' | 'until_date', value?: string | number) => {
    const newConfig = {
      ...localConfig,
      end_condition: {
        type,
        value: value !== undefined ? value : localConfig.end_condition?.value
      }
    };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const handleCronExpressionChange = (expression: string) => {
    if (localConfig.pattern !== 'custom') return;

    const newConfig = { ...localConfig, cron_expression: expression };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const clearRecurrence = () => {
    onChange(null);
    setLocalConfig({
      pattern: 'daily',
      interval: 1,
      end_condition: { type: 'never' }
    });
  };

  const getPatternLabel = (pattern: RecurrencePattern): string => {
    switch (pattern) {
      case 'daily': return 'Daily';
      case 'weekly': return 'Weekly';
      case 'monthly': return 'Monthly';
      case 'yearly': return 'Yearly';
      case 'custom': return 'Custom';
    }
  };

  const getPatternDescription = (config: RecurrenceConfig): string => {
    if (!config) return 'Does not repeat';

    switch (config.pattern) {
      case 'daily':
        return config.interval === 1
          ? 'Every day'
          : `Every ${config.interval} days`;

      case 'weekly':
        if (config.days_of_week && config.days_of_week.length > 0) {
          const days = config.days_of_week.map(day =>
            ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day]
          ).join(', ');
          return config.interval === 1
            ? `Weekly on ${days}`
            : `Every ${config.interval} weeks on ${days}`;
        }
        return config.interval === 1
          ? 'Weekly'
          : `Every ${config.interval} weeks`;

      case 'monthly':
        if (config.day_of_month) {
          return config.interval === 1
            ? `Monthly on day ${config.day_of_month}`
            : `Every ${config.interval} months on day ${config.day_of_month}`;
        }
        return config.interval === 1
          ? 'Monthly'
          : `Every ${config.interval} months`;

      case 'yearly':
        return config.interval === 1
          ? 'Yearly'
          : `Every ${config.interval} years`;

      case 'custom':
        return `Custom (${config.cron_expression || 'no expression'})`;

      default:
        return 'Does not repeat';
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-between",
            className,
            value && "border-primary bg-primary/5"
          )}
          disabled={disabled}
        >
          <div className="flex items-center gap-2">
            <Repeat size={16} />
            <span>
              {value ? getPatternDescription(value) : 'Does not repeat'}
            </span>
          </div>
          <Settings size={16} />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-4 bg-white" align="start">
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-semibold">Recurrence Pattern</h3>
            {value && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearRecurrence}
                className="text-destructive hover:text-destructive"
              >
                <X size={16} />
                <span className="ml-1">Clear</span>
              </Button>
            )}
          </div>

          {/* Pattern selection */}
          <div>
            <Label>Pattern</Label>
            <Select
              value={localConfig.pattern}
              onValueChange={(v: RecurrencePattern) => handlePatternChange(v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select pattern" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
                <SelectItem value="custom">Custom (Cron)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Interval input */}
          <div>
            <Label>Repeat every</Label>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="1"
                value={localConfig.interval || 1}
                onChange={(e) => handleIntervalChange(parseInt(e.target.value) || 1)}
                className="w-20"
              />
              <span className="text-sm text-muted-foreground">
                {localConfig.pattern === 'daily' && 'day(s)'}
                {localConfig.pattern === 'weekly' && 'week(s)'}
                {localConfig.pattern === 'monthly' && 'month(s)'}
                {localConfig.pattern === 'yearly' && 'year(s)'}
              </span>
            </div>
          </div>

          {/* Weekly specific options */}
          {localConfig.pattern === 'weekly' && (
            <div>
              <Label>On days</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
                  <div key={day} className="flex items-center space-x-2">
                    <Checkbox
                      id={`day-${index}`}
                      checked={localConfig.days_of_week?.includes(index) ?? false}
                      onCheckedChange={() => toggleDayOfWeek(index)}
                    />
                    <label htmlFor={`day-${index}`} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      {day}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Monthly specific options */}
          {localConfig.pattern === 'monthly' && (
            <div>
              <Label>On day of month</Label>
              <Input
                type="number"
                min="1"
                max="31"
                value={localConfig.day_of_month || new Date().getDate()}
                onChange={(e) => handleDayOfMonthChange(parseInt(e.target.value) || 1)}
                className="w-20"
              />
            </div>
          )}

          {/* Custom cron expression */}
          {localConfig.pattern === 'custom' && (
            <div>
              <Label>Cron Expression</Label>
              <Input
                value={localConfig.cron_expression || ''}
                onChange={(e) => handleCronExpressionChange(e.target.value)}
                placeholder="0 9 * * *" // Example: daily at 9 AM
              />
              <p className="text-xs text-muted-foreground mt-1">
                Format: minute hour day month day-of-week (e.g., "0 9 * * *" for daily at 9 AM)
              </p>
            </div>
          )}

          {/* End condition */}
          <div>
            <Label>End condition</Label>
            <Select
              value={localConfig.end_condition?.type || 'never'}
              onValueChange={(v: 'never' | 'after_occurrences' | 'until_date') => handleEndConditionChange(v as 'never' | 'after_occurrences' | 'until_date')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select end condition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="never">Never</SelectItem>
                <SelectItem value="after_occurrences">After occurrences</SelectItem>
                <SelectItem value="until_date">Until date</SelectItem>
              </SelectContent>
            </Select>

            {localConfig.end_condition?.type === 'after_occurrences' && (
              <div className="mt-2">
                <Label>Number of occurrences</Label>
                <Input
                  type="number"
                  min="1"
                  value={localConfig.end_condition.value || 1}
                  onChange={(e) => handleEndConditionChange('after_occurrences', parseInt(e.target.value) || 1)}
                  className="w-20"
                />
              </div>
            )}

            {localConfig.end_condition?.type === 'until_date' && (
              <div className="mt-2">
                <Label>End date</Label>
                <Input
                  type="date"
                  value={localConfig.end_condition.value as string || ''}
                  onChange={(e) => handleEndConditionChange('until_date', e.target.value)}
                />
              </div>
            )}
          </div>

          {/* Preview */}
          <div className="pt-2 border-t">
            <Label>Preview</Label>
            <div className="mt-2 p-3 bg-muted rounded-md">
              <p className="text-sm">
                {getPatternDescription(localConfig)}
              </p>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Helper functions to be used by RecurrenceBadge component
const getPatternLabelHelper = (pattern: RecurrencePattern): string => {
  switch (pattern) {
    case 'daily': return 'Daily';
    case 'weekly': return 'Weekly';
    case 'monthly': return 'Monthly';
    case 'yearly': return 'Yearly';
    case 'custom': return 'Custom';
  }
};

const getPatternDescriptionHelper = (config: RecurrenceConfig): string => {
  if (!config) return 'Does not repeat';

  switch (config.pattern) {
    case 'daily':
      return config.interval === 1
        ? 'Every day'
        : `Every ${config.interval} days`;

    case 'weekly':
      if (config.days_of_week && config.days_of_week.length > 0) {
        const days = config.days_of_week.map(day =>
          ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day]
        ).join(', ');
        return config.interval === 1
          ? `Weekly on ${days}`
          : `Every ${config.interval} weeks on ${days}`;
      }
      return config.interval === 1
        ? 'Weekly'
        : `Every ${config.interval} weeks`;

    case 'monthly':
      if (config.day_of_month) {
        return config.interval === 1
          ? `Monthly on day ${config.day_of_month}`
          : `Every ${config.interval} months on day ${config.day_of_month}`;
      }
      return config.interval === 1
        ? 'Monthly'
        : `Every ${config.interval} months`;

    case 'yearly':
      return config.interval === 1
        ? 'Yearly'
        : `Every ${config.interval} years`;

    case 'custom':
      return `Custom (${config.cron_expression || 'no expression'})`;

    default:
      return 'Does not repeat';
  }
};

// Export a simple component for displaying recurrence badges
interface RecurrenceBadgeProps {
  config: RecurrenceConfig;
  className?: string;
}

export function RecurrenceBadge({ config, className }: RecurrenceBadgeProps) {
  if (!config) {
    return null;
  }

  const patternLabel = getPatternLabelHelper(config.pattern);
  const patternDescription = getPatternDescriptionHelper(config);

  return (
    <Badge
      variant="secondary"
      className={cn("flex items-center gap-1.5", className)}
      title={patternDescription}
    >
      <Repeat size={12} />
      <span>{patternLabel}</span>
    </Badge>
  );
}

export default RecurrencePatternSelector;