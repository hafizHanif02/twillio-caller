import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_BASE_URL } from '../utils/constants';
import type { Call, CallHistoryResponse, OutboundCallRequest } from '../types/call';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Initiate an outbound call
   */
  async initiateCall(request: OutboundCallRequest): Promise<Call> {
    const response = await this.client.post<Call>('/api/calls/outbound', request);
    return response.data;
  }

  /**
   * Get call history with pagination
   */
  async getCallHistory(
    page: number = 1,
    pageSize: number = 50,
    direction?: 'inbound' | 'outbound',
    status?: string
  ): Promise<CallHistoryResponse> {
    const params: Record<string, any> = { page, page_size: pageSize };

    if (direction) params.direction = direction;
    if (status) params.status = status;

    const response = await this.client.get<CallHistoryResponse>('/api/calls/history', { params });
    return response.data;
  }

  /**
   * Get details for a specific call
   */
  async getCallDetails(callSid: string, syncFromTwilio: boolean = false): Promise<Call> {
    const response = await this.client.get<Call>(`/api/calls/${callSid}`, {
      params: { sync_from_twilio: syncFromTwilio }
    });
    return response.data;
  }

  /**
   * Get call statistics
   */
  async getStatistics(): Promise<Record<string, any>> {
    const response = await this.client.get('/api/calls/statistics/summary');
    return response.data;
  }

  /**
   * Get access token for Twilio Voice SDK
   */
  async getAccessToken(identity?: string): Promise<{ token: string; identity: string; expires_in: number }> {
    const params = identity ? { identity } : {};
    const response = await this.client.get('/api/calls/token', { params });
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
