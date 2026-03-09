import { useEffect, useState } from 'react';
import { useCalls } from '../hooks/useCalls';
import { useCallStore } from '../store/callStore';
import { CALL_STATUS_LABELS, CALL_STATUS_COLORS } from '../utils/constants';

export function CallHistory() {
  const { fetchCallHistory } = useCalls();
  const { callHistory, isLoading } = useCallStore();
  const [filter, setFilter] = useState<{
    direction?: 'inbound' | 'outbound';
    status?: string;
  }>({});

  useEffect(() => {
    fetchCallHistory(1, 50, filter.direction, filter.status);
  }, [filter, fetchCallHistory]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getStatusColor = (status: string): string => {
    return CALL_STATUS_COLORS[status] || '#808080';
  };

  const getStatusLabel = (status: string): string => {
    return CALL_STATUS_LABELS[status] || status;
  };

  if (isLoading) {
    return <div className="loading">Loading call history...</div>;
  }

  return (
    <div className="call-history-container">
      {/* Filters */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>
            Direction
          </label>
          <select
            value={filter.direction || ''}
            onChange={(e) => setFilter({ ...filter, direction: e.target.value as any || undefined })}
            style={{
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ddd',
              fontSize: '0.875rem'
            }}
          >
            <option value="">All</option>
            <option value="inbound">Inbound</option>
            <option value="outbound">Outbound</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 500 }}>
            Status
          </label>
          <select
            value={filter.status || ''}
            onChange={(e) => setFilter({ ...filter, status: e.target.value || undefined })}
            style={{
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ddd',
              fontSize: '0.875rem'
            }}
          >
            <option value="">All</option>
            <option value="completed">Completed</option>
            <option value="in-progress">In Progress</option>
            <option value="ringing">Ringing</option>
            <option value="busy">Busy</option>
            <option value="failed">Failed</option>
            <option value="no-answer">No Answer</option>
          </select>
        </div>
      </div>

      {/* Call history table */}
      {callHistory.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No calls found. Make your first call to get started!
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Direction</th>
                <th>From</th>
                <th>To</th>
                <th>Status</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {callHistory.map((call) => (
                <tr key={call.call_sid}>
                  <td style={{ fontSize: '0.875rem' }}>
                    {formatDate(call.created_at)}
                  </td>
                  <td>
                    <span style={{
                      textTransform: 'capitalize',
                      fontSize: '0.875rem'
                    }}>
                      {call.direction}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                    {call.from_number}
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                    {call.to_number}
                  </td>
                  <td>
                    <span
                      className="status-badge"
                      style={{
                        backgroundColor: getStatusColor(call.status),
                        color: 'white'
                      }}
                    >
                      {getStatusLabel(call.status)}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.875rem' }}>
                    {formatDuration(call.duration)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
