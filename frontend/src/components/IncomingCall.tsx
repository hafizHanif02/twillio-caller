import { useCallStore } from '../store/callStore';
import type { Call } from '../types/call';

interface IncomingCallProps {
  call: Call;
}

export function IncomingCall({ call }: IncomingCallProps) {
  const { setIncomingCall } = useCallStore();

  const handleDismiss = () => {
    setIncomingCall(null);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '2rem',
        maxWidth: '400px',
        width: '90%',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: '#4caf50',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem',
            animation: 'pulse 1.5s ease-in-out infinite'
          }}>
            <svg
              width="40"
              height="40"
              fill="white"
              viewBox="0 0 24 24"
            >
              <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
            </svg>
          </div>

          <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem' }}>
            Incoming Call
          </h2>

          <p style={{ fontSize: '1.25rem', fontWeight: 500, margin: '0', color: '#333' }}>
            {call.from_number}
          </p>

          <p style={{ fontSize: '0.875rem', color: '#666', margin: '0.5rem 0 0' }}>
            Calling {call.to_number}
          </p>
        </div>

        <div style={{
          display: 'flex',
          gap: '1rem',
          marginTop: '1.5rem'
        }}>
          <button
            className="secondary-button"
            onClick={handleDismiss}
            style={{ flex: 1 }}
          >
            Dismiss
          </button>
        </div>

        <p style={{
          fontSize: '0.75rem',
          color: '#999',
          textAlign: 'center',
          marginTop: '1rem',
          marginBottom: 0
        }}>
          Call will be handled by Twilio
        </p>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.05);
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
}
