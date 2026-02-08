import React from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/tasks/ui/badge';
import { Button } from '@/components/tasks/ui/button';
import {
  ArrowDownIcon,
  MinusIcon,
  ArrowUpIcon,
  ChevronDownIcon
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/tasks/ui/dropdown-menu';

export type Priority = 'low' | 'medium' | 'high';

interface PrioritySelectorProps {
  value: Priority;
  onChange: (priority: Priority) => void;
  disabled?: boolean;
  className?: string;
  variant?: 'dropdown' | 'buttons';
  size?: 'sm' | 'md' | 'lg';
}

const PRIORITY_OPTIONS: Array<{
  value: Priority;
  label: string;
  icon: React.ReactNode;
  badgeVariant: 'secondary' | 'default' | 'destructive' | 'outline';
  buttonVariant: 'default' | 'outline' | 'secondary' | 'ghost' | 'link';
  colorClass: string;
  bgClass: string;
}> = [
  {
    value: 'low',
    label: 'Low',
    icon: <ArrowDownIcon className="w-4 h-4" />,
    badgeVariant: 'secondary',
    buttonVariant: 'outline',
    colorClass: 'text-green-700',
    bgClass: 'bg-green-100'
  },
  {
    value: 'medium',
    label: 'Medium',
    icon: <MinusIcon className="w-4 h-4" />,
    badgeVariant: 'default',
    buttonVariant: 'outline',
    colorClass: 'text-yellow-700',
    bgClass: 'bg-yellow-100'
  },
  {
    value: 'high',
    label: 'High',
    icon: <ArrowUpIcon className="w-4 h-4" />,
    badgeVariant: 'destructive',
    buttonVariant: 'outline',
    colorClass: 'text-red-700',
    bgClass: 'bg-red-100'
  }
];

export function PrioritySelector({
  value,
  onChange,
  disabled = false,
  className,
  variant = 'dropdown',
  size = 'md'
}: PrioritySelectorProps) {
  const currentOption = PRIORITY_OPTIONS.find(opt => opt.value === value);

  if (variant === 'buttons') {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        {PRIORITY_OPTIONS.map((option) => {
          const isSelected = value === option.value;

          return (
            <Button
              key={option.value}
              variant={isSelected ? option.buttonVariant : 'outline'}
              size={size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'default'}
              onClick={() => onChange(option.value)}
              disabled={disabled}
              className={cn(
                'transition-colors duration-200',
                isSelected ? option.colorClass : '',
                isSelected ? option.bgClass.replace('bg-', 'hover:') : '',
                disabled && 'opacity-50 cursor-not-allowed'
              )}
              aria-label={`Set priority to ${option.label}`}
              aria-pressed={isSelected}
            >
              {option.icon}
              <span className="ml-1">{option.label}</span>
            </Button>
          );
        })}
      </div>
    );
  }

  // Default to dropdown variant
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size={size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'default'}
          disabled={disabled}
          className={cn(
            'justify-between',
            currentOption?.colorClass,
            className,
            disabled && 'opacity-50 cursor-not-allowed'
          )}
          aria-label="Select task priority"
        >
          <div className="flex items-center gap-2">
            {currentOption?.icon}
            <span>{currentOption?.label}</span>
          </div>
          <ChevronDownIcon className="w-4 h-4 ml-2 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-48">
        {PRIORITY_OPTIONS.map((option) => (
          <DropdownMenuItem
            key={option.value}
            onClick={() => onChange(option.value)}
            className={cn(
              'flex items-center gap-2',
              option.colorClass
            )}
          >
            {option.icon}
            <span>{option.label}</span>
            {value === option.value && (
              <span className="ml-auto">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// Badge component for displaying priority in task lists
interface PriorityBadgeProps {
  priority: Priority;
  className?: string;
  showLabel?: boolean;
}

export function PriorityBadge({
  priority,
  className,
  showLabel = true
}: PriorityBadgeProps) {
  const option = PRIORITY_OPTIONS.find(opt => opt.value === priority);

  if (!option) return null;

  return (
    <Badge
      variant={option.badgeVariant}
      className={cn(
        option.colorClass,
        option.bgClass,
        'flex items-center gap-1.5',
        className
      )}
    >
      {option.icon}
      {showLabel && <span>{option.label}</span>}
    </Badge>
  );
}

// Usage example as a comment:
/*
// In a form component:
function TaskForm() {
  const [priority, setPriority] = useState<Priority>('medium');

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="priority" className="block text-sm font-medium mb-2">
          Priority
        </label>
        <PrioritySelector
          value={priority}
          onChange={setPriority}
          variant="buttons"
        />
      </div>

      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Task Title
        </label>
        <input id="title" className="w-full p-2 border rounded" />
      </div>
    </div>
  );
}

// In a task list:
function TaskItem({ task }) {
  return (
    <div className="flex items-center justify-between p-4 border-b">
      <div>
        <h3 className="font-medium">{task.title}</h3>
        <p className="text-sm text-gray-500">{task.description}</p>
      </div>
      <PriorityBadge priority={task.priority} />
    </div>
  );
}
*/