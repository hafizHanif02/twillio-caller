export interface Call {
  call_sid: string;
  direction: 'inbound' | 'outbound';
  from_number: string;
  to_number: string;
  status: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  recording_url?: string;
  price?: number;
  price_unit?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CallHistoryResponse {
  calls: Call[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface OutboundCallRequest {
  to_number: string;
}

export interface WSMessage {
  type: string;
  timestamp: string;
  data: {
    callSid?: string;
    status?: string;
    direction?: 'inbound' | 'outbound';
    from?: string;
    to?: string;
    duration?: number;
    error?: string;
    message?: string;
  };
}

export type CallStatus =
  | 'queued'
  | 'ringing'
  | 'in-progress'
  | 'completed'
  | 'busy'
  | 'failed'
  | 'no-answer';
