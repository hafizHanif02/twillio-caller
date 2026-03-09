export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:7000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:7000/ws';

export const CALL_STATUS_LABELS: Record<string, string> = {
  queued: 'Queued',
  ringing: 'Ringing',
  'in-progress': 'In Progress',
  completed: 'Completed',
  busy: 'Busy',
  failed: 'Failed',
  'no-answer': 'No Answer',
};

export const CALL_STATUS_COLORS: Record<string, string> = {
  queued: '#FFA500',
  ringing: '#4169E1',
  'in-progress': '#32CD32',
  completed: '#808080',
  busy: '#FF6347',
  failed: '#DC143C',
  'no-answer': '#FFD700',
};
