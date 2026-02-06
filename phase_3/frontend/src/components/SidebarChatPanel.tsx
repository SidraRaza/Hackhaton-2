'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { Button } from './ui/button';
import { ChatMessage } from '../lib/types';
import AiLoadingSpinner from './AiLoadingSpinner';
import { AIErrorHandler } from '../utils/aiErrorHandler';

interface SidebarChatPanelProps {
  isExpanded: boolean;
}

export const SidebarChatPanel: React.FC<SidebarChatPanelProps> = ({ isExpanded }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      content: 'Hello! I\'m your AI assistant. How can I help you today?',
      timestamp: new Date(Date.now() - 300000), // 5 minutes ago
      status: 'read',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      setIsLoading(true);

      // Add user message
      const newUserMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        sender: 'user',
        content: inputValue,
        timestamp: new Date(),
        status: 'sent',
      };

      setMessages(prev => [...prev, newUserMessage]);
      setInputValue('');

      try {
        // Simulate AI response after a delay
        // In a real implementation, this would call the AI service
        await new Promise(resolve => setTimeout(resolve, 1000));

        const aiResponse: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          sender: 'assistant',
          content: `I received your message: "${inputValue}". This is a simulated response from the AI assistant. How else can I help you?`,
          timestamp: new Date(),
          status: 'delivered',
        };

        setMessages(prev => [...prev, aiResponse]);
      } catch (error) {
        // Handle error with user-friendly message
        const errorMessage: ChatMessage = {
          id: `msg-${Date.now() + 2}`,
          sender: 'assistant',
          content: AIErrorHandler.handleAIError(error),
          timestamp: new Date(),
          status: 'read',
        };

        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Format timestamp for display
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="p-3 border-b border-border flex items-center gap-2">
        <Bot className="h-5 w-5 text-primary" />
        <h3 className="font-medium text-foreground">AI Assistant</h3>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4 bg-muted/5">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 ${
                message.sender === 'user'
                  ? 'bg-primary text-primary-foreground rounded-br-none'
                  : 'bg-secondary text-secondary-foreground rounded-bl-none'
              }`}
            >
              <div className="flex items-start gap-2">
                {message.sender === 'assistant' && (
                  <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                )}
                <div className="whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                {message.sender === 'user' && (
                  <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                )}
              </div>
              <div className="text-xs opacity-70 mt-1 text-right">
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-secondary text-secondary-foreground rounded-lg px-3 py-2 rounded-bl-none max-w-[85%]">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                <AiLoadingSpinner size="sm" message="" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-border">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isExpanded ? "Ask me anything..." : ""}
            className="flex-1 px-3 py-2 border border-border rounded-md text-sm bg-background focus:outline-none focus:ring-1 focus:ring-primary"
            disabled={isLoading}
          />
          <Button type="submit" size="sm" disabled={!inputValue.trim() || isLoading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
};