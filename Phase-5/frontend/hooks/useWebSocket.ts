import { useState, useEffect, useRef, useCallback } from 'react';
import { NotificationMessage } from '@/types/taskTypes';

interface WebSocketHookReturn {
  isConnected: boolean;
  sendMessage: (message: any) => void;
  notifications: NotificationMessage[];
  clearNotifications: () => void;
  error: string | null;
}

export const useWebSocket = (url: string): WebSocketHookReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = 5000; // 5 seconds

  // Function to establish WebSocket connection
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          // Handle different message types
          switch (message.type) {
            case 'notification':
              // Add notification to the list
              const newNotification: NotificationMessage = {
                id: message.data.id || `notif_${Date.now()}`,
                type: message.data.type || 'system',
                title: message.data.title || 'Notification',
                message: message.data.message || '',
                task_id: message.data.task_id,
                priority: message.data.priority || 'medium',
                timestamp: message.data.timestamp || new Date().toISOString(),
              };

              setNotifications(prev => [newNotification, ...prev.slice(0, 9)]); // Keep only last 10 notifications
              break;

            case 'ping':
              // Respond to ping with pong to keep connection alive
              if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: 'pong' }));
              }
              break;

            default:
              // For other message types, just log them
              console.log('Received message:', message);
              break;
          }
        } catch (parseError) {
          console.error('❌ Error parsing WebSocket message:', parseError);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setError('WebSocket connection error occurred');
      };

      ws.onclose = (event) => {
        console.log('⚠️ WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);

        // Attempt to reconnect if it wasn't a deliberate close
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`🔄 Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);

          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError(`Maximum reconnection attempts (${maxReconnectAttempts}) reached`);
        }
      };

      wsRef.current = ws;
    } catch (connectionError) {
      console.error('❌ Failed to create WebSocket connection:', connectionError);
      setError('Failed to establish WebSocket connection');
    }
  }, [url]);

  // Function to send messages
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message));
      } catch (sendError) {
        console.error('❌ Error sending message:', sendError);
        setError('Failed to send message');
      }
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message:', message);
      setError('WebSocket not connected');
    }
  }, []);

  // Function to clear notifications
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Establish connection on mount
  useEffect(() => {
    connect();

    return () => {
      // Cleanup on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Manual disconnect');
      }
    };
  }, [connect]); // Only reconnect when URL changes

  return {
    isConnected,
    sendMessage,
    notifications,
    clearNotifications,
    error,
  };
};