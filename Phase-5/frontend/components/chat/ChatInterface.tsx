'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { Search, Filter, X, Bell, MessageCircle, Clock, Plus, Trash2 } from 'lucide-react';
import { ChatInterface } from '../tasks/ChatInterface';

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface Conversation {
  id: number;
  title: string;
  last_message?: string; // Make optional
  updated_at: string;
  message_count: number;
}

interface UserProfile {
  user_id: string;
  email: string;
  name: string;
}

interface ChatInterfaceProps {
  user: UserProfile;
}

export default function ChatInterfaces({ user }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: 'Hello! I\'m your AI assistant. You can ask me to create, list, or manage your tasks.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const [showChatInterface, setShowChatInterface] = useState(false);
  const router = useRouter();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Create a new conversation on component mount
  useEffect(() => {
    createNewConversation();
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const response = await apiClient.get<Conversation[]>('/chat/conversations');
      setConversations(response || []);
      
      // Set first conversation as active if no current conversation
      if (response && response.length > 0 && !currentConversationId) {
        setCurrentConversationId(response[0].id);
        loadConversationMessages(response[0].id);
      }
    } catch (error: any) {
      console.error('❌ Failed to load conversations:', error);
      setError('Failed to load conversation history');
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId: number) => {
    try {
      setIsLoading(true);
      const response = await apiClient.get<Message[]>(`/chat/conversations/${conversationId}/messages`);
      
      if (response && response.length > 0) {
        setMessages(response);
      } else {
        setMessages([
          { 
            role: 'assistant', 
            content: 'New conversation started.',
            timestamp: new Date().toISOString()
          }
        ]);
      }
      setCurrentConversationId(conversationId);
    } catch (error: any) {
      console.error('❌ Failed to load messages:', error);
      setMessages([
        { 
          role: 'assistant', 
          content: 'Error loading conversation. Starting fresh.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = async () => {
    try {
      console.log('📝 Creating new conversation...');
      const response = await apiClient.post<{ id: number }>('/chat/conversations', {
        title: 'New Conversation'
      });
      
      console.log('✅ Conversation created:', response);
      
      if (response && response.id) {
        setCurrentConversationId(response.id);
        await loadConversations(); // Refresh the sidebar
        console.log('✅ Conversation ID set to:', response.id);
      } else {
        console.error('❌ Invalid response format:', response);
        setError('Failed to create conversation - invalid response');
      }
    } catch (error: any) {
      console.error('❌ Failed to create conversation:', error);
      setError('Failed to create conversation: ' + (error.message || 'Unknown error'));
    }
  };

  const deleteConversation = async (conversationId: number) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    
    try {
      await apiClient.delete(`/chat/conversations/${conversationId}`);
      await loadConversations(); // Refresh list
      
      // If we deleted the current conversation, create a new one
      if (currentConversationId === conversationId) {
        await createNewConversation();
      }
    } catch (error: any) {
      console.error('❌ Failed to delete conversation:', error);
      setError('Failed to delete conversation');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const truncateText = (text: string | undefined | null, maxLength: number = 50) => {
    // Add null/undefined checks
    if (!text) return 'No messages yet';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Check if conversation exists
    if (!currentConversationId) {
      console.log('⚠️ No conversation ID, creating one...');
      await createNewConversation();
      // Wait for conversation to be created
      await new Promise(resolve => setTimeout(resolve, 500));
      
      if (!currentConversationId) {
        setError('Failed to create conversation. Please refresh the page.');
        return;
      }
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      console.log('📤 Sending message to conversation:', currentConversationId);
      console.log('📤 Message:', messageToSend);
      
      const response = await apiClient.post<{
        conversation_id: number;
        response: string;
        timestamp: string;
      }>(`/chat/conversations/${currentConversationId}/messages`, {
        message: messageToSend,
      });

      console.log('✅ Received response:', response);

      // Add assistant response to UI
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp || new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Refresh conversations to update last message
      await loadConversations();
    } catch (error: any) {
      console.error('❌ Error sending message:', error);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setError(error.message || 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    apiClient.clearToken();
    router.push('/login');
  };

  const handleNewChat = async () => {
    await createNewConversation();
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading user information...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
       
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="text-gray-600 hover:text-gray-900"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                </button>
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Task Assistant</h1>
                <p className="text-sm text-gray-600">
                  Logged in as {user?.name || 'User'} ({user?.email || ''})
                </p>
                {currentConversationId && (
                  <p className="text-xs text-gray-500 mt-1">
                    Conversation ID: {currentConversationId}
                  </p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowChatInterface(true)}
                className="relative p-2 text-gray-600 hover:text-gray-900 rounded-md transition"
                title="Open AI Task Assistant"
              >
                <MessageCircle className="h-5 w-5" />
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border-b border-red-200 p-3">
            <div className="flex justify-between items-center">
              <p className="text-red-600 text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-800 hover:text-red-900"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`p-4 rounded-lg max-w-[80%] shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-800 border border-gray-200'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                  {msg.timestamp && (
                    <div className={`text-xs mt-2 ${
                      msg.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                    }`}>
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 border border-gray-200 p-4 rounded-lg shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <span className="text-sm ml-2">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4 shadow-lg">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={currentConversationId ? "Type your message... (e.g., 'Create a task to buy groceries')" : "Setting up conversation..."}
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={isLoading || !currentConversationId}
              />
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isLoading || !inputValue.trim() || !currentConversationId}
              >
                {isLoading ? (
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  'Send'
                )}
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2 text-center">
              Try: "Create a task", "List my tasks", "Mark task 1 as complete"
            </p>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      {showChatInterface && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh]">
            <ChatInterface
              userId={user.user_id}
              onClose={() => setShowChatInterface(false)}
              onTaskOperation={(operation) => {
                console.log('AI assistant task operation:', operation);
                // Handle task refresh if needed
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}