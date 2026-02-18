import { Bell, X } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { NotificationMessage } from '@/types/taskTypes';

interface NotificationPanelProps {
  userId: string;
  onClose?: () => void;
  onNotificationClick?: (notification: NotificationMessage) => void;
}

export const NotificationPanel = ({
  userId,
  onClose,
  onNotificationClick
}: NotificationPanelProps) => {
  // Construct WebSocket URL based on API URL
  const getWebSocketUrl = () => {
    const apiUrl = process.env.NEXT_PUBLIC_TODO_API_URL || ' ahmed-raza-backend-phase-5.hf.space';
    
    // Convert HTTP URL to WebSocket URL
    const wsUrl = apiUrl
      .replace('http://', 'ws://')
      .replace('https://', 'wss://');
    
    return `${wsUrl}/ws/notifications/${userId}`;
  };

  const wsUrl = getWebSocketUrl();
  const { isConnected, notifications, clearNotifications, error } = useWebSocket(wsUrl);

  const handleNotificationClick = (notification: NotificationMessage) => {
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 w-80 max-h-96 bg-white shadow-lg rounded-md border border-gray-200">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Bell className="h-5 w-5 text-gray-600" />
          <h3 className="font-medium text-gray-900">Notifications</h3>
          <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2 py-0.5 rounded-full">
            {notifications.length}
          </span>
        </div>
        <div className="flex gap-2">
          {notifications.length > 0 && (
            <button
              onClick={() => clearNotifications()}
              className="text-gray-400 hover:text-gray-600 text-sm"
            >
              Clear All
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      <div className="max-h-80 overflow-y-auto">
        {error && (
          <div className="p-4 text-sm text-red-600 bg-red-50 border-b border-red-200">
            <div className="font-medium mb-1">Connection Error</div>
            <div className="text-xs">{error}</div>
            <div className="text-xs mt-2 text-gray-600">
              Make sure your backend is running at: {wsUrl.replace(`/ws/notifications/${userId}`, '')}
            </div>
          </div>
        )}

        {!isConnected && !error && (
          <div className="p-4 text-sm text-yellow-600 bg-yellow-50 border-b border-yellow-200">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
              Connecting to notification service...
            </div>
          </div>
        )}

        {isConnected && !error && notifications.length === 0 && (
          <div className="p-8 text-center">
            <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-3 flex items-center justify-center">
              <Bell className="h-8 w-8 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500 font-medium">No notifications yet</p>
            <p className="text-xs text-gray-400 mt-1">You'll be notified about important updates</p>
          </div>
        )}

        {isConnected && !error && notifications.length > 0 && (
          <ul className="divide-y divide-gray-200">
            {notifications.map((notification) => (
              <li
                key={notification.id}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition ${
                  notification.priority === 'high' ? 'border-l-4 border-red-500 bg-red-50/50' :
                  notification.priority === 'medium' ? 'border-l-4 border-yellow-500 bg-yellow-50/50' :
                  'border-l-4 border-blue-500 bg-blue-50/50'
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex justify-between items-start gap-2">
                  <h4 className="font-medium text-gray-900 flex-1">{notification.title}</h4>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {new Date(notification.timestamp).toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                </div>
                <p className="mt-1 text-sm text-gray-600">{notification.message}</p>
                <div className="mt-2 flex items-center gap-2">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    notification.priority === 'high' ? 'bg-red-100 text-red-800' :
                    notification.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {notification.priority}
                  </span>
                  {notification.type && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {notification.type}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};