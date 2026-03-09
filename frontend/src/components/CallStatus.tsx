import { useEffect, useState } from 'react';
import type { Call } from '../types/call';
import { CALL_STATUS_LABELS, CALL_STATUS_COLORS } from '../utils/constants';

interface CallStatusProps {
  call: Call;
}

export function CallStatus({ call }: CallStatusProps) {
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    // Start timer if call is in progress
    if (call.status === 'in-progress' || call.status === 'ringing') {
      const interval = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [call.status]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string): string => {
    return CALL_STATUS_COLORS[status] || '#808080';
  };

  const getStatusLabel = (status: string): string => {
    return CALL_STATUS_LABELS[status] || status;
  };

  return (
    <div className="call-status-container">
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.125rem' }}>
            {call.direction === 'outbound' ? 'Outbound Call' : 'Inbound Call'}
          </h3>
          <p style={{ margin: '0.25rem 0', color: '#666' }}>
            {call.direction === 'outbound' ? `Calling ${call.to_number}` : `From ${call.from_number}`}
          </p>
        </div>

        <div>
          <span
            className="status-badge"
            style={{
              backgroundColor: getStatusColor(call.status),
              color: 'white'
            }}
          >
            {getStatusLabel(call.status)}
          </span>
        </div>
      </div>

      {(call.status === 'in-progress' || call.status === 'ringing') && (
        <div style={{
          textAlign: 'center',
          padding: '1.5rem',
          background: '#f5f5f5',
          borderRadius: '8px'
        }}>
          <div style={{
            fontSize: '2.5rem',
            fontWeight: 'bold',
            color: '#1976d2',
            fontFamily: 'monospace'
          }}>
            {formatDuration(duration)}
          </div>
          <div style={{ marginTop: '0.5rem', color: '#666' }}>
            {call.status === 'ringing' ? 'Ringing...' : 'Call in progress'}
          </div>
        </div>
      )}

      <div style={{
        marginTop: '1rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '0.5rem',
        fontSize: '0.875rem'
      }}>
        <div>
          <strong>Call SID:</strong>
          <div style={{ color: '#666', wordBreak: 'break-all', fontFamily: 'monospace', fontSize: '0.75rem' }}>
            {call.call_sid}
          </div>
        </div>

        <div>
          <strong>From:</strong>
          <div style={{ color: '#666' }}>{call.from_number}</div>
        </div>

        <div>
          <strong>To:</strong>
          <div style={{ color: '#666' }}>{call.to_number}</div>
        </div>

        {call.duration && (
          <div>
            <strong>Duration:</strong>
            <div style={{ color: '#666' }}>{call.duration}s</div>
          </div>
        )}
      </div>
    </div>
  );
}
