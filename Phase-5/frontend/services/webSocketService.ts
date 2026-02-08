import { EventEmitter } from 'events';

// Define types for WebSocket events
export interface WebSocketEvent {
  type: string;
  data: any;
  timestamp: Date;
}

export interface NotificationMessage {
  id: string;
  type: 'reminder' | 'task_update' | 'system' | 'recurring_task';
  title: string;
  message: string;
  task_id?: number;
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
}

export interface TaskUpdateMessage {
  id: number;
  action: 'created' | 'updated' | 'deleted' | 'completed';
  task: any; // Should match Task interface from taskService
  timestamp: string;
}

export interface WebSocketServiceConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private eventEmitter = new EventEmitter();
  private config: WebSocketServiceConfig;
  private reconnectAttempts = 0;
  private isConnected = false;
  private queuedMessages: any[] = [];

  constructor(config: WebSocketServiceConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      ...config
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.eventEmitter.emit('connect');

          // Send any queued messages
          this.flushQueuedMessages();

          // Start heartbeat
          this.startHeartbeat();

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            // Emit the message based on its type
            switch (message.type) {
              case 'notification':
                this.eventEmitter.emit('notification', message.data as NotificationMessage);
                break;
              case 'task_update':
                this.eventEmitter.emit('task_update', message.data as TaskUpdateMessage);
                break;
              case 'ping':
                this.send({ type: 'pong' });
                break;
              default:
                this.eventEmitter.emit('message', message);
                break;
            }
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
            this.eventEmitter.emit('error', { message: 'Failed to parse message', error });
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.eventEmitter.emit('error', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('⚠️ WebSocket disconnected');
          this.isConnected = false;
          this.eventEmitter.emit('disconnect');

          // Attempt to reconnect if within limits
          if (this.reconnectAttempts < this.config.maxReconnectAttempts!) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})...`);

            setTimeout(() => {
              this.connect().catch(console.error);
            }, this.config.reconnectInterval);
          } else {
            console.warn('❌ Maximum reconnection attempts reached');
            this.eventEmitter.emit('reconnect_failed');
          }
        };
      } catch (error) {
        console.error('❌ Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  /**
   * Send a message through the WebSocket
   */
  send(message: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      // Queue the message if not connected
      this.queuedMessages.push(message);
      console.warn('⚠️ WebSocket not connected, queuing message');
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('❌ Error sending message:', error);
      // Add to queue in case of error
      this.queuedMessages.push(message);
    }
  }

  /**
   * Flush queued messages when connection is established
   */
  private flushQueuedMessages(): void {
    while (this.queuedMessages.length > 0) {
      const message = this.queuedMessages.shift();
      this.send(message);
    }
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    setInterval(() => {
      if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, this.config.heartbeatInterval!);
  }

  /**
   * Subscribe to notification events
   */
  onNotification(callback: (notification: NotificationMessage) => void): void {
    this.eventEmitter.on('notification', callback);
  }

  /**
   * Unsubscribe from notification events
   */
  offNotification(callback: (notification: NotificationMessage) => void): void {
    this.eventEmitter.off('notification', callback);
  }

  /**
   * Subscribe to task update events
   */
  onTaskUpdate(callback: (update: TaskUpdateMessage) => void): void {
    this.eventEmitter.on('task_update', callback);
  }

  /**
   * Unsubscribe from task update events
   */
  offTaskUpdate(callback: (update: TaskUpdateMessage) => void): void {
    this.eventEmitter.off('task_update', callback);
  }

  /**
   * Subscribe to general messages
   */
  onMessage(callback: (message: any) => void): void {
    this.eventEmitter.on('message', callback);
  }

  /**
   * Unsubscribe from general messages
   */
  offMessage(callback: (message: any) => void): void {
    this.eventEmitter.off('message', callback);
  }

  /**
   * Subscribe to connection events
   */
  onConnect(callback: () => void): void {
    this.eventEmitter.on('connect', callback);
  }

  /**
   * Subscribe to disconnection events
   */
  onDisconnect(callback: () => void): void {
    this.eventEmitter.on('disconnect', callback);
  }

  /**
   * Subscribe to error events
   */
  onError(callback: (error: any) => void): void {
    this.eventEmitter.on('error', callback);
  }

  /**
   * Check if the connection is established
   */
  isConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Get current connection status
   */
  getStatus(): 'connecting' | 'connected' | 'disconnected' {
    if (!this.ws) return 'disconnected';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      default:
        return 'disconnected';
    }
  }
}

// Singleton instance
let webSocketService: WebSocketService | null = null;

export const getWebSocketService = (config?: WebSocketServiceConfig): WebSocketService => {
  if (!webSocketService && config) {
    webSocketService = new WebSocketService(config);
  } else if (!webSocketService) {
    throw new Error('WebSocketService not initialized. Call with config first.');
  }

  return webSocketService;
};

export default WebSocketService;