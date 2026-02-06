'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, X } from 'lucide-react';
import { Button } from './ui/button';
import { MessageBubble } from './MessageBubble';
import { ChatMessage } from '../lib/types';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      content: 'Hello! I\'m your AI assistant. How can I help you today?',
      timestamp: new Date(Date.now() - 300000), // 5 minutes ago
      status: 'read',
    },
    {
      id: '2',
      sender: 'user',
      content: 'Can you help me organize my tasks?',
      timestamp: new Date(Date.now() - 240000), // 4 minutes ago
      status: 'read',
    },
    {
      id: '3',
      sender: 'assistant',
      content: 'Of course! You can categorize your tasks by priority or due date. Would you like me to suggest a specific organization method?',
      timestamp: new Date(Date.now() - 180000), // 3 minutes ago
      status: 'read',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const newUserMessage: ChatMessage = {
        id: (messages.length + 1).toString(),
        sender: 'user',
        content: inputValue,
        timestamp: new Date(),
        status: 'sent',
      };

      setMessages(prev => [...prev, newUserMessage]);
      setInputValue('');

      // Simulate AI response after a delay
      setTimeout(() => {
        const aiResponse: ChatMessage = {
          id: (messages.length + 2).toString(),
          sender: 'assistant',
          content: `I received your message: "${inputValue}". This is a simulated response from the AI assistant.`,
          timestamp: new Date(),
          status: 'delivered',
        };
        setMessages(prev => [...prev, aiResponse]);
      }, 1000);
    }
  };

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed bottom-24 right-6 z-50 w-80 max-w-[90vw] bg-background border border-border rounded-lg shadow-xl overflow-hidden flex flex-col h-[500px]"
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        >
          {/* Chat header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h3 className="font-semibold text-foreground">AI Assistant</h3>
            <Button variant="ghost" size="sm" onClick={onClose} className="p-1 h-auto">
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Messages container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/5">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                sender={message.sender}
                content={message.content}
                timestamp={message.timestamp}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-border">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-border rounded-md text-sm bg-background focus:outline-none focus:ring-1 focus:ring-primary"
                autoFocus
              />
              <Button type="submit" size="sm" disabled={!inputValue.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </motion.div>
      )}
    </AnimatePresence>
  );
};