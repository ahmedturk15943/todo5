"""useWebSocket hook for WebSocket connection management."""

import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8001';

export function useWebSocket(userId?: string) {
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!userId) return;

    // Connect to WebSocket server
    const socket = io(WS_URL, {
      auth: {
        user_id: userId
      },
      transports: ['websocket']
    });

    socket.on('connect', () => {
      console.log('WebSocket connected');
      setConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [userId]);

  const subscribe = (event: string, handler: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, handler);
    }
  };

  const unsubscribe = (event: string, handler: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.off(event, handler);
    }
  };

  return {
    connected,
    subscribe,
    unsubscribe
  };
}
