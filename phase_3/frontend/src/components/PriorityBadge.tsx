import React from 'react';
import { Badge } from './ui/badge';
import { BadgeProps } from './ui/badge';
import { cn } from '../lib/utils';

interface PriorityBadgeProps extends BadgeProps {
  priority: 'low' | 'medium' | 'high';
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority,
  className,
  ...props
}) => {
  const priorityStyles = {
    low: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900 dark:text-green-100 dark:border-green-800',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-100 dark:border-yellow-800',
    high: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-100 dark:border-red-800',
  };

  return (
    <Badge
      className={cn(
        priorityStyles[priority],
        'capitalize',
        className
      )}
      {...props}
    >
      {priority}
    </Badge>
  );
};