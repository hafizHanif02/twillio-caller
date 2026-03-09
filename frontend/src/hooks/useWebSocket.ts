import { useEffect } from 'react';
import { wsService } from '../services/websocket';
import { useCallStore } from '../store/callStore';
import type { WSMessage } from '../types/call';

export function useWebSocket() {
  const {
    setWsConnected,
    setActiveCall,
    updateCallInHistory,
    addCallToHistory,
    setIncomingCall,
    addNotification,
  } = useCallStore();

  useEffect(() => {
    // Connect to WebSocket
    wsService.connect();

    // Handle connection
    const unsubscribeConnect = wsService.onConnect(() => {
      console.log('WebSocket connected in hook');
      setWsConnected(true);
    });

    // Handle disconnection
    const unsubscribeDisconnect = wsService.onDisconnect(() => {
      console.log('WebSocket disconnected in hook');
      setWsConnected(false);
    });

    // Handle messages
    const unsubscribeMessage = wsService.onMessage((message: WSMessage) => {
      console.log('Received WebSocket message:', message);

      // Add to notifications
      addNotification(message);

      // Handle different message types
      switch (message.type) {
        case 'connection.established':
          console.log('Connection established:', message.data.message);
          break;

        case 'call.initiated':
        case 'call.ringing':
        case 'call.answered':
        case 'call.in_progress':
          // Update active call status
          if (message.data.callSid) {
            updateCallInHistory(message.data.callSid, {
              status: message.data.status || message.type.split('.')[1],
            });
          }
          break;

        case 'call.completed':
        case 'call.busy':
        case 'call.failed':
        case 'call.no_answer':
          // Call ended - clear active call if it matches
          if (message.data.callSid) {
            updateCallInHistory(message.data.callSid, {
              status: message.data.status || message.type.split('.')[1],
              duration: message.data.duration,
            });
            setActiveCall(null);
          }
          break;

        case 'incoming.call':
          // Show incoming call notification
          if (message.data.callSid && message.data.from && message.data.to) {
            const incomingCallData = {
              call_sid: message.data.callSid,
              direction: 'inbound' as const,
              from_number: message.data.from,
              to_number: message.data.to,
              status: message.data.status || 'ringing',
              created_at: message.timestamp,
              updated_at: message.timestamp,
            };
            setIncomingCall(incomingCallData);
            addCallToHistory(incomingCallData);
          }
          break;

        case 'pong':
          // Heartbeat response
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    });

    // Cleanup on unmount
    return () => {
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeMessage();
      wsService.disconnect();
    };
  }, []);

  return {
    isConnected: wsService.isConnected(),
    send: (message: any) => wsService.send(message),
  };
}
