import { useState, useEffect, useRef, KeyboardEvent } from 'react';
import { Send, Bot, User, Trash2, Plus } from 'lucide-react';
import { ChatService, ChatMessage, Conversation } from '@/services/chatService';

interface ChatInterfaceProps {
  userId: string;
  onClose?: () => void;
  onTaskOperation?: (operation: any) => void;
}

export const ChatInterface = ({
  userId,
  onClose,
  onTaskOperation
}: ChatInterfaceProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversation) {
      loadMessages(currentConversation.id);
    } else {
      setMessages([]);
    }
  }, [currentConversation]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const convs = await ChatService.getConversations();
      setConversations(convs);

      // Load the most recent conversation or create a new one if none exist
      if (convs.length > 0) {
        setCurrentConversation(convs[0]); // Most recent conversation
      } else {
        await createNewConversation();
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversations');
    }
  };

  const createNewConversation = async () => {
    try {
      const newConv = await ChatService.createConversation();
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
      setError(null);
      return newConv;
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError('Failed to create new conversation');
      return null;
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      setIsLoading(true);
      const msgs = await ChatService.getMessages(conversationId);
      setMessages(msgs);
      setError(null);
    } catch (err) {
      console.error('Failed to load messages:', err);
      setError('Failed to load messages');
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessageId = `temp_${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMessageId,
      conversation_id: currentConversation?.id || '',
      sender: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    // Add user message optimistically
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await ChatService.sendMessage({
        message: inputMessage.trim(),
        conversation_id: currentConversation?.id
      });

      // Add AI response
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        conversation_id: response.conversation_id,
        sender: 'ai',
        content: response.response,
        timestamp: new Date().toISOString(),
        status: 'sent'
      };

      setMessages(prev => [...prev, aiMessage]);

      // Handle any task operations returned by the AI
      if (response.task_operations && response.task_operations.length > 0) {
        response.task_operations.forEach(op => {
          if (onTaskOperation) {
            onTaskOperation(op);
          }
        });
      }

      // Update conversation if needed
      if (!currentConversation) {
        const newConv = await ChatService.getConversation(response.conversation_id);
        setCurrentConversation(newConv);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');

      // Update the user's message status to error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === userMessageId ? { ...msg, status: 'error' } : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      const success = await ChatService.deleteConversation(conversationId);
      if (success) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));

        // If deleting current conversation, switch to another or create new
        if (currentConversation?.id === conversationId) {
          const remainingConvs = conversations.filter(conv => conv.id !== conversationId);
          if (remainingConvs.length > 0) {
            setCurrentConversation(remainingConvs[0]);
          } else {
            await createNewConversation();
          }
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex h-[600px] w-full max-w-4xl bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* Sidebar - Conversation List */}
      <div className="w-64 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
            <button
              onClick={createNewConversation}
              className="p-1 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100"
              title="New conversation"
            >
              <Plus className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.map(conversation => (
            <div
              key={conversation.id}
              className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 flex justify-between items-center ${
                currentConversation?.id === conversation.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
              }`}
              onClick={() => setCurrentConversation(conversation)}
            >
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 truncate">
                  {conversation.title || 'New Conversation'}
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(conversation.id);
                }}
                className="p-1 text-gray-400 hover:text-red-500"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-md font-medium text-gray-900">
            {currentConversation?.title || 'AI Task Assistant'}
          </h3>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-4">
              {error}
            </div>
          )}

          {messages.length === 0 && !isLoading ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to AI Task Assistant</h3>
              <p className="text-gray-600 max-w-md">
                I can help you manage your tasks using natural language. Try asking me to create a task, find tasks, or update existing tasks.
              </p>
              <div className="mt-4 text-sm text-gray-500">
                <p>Examples:</p>
                <ul className="list-disc list-inside mt-2 text-left space-y-1">
                  <li>"Create a high priority task called 'Finish report' due tomorrow"</li>
                  <li>"Show me all tasks with due dates this week"</li>
                  <li>"Mark 'Buy groceries' as completed"</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.sender === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {message.sender === 'ai' ? (
                        <Bot className="h-4 w-4 flex-shrink-0" />
                      ) : (
                        <User className="h-4 w-4 flex-shrink-0" />
                      )}
                      <span className="text-xs font-medium">
                        {message.sender === 'ai' ? 'AI Assistant' : 'You'}
                      </span>
                      <span className="text-xs opacity-70 ml-auto">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    <div className={message.sender === 'user' ? 'text-white' : 'text-gray-800'}>
                      {message.content}
                    </div>
                    {message.status === 'error' && (
                      <div className="text-xs mt-1 text-red-200">Failed to send</div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center gap-2 mb-1">
                      <Bot className="h-4 w-4 flex-shrink-0" />
                      <span className="text-xs font-medium">AI Assistant</span>
                    </div>
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type a message to the AI assistant..."
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-indigo-600 text-white rounded-md p-2 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Ask me to create, update, search, or manage tasks using natural language
          </p>
        </div>
      </div>
    </div>
  );
};