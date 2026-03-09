import { create } from 'zustand';
import type { Call, WSMessage } from '../types/call';

interface CallState {
  // Current active call
  activeCall: Call | null;
  setActiveCall: (call: Call | null) => void;

  // Call history
  callHistory: Call[];
  setCallHistory: (calls: Call[]) => void;
  addCallToHistory: (call: Call) => void;
  updateCallInHistory: (callSid: string, updates: Partial<Call>) => void;

  // WebSocket connection status
  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;

  // Incoming call notification
  incomingCall: Call | null;
  setIncomingCall: (call: Call | null) => void;

  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  error: string | null;
  setError: (error: string | null) => void;

  // Notifications
  notifications: WSMessage[];
  addNotification: (notification: WSMessage) => void;
  clearNotifications: () => void;
}

export const useCallStore = create<CallState>((set, get) => ({
  // Active call
  activeCall: null,
  setActiveCall: (call) => set({ activeCall: call }),

  // Call history
  callHistory: [],
  setCallHistory: (calls) => set({ callHistory: calls }),

  addCallToHistory: (call) => set((state) => ({
    callHistory: [call, ...state.callHistory]
  })),

  updateCallInHistory: (callSid, updates) => set((state) => ({
    callHistory: state.callHistory.map((call) =>
      call.call_sid === callSid ? { ...call, ...updates } : call
    )
  })),

  // WebSocket status
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),

  // Incoming call
  incomingCall: null,
  setIncomingCall: (call) => set({ incomingCall: call }),

  // UI state
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  error: null,
  setError: (error) => set({ error }),

  // Notifications
  notifications: [],

  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, notification]
  })),

  clearNotifications: () => set({ notifications: [] }),
}));
