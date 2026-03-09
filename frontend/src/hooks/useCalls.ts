import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { useCallStore } from '../store/callStore';
import type { Call, OutboundCallRequest } from '../types/call';

export function useCalls() {
  const {
    setActiveCall,
    setCallHistory,
    addCallToHistory,
    setIsLoading,
    setError,
  } = useCallStore();

  const [isInitiatingCall, setIsInitiatingCall] = useState(false);

  /**
   * Initiate an outbound call
   */
  const initiateCall = useCallback(async (toNumber: string): Promise<Call | null> => {
    try {
      setIsInitiatingCall(true);
      setError(null);

      const request: OutboundCallRequest = { to_number: toNumber };
      const call = await apiService.initiateCall(request);

      // Set as active call
      setActiveCall(call);

      // Add to call history
      addCallToHistory(call);

      console.log('Call initiated:', call);
      return call;

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to initiate call';
      setError(errorMessage);
      console.error('Error initiating call:', error);
      return null;

    } finally {
      setIsInitiatingCall(false);
    }
  }, [setActiveCall, addCallToHistory, setError]);

  /**
   * Fetch call history
   */
  const fetchCallHistory = useCallback(async (
    page: number = 1,
    pageSize: number = 50,
    direction?: 'inbound' | 'outbound',
    status?: string
  ) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiService.getCallHistory(page, pageSize, direction, status);

      setCallHistory(response.calls);

      return response;

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch call history';
      setError(errorMessage);
      console.error('Error fetching call history:', error);
      return null;

    } finally {
      setIsLoading(false);
    }
  }, [setCallHistory, setIsLoading, setError]);

  /**
   * Fetch details for a specific call
   */
  const fetchCallDetails = useCallback(async (callSid: string, syncFromTwilio: boolean = false): Promise<Call | null> => {
    try {
      setError(null);

      const call = await apiService.getCallDetails(callSid, syncFromTwilio);

      console.log('Fetched call details:', call);
      return call;

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch call details';
      setError(errorMessage);
      console.error('Error fetching call details:', error);
      return null;
    }
  }, [setError]);

  /**
   * Fetch call statistics
   */
  const fetchStatistics = useCallback(async () => {
    try {
      setError(null);

      const stats = await apiService.getStatistics();

      console.log('Fetched statistics:', stats);
      return stats;

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch statistics';
      setError(errorMessage);
      console.error('Error fetching statistics:', error);
      return null;
    }
  }, [setError]);

  return {
    initiateCall,
    isInitiatingCall,
    fetchCallHistory,
    fetchCallDetails,
    fetchStatistics,
  };
}
