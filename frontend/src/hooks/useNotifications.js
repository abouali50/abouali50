import { useEffect, useRef } from 'react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const WS_URL = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');

export const useNotifications = (memberId, isAuthenticated) => {
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = () => {
    if (!memberId || !isAuthenticated) return;

    try {
      const wsUrl = `${WS_URL}/api/ws/notifications?member_id=${memberId}`;
      console.log('🔌 Connecting to WebSocket:', wsUrl);
      
      ws.current = new WebSocket(wsUrl);
      
      ws.current.onopen = () => {
        console.log('✅ WebSocket connected');
        reconnectAttempts.current = 0;
        
        // Send keepalive every 30 seconds
        const keepAlive = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send('ping');
          } else {
            clearInterval(keepAlive);
          }
        }, 30000);
        
        ws.current.keepAliveInterval = keepAlive;
      };
      
      ws.current.onmessage = (event) => {
        try {
          const notification = JSON.parse(event.data);
          console.log('📬 Received notification:', notification);
          
          handleNotification(notification);
        } catch (error) {
          console.error('❌ Error parsing notification:', error);
        }
      };
      
      ws.current.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
        
        if (ws.current?.keepAliveInterval) {
          clearInterval(ws.current.keepAliveInterval);
        }
        
        // Attempt to reconnect if not closed intentionally
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1})`);
          
          setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        }
      };
      
      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('❌ Error creating WebSocket:', error);
    }
  };

  const handleNotification = (notification) => {
    const { type, title, message, data } = notification;
    
    switch (type) {
      case 'LEVEL_UP':
        toast.success(title, {
          description: message,
          duration: 6000,
          action: {
            label: 'Voir mes niveaux',
            onClick: () => {
              // Could navigate to profile or show level details
              console.log('Navigate to levels');
            }
          }
        });
        break;
        
      case 'BADGE_AWARDED':
        toast.success(title, {
          description: message,
          duration: 6000,
          action: {
            label: 'Voir mes badges',
            onClick: () => {
              // Could navigate to badges section
              console.log('Navigate to badges');
            }
          }
        });
        break;
        
      case 'REDEMPTION_APPROVED':
        toast.success(title, {
          description: message,
          duration: 5000,
        });
        break;
        
      case 'REDEMPTION_DELIVERED':
        toast.success(title, {
          description: message,
          duration: 5000,
        });
        break;
        
      default:
        toast.info(title, {
          description: message,
          duration: 4000,
        });
    }
  };

  const disconnect = () => {
    if (ws.current) {
      console.log('🔌 Disconnecting WebSocket');
      
      if (ws.current.keepAliveInterval) {
        clearInterval(ws.current.keepAliveInterval);
      }
      
      ws.current.close(1000, 'User disconnected');
      ws.current = null;
    }
  };

  useEffect(() => {
    if (memberId && isAuthenticated) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [memberId, isAuthenticated]);

  return {
    isConnected: ws.current?.readyState === WebSocket.OPEN,
    disconnect
  };
};