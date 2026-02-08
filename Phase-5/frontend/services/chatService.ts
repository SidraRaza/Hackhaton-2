import { apiClient } from '@/lib/api';

export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: string;
  status: 'sending' | 'sent' | 'delivered' | 'error';
  user_id?: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  suggestions?: string[];
  task_operations?: Array<{
    operation: 'create' | 'update' | 'delete' | 'search';
    task_data?: any;
    task_ids?: number[];
  }>;
}

export class ChatService {
  /**
   * Send a message to the AI assistant
   */
  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>('/chat/messages', request);
      return response;
    } catch (error) {
      console.error('Failed to send chat message:', error);
      throw error;
    }
  }

  /**
   * Create a new conversation
   */
  static async createConversation(): Promise<Conversation> {
    try {
      const response = await apiClient.post<Conversation>('/chat/conversations', {});
      return response;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  }

  /**
   * Get conversation details
   */
  static async getConversation(conversationId: string): Promise<Conversation> {
    try {
      const response = await apiClient.get<Conversation>(`/chat/conversations/${conversationId}`);
      return response;
    } catch (error) {
      console.error('Failed to get conversation:', error);
      throw error;
    }
  }

  /**
   * Get all conversations for the user
   */
  static async getConversations(): Promise<Conversation[]> {
    try {
      const response = await apiClient.get<Conversation[]>('/chat/conversations');
      return response || [];
    } catch (error) {
      console.error('Failed to get conversations:', error);
      return [];
    }
  }

  /**
   * Get messages for a conversation
   */
  static async getMessages(conversationId: string): Promise<ChatMessage[]> {
    try {
      const response = await apiClient.get<ChatMessage[]>(`/chat/conversations/${conversationId}/messages`);
      return response || [];
    } catch (error) {
      console.error('Failed to get messages:', error);
      return [];
    }
  }

  /**
   * Delete a conversation
   */
  static async deleteConversation(conversationId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/chat/conversations/${conversationId}`);
      return true;
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      return false;
    }
  }

  /**
   * Process a natural language task command
   */
  static async processNaturalLanguageCommand(command: string, conversationId?: string): Promise<ChatResponse> {
    try {
      // For now, we'll use the standard sendMessage method which should handle natural language processing
      // In a real implementation, this might be a separate endpoint
      return await this.sendMessage({
        message: command,
        conversation_id: conversationId
      });
    } catch (error) {
      console.error('Failed to process natural language command:', error);
      throw error;
    }
  }
}