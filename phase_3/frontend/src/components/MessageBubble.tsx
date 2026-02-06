import React from 'react';
import { cn } from '../lib/utils';

interface MessageBubbleProps {
  sender: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ sender, content, timestamp }) => {
  const isUser = sender === 'user';

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-2 text-sm',
          isUser
            ? 'bg-primary text-primary-foreground rounded-br-md'
            : 'bg-secondary text-secondary-foreground rounded-bl-md'
        )}
      >
        <div className="whitespace-pre-wrap">{content}</div>
        <div
          className={cn(
            'text-xs mt-1',
            isUser ? 'text-primary-foreground/70' : 'text-secondary-foreground/70'
          )}
        >
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};