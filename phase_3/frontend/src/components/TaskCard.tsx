'use client';

import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { MoreHorizontal, Edit3, Trash2, CheckCircle, Circle, Clock, Calendar } from 'lucide-react';
import { TaskApiResponse } from '../lib/types';
import { motion, AnimatePresence } from 'framer-motion';

interface TaskCardProps {
  task: TaskApiResponse;
  onEdit?: (task: TaskApiResponse) => void;
  onDelete?: (id: string) => void;
  onToggleStatus?: (id: string, newStatus: 'pending' | 'in-progress' | 'completed') => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onEdit,
  onDelete,
  onToggleStatus
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(task.description || '');

  const handleSave = () => {
    // In a real app, this would call an API to update the task
    const updatedTask = { ...task, title: editedTitle, description: editedDescription };
    onEdit?.(updatedTask);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTitle(task.title);
    setEditedDescription(task.description || '');
    setIsEditing(false);
  };

  const handleStatusToggle = () => {
    let newStatus: 'pending' | 'in-progress' | 'completed' = 'pending';
    if (task.status === 'pending') newStatus = 'in-progress';
    else if (task.status === 'in-progress') newStatus = 'completed';
    else newStatus = 'pending';

    onToggleStatus?.(task.id, newStatus);
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="h-full"
    >
      <Card className="h-full flex flex-col border-border bg-background shadow-none hover:shadow-sm transition-shadow duration-200">
        <CardContent className="p-3 flex-1 flex flex-col">
          <div className="flex justify-between items-start mb-2">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleStatusToggle}
                className="p-1 h-auto w-auto hover:bg-transparent"
              >
                {task.status === 'completed' ? (
                  <CheckCircle className="h-4 w-4 text-primary" />
                ) : (
                  <Circle className="h-4 w-4 text-border" />
                )}
              </Button>
              <h3 className="font-medium text-foreground truncate text-sm">
                {task.title}
              </h3>
            </div>
          </div>

          {task.description && (
            <p className="text-xs text-text-muted mb-2 flex-1">
              {task.description}
            </p>
          )}

          <div className="flex flex-wrap gap-1 mb-2">
            <Badge variant={task.priority} className="text-xs px-2 py-0.5">
              {task.priority}
            </Badge>
            <Badge
              variant="outline"
              className="text-xs px-2 py-0.5 border-border text-text-muted"
            >
              {task.status.replace('-', ' ')}
            </Badge>
          </div>

          {task.dueDate && (
            <div className="flex items-center text-xs text-text-muted mb-2">
              <Calendar className="h-3 w-3 mr-1" />
              <span>Due: {formatDate(task.dueDate)}</span>
            </div>
          )}

          <div className="flex justify-end items-center mt-auto pt-1 border-t border-border">
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit?.(task)}
                className="p-1 h-7 w-7 text-text-muted hover:text-foreground hover:bg-muted"
              >
                <Edit3 className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete?.(task.id)}
                className="p-1 h-7 w-7 text-text-muted hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};