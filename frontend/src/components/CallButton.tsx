import { useState } from 'react';
import { useTwilioDevice } from '../hooks/useTwilioDevice';

export function CallButton() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const {
    isReady,
    isOnCall,
    isCalling,
    error: deviceError,
    isMuted,
    currentCall,
    makeCall,
    hangup,
    toggleMute,
    isInitializing,
  } = useTwilioDevice();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!phoneNumber.trim()) {
      return;
    }

    try {
      await makeCall(phoneNumber);
    } catch (error) {
      console.error('Failed to make call:', error);
    }
  };

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digit characters except +
    const cleaned = value.replace(/[^\d+]/g, '');
    setPhoneNumber(cleaned);
  };

  const handleHangup = () => {
    hangup();
    // Don't clear the phone number so user can redial
  };

  // Show device status
  const getDeviceStatusText = () => {
    if (isInitializing) return 'Initializing...';
    if (!isReady && !isOnCall && !isCalling) return 'Device not ready';
    if (isCalling) return 'Connecting...';
    if (isOnCall) return 'On call';
    return 'Ready to call';
  };

  return (
    <div className="call-button-container">
      <div style={{ marginBottom: '1rem' }}>
        <div style={{
          padding: '0.5rem',
          borderRadius: '4px',
          backgroundColor: isReady ? '#d4edda' : (isOnCall ? '#fff3cd' : '#f8d7da'),
          color: isReady ? '#155724' : (isOnCall ? '#856404' : '#721c24'),
          border: `1px solid ${isReady ? '#c3e6cb' : (isOnCall ? '#ffeeba' : '#f5c6cb')}`,
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isReady ? '#28a745' : (isOnCall ? '#ffc107' : '#dc3545'),
            display: 'inline-block'
          }}></span>
          <span>{getDeviceStatusText()}</span>
        </div>
      </div>

      {!isOnCall && (
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <input
              type="tel"
              placeholder="Enter phone number (e.g., +1234567890)"
              value={phoneNumber}
              onChange={(e) => formatPhoneNumber(e.target.value)}
              disabled={!isReady || isCalling}
              style={{ width: '100%' }}
            />
            <p style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}>
              Enter number in E.164 format (e.g., +12025551234)
            </p>
          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={!phoneNumber.trim() || !isReady || isCalling}
            style={{ minWidth: '120px' }}
          >
            {isCalling ? 'Calling...' : 'Make Call'}
          </button>
        </form>
      )}

      {isOnCall && currentCall && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#e7f3ff',
          borderRadius: '8px',
          border: '1px solid #b3d9ff'
        }}>
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem' }}>Active Call</h3>
            <p style={{ margin: '0', color: '#666' }}>
              Calling: <strong>{currentCall.to}</strong>
            </p>
            {currentCall.startTime && (
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                Started: {currentCall.startTime.toLocaleTimeString()}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={toggleMute}
              className="secondary-button"
              style={{ flex: 1 }}
            >
              {isMuted ? '🔇 Unmute' : '🔊 Mute'}
            </button>
            <button
              onClick={handleHangup}
              style={{
                flex: 1,
                padding: '0.75rem 1.5rem',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              📞 Hang Up
            </button>
          </div>
        </div>
      )}

      {deviceError && (
        <div className="error-message" style={{ marginTop: '1rem' }}>
          {deviceError}
        </div>
      )}

      {!isReady && !isInitializing && !isOnCall && (
        <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#666' }}>
          ⚠️ Make sure you're using HTTPS (ngrok) and have granted microphone permissions
        </div>
      )}
    </div>
  );
}
