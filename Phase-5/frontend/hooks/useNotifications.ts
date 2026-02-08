import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { NotificationMessage } from '@/types/taskTypes';

interface UseNotificationsReturn {
  notifications: NotificationMessage[];
  addNotification: (notification: NotificationMessage) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  markAsRead: (id: string) => void;
  unreadCount: number;
  isConnected: boolean;
  error: string | null;
}

export const useNotifications = (userId: string): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Using the existing useWebSocket hook to handle real-time notifications
  const wsUrl = process.env.NEXT_PUBLIC_TODO_WEBSOCKET_URL || `ws://localhost:8000/ws/notifications/${userId}`;
  const { isConnected, sendMessage, notifications: wsNotifications, clearNotifications: clearWsNotifications, error } = useWebSocket(wsUrl);

  // When a notification is received via WebSocket, add it to the list
  useEffect(() => {
    setNotifications(wsNotifications);
  }, [wsNotifications]);

  const addNotification = useCallback((notification: NotificationMessage) => {
    setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep max 50 notifications
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
    clearWsNotifications(); // Also clear notifications from WebSocket service
  }, [clearWsNotifications]);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } as NotificationMessage : notif
      )
    );
  }, []);

  // Update unread count when notifications change
  useEffect(() => {
    const count = notifications.filter(notif => !(notif as any).read).length;
    setUnreadCount(count);
  }, [notifications]);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications: clearAllNotifications,
    markAsRead,
    unreadCount,
    isConnected,
    error,
  };
};