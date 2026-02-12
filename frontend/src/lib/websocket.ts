"""WebSocket client for real-time task synchronization."""

import { io, Socket } from 'socket.io-client';

export interface WebSocketConfig {
  url: string;
  userId: string;
  deviceId: string;
  autoConnect?: boolean;
}

export interface TaskUpdateEvent {
  type: string;
  data: {
    event_type: string;
    task_id: string;
    user_id: string;
    changes?: Record<string, any>;
    task_data?: Record<string, any>;
    version?: number;
    source_device_id?: string;
  };
}

export type TaskUpdateHandler = (event: TaskUpdateEvent) => void;

export class WebSocketClient {
  private socket: Socket | null = null;
  private config: WebSocketConfig;
  private handlers: Set<TaskUpdateHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(config: WebSocketConfig) {
    this.config = config;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket server:', this.config.url);

    this.socket = io(this.config.url, {
      auth: {
        user_id: this.config.userId,
        device_id: this.config.deviceId,
      },
      autoConnect: this.config.autoConnect ?? true,
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.setupEventHandlers();
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      console.log('Disconnecting from WebSocket server');
      this.socket.disconnect();
      this.socket = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  /**
   * Subscribe to task updates
   */
  onTaskUpdate(handler: TaskUpdateHandler): () => void {
    this.handlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.delete(handler);
    };
  }

  /**
   * Send ping to server
   */
  ping(): void {
    if (this.socket?.connected) {
      this.socket.emit('ping');
    }
  }

  /**
   * Setup Socket.IO event handlers
   */
  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connected', (data) => {
      console.log('Connection confirmed:', data);
    });

    this.socket.on('pong', () => {
      console.log('Pong received');
    });

    this.socket.on('task_update', (event: TaskUpdateEvent) => {
      console.log('Task update received:', event);
      this.notifyHandlers(event);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
      }
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  /**
   * Notify all registered handlers of a task update
   */
  private notifyHandlers(event: TaskUpdateEvent): void {
    this.handlers.forEach((handler) => {
      try {
        handler(event);
      } catch (error) {
        console.error('Error in task update handler:', error);
      }
    });
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null;

/**
 * Get or create WebSocket client instance
 */
export function getWebSocketClient(config?: WebSocketConfig): WebSocketClient {
  if (!wsClient && config) {
    wsClient = new WebSocketClient(config);
  }

  if (!wsClient) {
    throw new Error('WebSocket client not initialized. Provide config on first call.');
  }

  return wsClient;
}

/**
 * Initialize WebSocket client
 */
export function initWebSocket(config: WebSocketConfig): WebSocketClient {
  wsClient = new WebSocketClient(config);
  return wsClient;
}

/**
 * Cleanup WebSocket client
 */
export function cleanupWebSocket(): void {
  if (wsClient) {
    wsClient.disconnect();
    wsClient = null;
  }
}
