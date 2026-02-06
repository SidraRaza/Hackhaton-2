import React from 'react';
import { Badge } from './ui/badge';
import { BadgeProps } from './ui/badge';
import { Circle, CheckCircle2, CircleDot, Clock } from 'lucide-react';
import { cn } from '../lib/utils';

interface StatusIndicatorProps extends BadgeProps {
  status: 'todo' | 'in-progress' | 'completed';
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  className,
  ...props
}) => {
  const statusConfig = {
    todo: {
      text: 'To Do',
      icon: Circle,
      variant: 'outline',
      className: 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300',
    },
    'in-progress': {
      text: 'In Progress',
      icon: CircleDot,
      variant: 'warning',
      className: 'border-yellow-300 dark:border-yellow-600 text-yellow-700 dark:text-yellow-300',
    },
    completed: {
      text: 'Completed',
      icon: CheckCircle2,
      variant: 'success',
      className: 'border-green-300 dark:border-green-600 text-green-700 dark:text-green-300',
    },
  };

  const statusInfo = statusConfig[status];
  const Icon = statusInfo.icon;

  return (
    <Badge
      variant={statusInfo.variant as any}
      className={cn(
        statusInfo.className,
        'flex items-center gap-1',
        className
      )}
      {...props}
    >
      <Icon size={14} />
      <span className="capitalize">{statusInfo.text}</span>
    </Badge>
  );
};