import { useState, useEffect, useCallback } from 'react';
import { twilioDevice, DeviceStatus, CallInfo } from '../services/twilioDevice';

export function useTwilioDevice() {
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus>('notReady');
  const [currentCall, setCurrentCall] = useState<CallInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);

  // Initialize device on mount
  useEffect(() => {
    const initDevice = async () => {
      try {
        setIsInitializing(true);
        await twilioDevice.initialize();
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to initialize device';
        setError(errorMessage);
        console.error('Device initialization error:', err);
      } finally {
        setIsInitializing(false);
      }
    };

    initDevice();

    // Subscribe to device status changes
    const unsubscribeStatus = twilioDevice.onStatusChange((status) => {
      setDeviceStatus(status);
    });

    // Subscribe to call changes
    const unsubscribeCall = twilioDevice.onCallChange((callInfo) => {
      setCurrentCall(callInfo);
    });

    // Subscribe to errors
    const unsubscribeError = twilioDevice.onError((errorMsg) => {
      setError(errorMsg);
    });

    // Cleanup on unmount
    return () => {
      unsubscribeStatus();
      unsubscribeCall();
      unsubscribeError();
      twilioDevice.destroy();
    };
  }, []);

  /**
   * Make a call to a phone number
   */
  const makeCall = useCallback(async (phoneNumber: string) => {
    try {
      setError(null);
      await twilioDevice.makeCall(phoneNumber);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to make call';
      setError(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Hang up the active call
   */
  const hangup = useCallback(() => {
    twilioDevice.hangup();
    setIsMuted(false);
  }, []);

  /**
   * Toggle mute on/off
   */
  const toggleMute = useCallback(() => {
    const newMuteState = !isMuted;
    twilioDevice.mute(newMuteState);
    setIsMuted(newMuteState);
  }, [isMuted]);

  /**
   * Retry initialization if device failed
   */
  const retryInitialization = useCallback(async () => {
    try {
      setIsInitializing(true);
      setError(null);
      await twilioDevice.initialize();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize device';
      setError(errorMessage);
    } finally {
      setIsInitializing(false);
    }
  }, []);

  return {
    // State
    deviceStatus,
    currentCall,
    error,
    isMuted,
    isInitializing,

    // Computed state
    isReady: deviceStatus === 'ready',
    isOnCall: deviceStatus === 'onCall',
    isCalling: deviceStatus === 'calling',
    hasActiveCall: currentCall !== null,

    // Actions
    makeCall,
    hangup,
    toggleMute,
    retryInitialization,
  };
}
