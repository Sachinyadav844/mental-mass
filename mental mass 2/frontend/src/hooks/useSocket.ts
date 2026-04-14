import { useEffect, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";

const SOCKET_URL = "http://localhost:5000";

interface SocketEvents {
  dashboard_update: (data: any) => void;
  session_created: (data: any) => void;
  emotion_detected: (data: any) => void;
  [key: string]: (data: any) => void;
}

/**
 * Custom hook for Socket.IO connection
 * Manages socket lifecycle and event subscriptions
 */
export const useSocket = () => {
  const socketRef = useRef<Socket | null>(null);
  const eventHandlersRef = useRef<Partial<SocketEvents>>({});

  // Initialize socket connection
  const connect = useCallback(() => {
    if (!socketRef.current) {
      console.log("[Socket] Connecting to backend at", SOCKET_URL);
      socketRef.current = io(SOCKET_URL, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        transports: ["websocket", "polling"],
      });

      // Connection event handlers
      socketRef.current.on("connect", () => {
        console.log("[Socket] Connected successfully");
      });

      socketRef.current.on("disconnect", () => {
        console.log("[Socket] Disconnected from server");
      });

      socketRef.current.on("error", (error: any) => {
        console.error("[Socket] Connection error:", error);
      });

      socketRef.current.on("connect_error", (error: any) => {
        console.error("[Socket] Connect error:", error);
      });
    }
  }, []);

  // Subscribe to an event
  const on = useCallback(
    (event: string, handler: (data: any) => void) => {
      if (!socketRef.current) {
        connect();
      }

      eventHandlersRef.current[event] = handler;

      if (socketRef.current) {
        socketRef.current.on(event, handler);
        console.log(`[Socket] Subscribed to event: ${event}`);
      }
    },
    [connect]
  );

  // Unsubscribe from an event
  const off = useCallback((event: string) => {
    if (socketRef.current && eventHandlersRef.current[event]) {
      socketRef.current.off(event, eventHandlersRef.current[event]);
      delete eventHandlersRef.current[event];
      console.log(`[Socket] Unsubscribed from event: ${event}`);
    }
  }, []);

  // Emit an event
  const emit = useCallback((event: string, data: any) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit(event, data);
      console.log(`[Socket] Emitted event: ${event}`, data);
    } else {
      console.warn(`[Socket] Cannot emit event ${event}: socket not connected`);
    }
  }, []);

  // Check if connected
  const isConnected = useCallback(() => {
    return socketRef.current?.connected || false;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Don't disconnect on unmount - keep connection alive for other components
      // socketRef.current?.disconnect();
    };
  }, []);

  return {
    socket: socketRef.current,
    connect,
    on,
    off,
    emit,
    isConnected,
  };
};

/**
 * Global Socket.IO manager
 * Singleton pattern to ensure only one connection
 */
let globalSocket: Socket | null = null;

export const initGlobalSocket = () => {
  if (!globalSocket) {
    console.log("[Socket] Initializing global socket connection");
    globalSocket = io(SOCKET_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ["websocket", "polling"],
    });

    globalSocket.on("connect", () => {
      console.log("[Socket] Global socket connected");
    });

    globalSocket.on("disconnect", () => {
      console.log("[Socket] Global socket disconnected");
    });

    globalSocket.on("error", (error: any) => {
      console.error("[Socket] Global socket error:", error);
    });
  }

  return globalSocket;
};

export const useGlobalSocket = () => {
  useEffect(() => {
    initGlobalSocket();
  }, []);

  return globalSocket;
};
