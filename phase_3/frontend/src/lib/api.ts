const axios = require('axios');

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: any) => {
    // Check if running in browser environment
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      const token = localStorage.getItem('auth-token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response: any) => {
    return response;
  },
  (error: any) => {
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Check if running in browser environment
      if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
        // Token might be expired, redirect to login
        localStorage.removeItem('auth-token');
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// Export convenience methods
export const api = {
  get: (url: string, config?: any) => apiClient.get(url, config),

  post: (url: string, data?: any, config?: any) => apiClient.post(url, data, config),

  put: (url: string, data?: any, config?: any) => apiClient.put(url, data, config),

  delete: (url: string, config?: any) => apiClient.delete(url, config),

  patch: (url: string, data?: any, config?: any) => apiClient.patch(url, data, config),
};

// Specific API functions for tasks
export const taskApi = {
  getAll: () => api.get('/todos', {}),
  getById: (id: string) => api.get(`/todos/${id}`, {}),
  create: (taskData: any) => api.post('/todos', taskData, {}),
  update: (id: string, taskData: any) => api.put(`/todos/${id}`, taskData, {}),
  delete: (id: string) => api.delete(`/todos/${id}`, {}),
};

// Specific API functions for auth
export const authApi = {
  login: (credentials: any) => api.post('/auth/login', credentials, {}),
  register: (userData: any) => api.post('/auth/register', userData, {}),
  logout: () => api.post('/auth/logout', {}, {}),
  getCurrentUser: () => api.get('/auth/me', {}),
};

// Specific API functions for chat
export const chatApi = {
  sendMessage: (messageData: any) => api.post('/chat', messageData, {}),
  getConversations: () => api.get('/chat/conversations', {}),
  getConversation: (id: string) => api.get(`/chat/conversations/${id}`, {}),
  createConversation: (title?: string) => api.post('/chat/conversations', title ? { title } : {}, {}),
};