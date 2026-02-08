import { apiClient } from '@/lib/api';
import { NotificationMessage } from '@/types/taskTypes';

export interface NotificationPreferences {
  browser_notifications: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  reminder_lead_times: string[]; // e.g., ["1h", "1d"]
  notification_types: {
    task_created: boolean;
    task_completed: boolean;
    task_due_soon: boolean;
    task_overdue: boolean;
    recurring_task_generated: boolean;
  };
}

export class NotificationService {
  /**
   * Get all notifications for the current user
   */
  static async getNotifications(): Promise<NotificationMessage[]> {
    try {
      const response = await apiClient.get<NotificationMessage[]>('/notifications');
      return response || [];
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      throw error;
    }
  }

  /**
   * Mark a notification as read
   */
  static async markNotificationAsRead(notificationId: string): Promise<boolean> {
    try {
      await apiClient.patch(`/notifications/${notificationId}/read`, {});
      return true;
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      return false;
    }
  }

  /**
   * Mark all notifications as read
   */
  static async markAllNotificationsAsRead(): Promise<boolean> {
    try {
      await apiClient.post('/notifications/mark-all-read', {});
      return true;
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
      return false;
    }
  }

  /**
   * Delete a notification
   */
  static async deleteNotification(notificationId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/notifications/${notificationId}`);
      return true;
    } catch (error) {
      console.error('Failed to delete notification:', error);
      return false;
    }
  }

  /**
   * Get user's notification preferences
   */
  static async getNotificationPreferences(): Promise<NotificationPreferences> {
    try {
      const response = await apiClient.get<NotificationPreferences>('/notifications/preferences');
      return response || {
        browser_notifications: true,
        email_notifications: false,
        push_notifications: false,
        reminder_lead_times: ["1h", "1d"],
        notification_types: {
          task_created: true,
          task_completed: true,
          task_due_soon: true,
          task_overdue: true,
          recurring_task_generated: true,
        }
      };
    } catch (error) {
      console.error('Failed to fetch notification preferences:', error);
      // Return default preferences
      return {
        browser_notifications: true,
        email_notifications: false,
        push_notifications: false,
        reminder_lead_times: ["1h", "1d"],
        notification_types: {
          task_created: true,
          task_completed: true,
          task_due_soon: true,
          task_overdue: true,
          recurring_task_generated: true,
        }
      };
    }
  }

  /**
   * Update user's notification preferences
   */
  static async updateNotificationPreferences(preferences: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    try {
      const response = await apiClient.put<NotificationPreferences>('/notifications/preferences', preferences);
      return response;
    } catch (error) {
      console.error('Failed to update notification preferences:', error);
      throw error;
    }
  }

  /**
   * Request browser notification permission
   */
  static async requestNotificationPermission(): Promise<'granted' | 'denied' | 'default'> {
    if (!('Notification' in window)) {
      console.error('Browser does not support notifications');
      return 'default';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    const permission = await Notification.requestPermission();
    return permission;
  }

  /**
   * Show browser notification
   */
  static async showBrowserNotification(title: string, options?: NotificationOptions): Promise<void> {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      console.warn('Browser notifications not available or not granted');
      return;
    }

    new Notification(title, options);
  }

  /**
   * Check if browser notifications are supported and enabled
   */
  static areBrowserNotificationsEnabled(): boolean {
    return 'Notification' in window && Notification.permission === 'granted';
  }

  /**
   * Format notification for display
   */
  static formatNotification(notification: NotificationMessage): string {
    const timeDiff = this.getTimeDifference(new Date(notification.timestamp));
    return `${notification.title} - ${timeDiff} ago`;
  }

  /**
   * Calculate time difference for display
   */
  private static getTimeDifference(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (diffDays > 0) {
      return `${diffDays}d`;
    } else if (diffHours > 0) {
      return `${diffHours}h`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes}m`;
    } else {
      return 'Just now';
    }
  }
}