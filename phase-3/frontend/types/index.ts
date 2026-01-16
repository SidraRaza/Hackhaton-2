export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}