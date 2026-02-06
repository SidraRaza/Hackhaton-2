// UI Configuration Entity
export interface UIConfig {
  theme: 'dark' | 'light';
  sidebarCollapsed: boolean;
  animationsEnabled: boolean;
  fontSize: 'small' | 'normal' | 'large';
}

// Task Card Entity
export interface TaskCard {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed';
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
  isEditing?: boolean;
}

// Navigation Item Entity
export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon?: string;
  isActive: boolean;
}

// Chat Message Entity
export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sent' | 'delivered' | 'read';
}

// User Profile Entity
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences: UIConfig;
}

// Dashboard Layout State
export interface DashboardLayoutState {
  sidebarWidth: number;
  isSidebarCollapsed: boolean;
  navbarHeight: number;
  contentPadding: number;
}

// Task Filtering Options
export interface TaskFilters {
  status: Array<'pending' | 'in-progress' | 'completed'>;
  priority: Array<'low' | 'medium' | 'high'>;
  searchTerm: string;
  dueDateRange: { start: Date; end: Date } | null;
}

// Animation States
export interface AnimationState {
  isAdding: boolean;
  isRemoving: boolean;
  isEditing: boolean;
  isTransitioning: boolean;
}

// Task API Response
export interface TaskApiResponse {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed'; // Aligns with backend TaskStatus enum
  dueDate?: string; // ISO string format
  createdAt: string; // ISO string format
  updatedAt: string; // ISO string format
  completedAt?: string; // ISO string format when status is 'completed'
}

// API Response for getting tasks
export interface GetTasksResponse {
  tasks: TaskApiResponse[];
  total: number;
  hasMore: boolean;
}

// Theme Context Type
export interface ThemeContextType {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
  isDarkMode: boolean;
}

// Navigation Context Type
export interface NavigationContextType {
  activeRoute: string;
  setActiveRoute: (route: string) => void;
}

// Sidebar State Entity
export interface SidebarState {
  id: string;
  isVisible: boolean;
  isCollapsed: boolean;
  width: number;
  position: 'left' | 'right';
  lastUpdated: Date;
}

// Assistant Config Entity
export interface AssistantConfig {
  id: string;
  serviceEndpoint: string;
  isAvailable: boolean;
  displayPreferences: Record<string, any>;
  lastConnectionCheck: Date;
  status: 'online' | 'offline' | 'error';
}