import { Device, Call as TwilioCall } from '@twilio/voice-sdk';
import { apiService } from './api';

export type DeviceStatus = 'notReady' | 'ready' | 'calling' | 'onCall' | 'offline' | 'error';

export interface CallInfo {
  callSid: string;
  to: string;
  status: string;
  startTime?: Date;
}

class TwilioDeviceService {
  private device: Device | null = null;
  private activeCall: TwilioCall | null = null;
  private deviceStatus: DeviceStatus = 'notReady';
  private statusListeners: ((status: DeviceStatus) => void)[] = [];
  private callListeners: ((callInfo: CallInfo | null) => void)[] = [];
  private errorListeners: ((error: string) => void)[] = [];

  /**
   * Initialize the Twilio Device with an access token
   */
  async initialize(): Promise<void> {
    try {
      console.log('Initializing Twilio Device...');

      // Get access token from backend
      const tokenResponse = await apiService.getAccessToken();
      console.log('Access token received:', tokenResponse.identity);

      // Create new Device instance
      this.device = new Device(tokenResponse.token, {
        logLevel: 'debug',
      });

      // Set up event listeners
      this.setupDeviceListeners();

      // Register the device
      await this.device.register();

      console.log('Twilio Device initialized and registered');
      this.updateStatus('ready');
    } catch (error) {
      console.error('Failed to initialize Twilio Device:', error);
      this.updateStatus('error');
      this.notifyError(error instanceof Error ? error.message : 'Failed to initialize device');
      throw error;
    }
  }

  /**
   * Make an outbound call to a phone number
   */
  async makeCall(phoneNumber: string): Promise<void> {
    if (!this.device) {
      throw new Error('Device not initialized. Call initialize() first.');
    }

    if (this.activeCall) {
      throw new Error('A call is already in progress');
    }

    try {
      console.log('Making call to:', phoneNumber);
      this.updateStatus('calling');

      // Connect to the phone number
      // The "To" parameter will be passed to the backend TwiML webhook
      this.activeCall = await this.device.connect({
        params: {
          To: phoneNumber
        }
      });

      // Set up call event listeners
      this.setupCallListeners(this.activeCall);

      const callInfo: CallInfo = {
        callSid: this.activeCall.parameters.CallSid || '',
        to: phoneNumber,
        status: 'connecting',
        startTime: new Date()
      };

      this.notifyCallListeners(callInfo);
    } catch (error) {
      console.error('Failed to make call:', error);
      this.updateStatus('ready');
      this.activeCall = null;
      this.notifyError(error instanceof Error ? error.message : 'Failed to make call');
      throw error;
    }
  }

  /**
   * Hang up the active call
   */
  hangup(): void {
    if (this.activeCall) {
      console.log('Hanging up call');
      this.activeCall.disconnect();
    }
  }

  /**
   * Mute/unmute the microphone
   */
  mute(shouldMute: boolean): void {
    if (this.activeCall) {
      this.activeCall.mute(shouldMute);
      console.log('Microphone', shouldMute ? 'muted' : 'unmuted');
    }
  }

  /**
   * Get current device status
   */
  getStatus(): DeviceStatus {
    return this.deviceStatus;
  }

  /**
   * Check if device is ready to make calls
   */
  isReady(): boolean {
    return this.deviceStatus === 'ready';
  }

  /**
   * Check if there's an active call
   */
  hasActiveCall(): boolean {
    return this.activeCall !== null;
  }

  /**
   * Destroy the device and clean up
   */
  destroy(): void {
    if (this.device) {
      this.device.destroy();
      this.device = null;
    }
    this.activeCall = null;
    this.updateStatus('offline');
  }

  /**
   * Subscribe to device status changes
   */
  onStatusChange(listener: (status: DeviceStatus) => void): () => void {
    this.statusListeners.push(listener);
    // Return unsubscribe function
    return () => {
      this.statusListeners = this.statusListeners.filter(l => l !== listener);
    };
  }

  /**
   * Subscribe to call info updates
   */
  onCallChange(listener: (callInfo: CallInfo | null) => void): () => void {
    this.callListeners.push(listener);
    return () => {
      this.callListeners = this.callListeners.filter(l => l !== listener);
    };
  }

  /**
   * Subscribe to error events
   */
  onError(listener: (error: string) => void): () => void {
    this.errorListeners.push(listener);
    return () => {
      this.errorListeners = this.errorListeners.filter(l => l !== listener);
    };
  }

  /**
   * Set up Device event listeners
   */
  private setupDeviceListeners(): void {
    if (!this.device) return;

    this.device.on('registered', () => {
      console.log('Device registered');
      this.updateStatus('ready');
    });

    this.device.on('unregistered', () => {
      console.log('Device unregistered');
      this.updateStatus('offline');
    });

    this.device.on('error', (error) => {
      console.error('Device error:', error);
      this.updateStatus('error');
      this.notifyError(error.message);
    });

    this.device.on('incoming', (call: TwilioCall) => {
      console.log('Incoming call received:', call.parameters.From);
      // Handle incoming calls if needed
    });
  }

  /**
   * Set up Call event listeners
   */
  private setupCallListeners(call: TwilioCall): void {
    call.on('accept', () => {
      console.log('Call accepted');
      this.updateStatus('onCall');
      this.notifyCallListeners({
        callSid: call.parameters.CallSid || '',
        to: call.parameters.To || '',
        status: 'in-progress',
        startTime: new Date()
      });
    });

    call.on('disconnect', () => {
      console.log('Call disconnected');
      this.activeCall = null;
      this.updateStatus('ready');
      this.notifyCallListeners(null);
    });

    call.on('cancel', () => {
      console.log('Call cancelled');
      this.activeCall = null;
      this.updateStatus('ready');
      this.notifyCallListeners(null);
    });

    call.on('reject', () => {
      console.log('Call rejected');
      this.activeCall = null;
      this.updateStatus('ready');
      this.notifyCallListeners(null);
    });

    call.on('error', (error) => {
      console.error('Call error:', error);
      this.activeCall = null;
      this.updateStatus('ready');
      this.notifyError(error.message);
      this.notifyCallListeners(null);
    });
  }

  /**
   * Update device status and notify listeners
   */
  private updateStatus(status: DeviceStatus): void {
    this.deviceStatus = status;
    this.statusListeners.forEach(listener => listener(status));
  }

  /**
   * Notify call listeners
   */
  private notifyCallListeners(callInfo: CallInfo | null): void {
    this.callListeners.forEach(listener => listener(callInfo));
  }

  /**
   * Notify error listeners
   */
  private notifyError(error: string): void {
    this.errorListeners.forEach(listener => listener(error));
  }
}

// Export singleton instance
export const twilioDevice = new TwilioDeviceService();
