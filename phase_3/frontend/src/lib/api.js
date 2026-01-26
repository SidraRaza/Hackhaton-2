/**
 * API Helper Functions for the Todo App
 */

// Base API URL - defaults to localhost if not set in environment
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api';

// Default headers for API requests
const getDefaultHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('auth-token') || ''}`
});

/**
 * Generic API request function
 */
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      ...getDefaultHeaders(),
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, config);

    // If response is not ok, throw an error with the response text
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    // For successful responses, return the JSON
    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

/**
 * Chat API functions
 */

// Send a message to the chat endpoint
export const sendMessage = async (message, conversationId = null) => {
  const payload = {
    message: message
  };

  if (conversationId) {
    payload.conversation_id = conversationId;
  }

  return apiRequest('/chat', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
};

// Get all conversations for the current user
export const getUserConversations = async () => {
  return apiRequest('/chat/conversations');
};

// Get a specific conversation with its messages
export const getConversationById = async (conversationId) => {
  return apiRequest(`/chat/conversations/${conversationId}`);
};

// Create a new conversation
export const createConversation = async (title = null) => {
  const payload = {};
  if (title) {
    payload.title = title;
  }

  return apiRequest('/chat/conversations', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
};

/**
 * Task API functions (existing)
 */

// Get all tasks for the current user
export const getTasks = async () => {
  return apiRequest('/tasks');
};

// Create a new task
export const createTask = async (taskData) => {
  return apiRequest('/tasks', {
    method: 'POST',
    body: JSON.stringify(taskData)
  });
};

// Update a task
export const updateTask = async (taskId, taskData) => {
  return apiRequest(`/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(taskData)
  });
};

// Delete a task
export const deleteTask = async (taskId) => {
  return apiRequest(`/tasks/${taskId}`, {
    method: 'DELETE'
  });
};

// Toggle task completion
export const toggleTaskCompletion = async (taskId) => {
  return apiRequest(`/tasks/${taskId}/toggle`, {
    method: 'PUT'
  });
};

/**
 * Auth API functions (existing)
 */

// Sign up a new user
export const signUp = async (userData) => {
  return apiRequest('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(userData)
  });
};

// Sign in an existing user
export const signIn = async (credentials) => {
  return apiRequest('/auth/signin', {
    method: 'POST',
    body: JSON.stringify(credentials)
  });
};

// Get current user info
export const getCurrentUser = async () => {
  return apiRequest('/auth/me');
};

// Sign out the current user
export const signOut = async () => {
  localStorage.removeItem('auth-token');
  return { success: true, message: 'Signed out successfully' };
};

export default {
  sendMessage,
  getUserConversations,
  getConversationById,
  createConversation,
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskCompletion,
  signUp,
  signIn,
  getCurrentUser,
  signOut
};