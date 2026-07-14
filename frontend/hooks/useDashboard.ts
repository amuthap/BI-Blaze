import { useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { useDashboardStore } from '@/lib/store/dashboardStore';

export const useDashboard = () => {
  const {
    metrics,
    revenueTrend,
    topProducts,
    selectedPeriod,
    isLoading,
    error,
    setMetrics,
    setRevenueTrend,
    setTopProducts,
    setLoading,
    setError,
  } = useDashboardStore();

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [metricsData, trendData, productsData] = await Promise.all([
        apiClient.getMetrics(selectedPeriod),
        apiClient.getRevenueTrend(30),
        apiClient.getTopProducts(10, 'month'),
      ]);

      setMetrics(metricsData);
      setRevenueTrend(trendData);
      setTopProducts(productsData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [selectedPeriod]);

  return {
    metrics,
    revenueTrend,
    topProducts,
    selectedPeriod,
    isLoading,
    error,
    refresh: loadDashboard,
  };
};

export const useChat = () => {
  const {
    conversations,
    currentConversationId,
    getMessages,
    addMessage,
    setCurrentConversation,
  } = useDashboardStore();

  const sendMessage = async (message: string) => {
    try {
      // Add user message immediately for optimistic UI
      addMessage(currentConversationId, {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
      });

      // Send to API
      const response = await apiClient.sendChat({
        message,
        conversation_id: currentConversationId,
      });

      // Add assistant response
      addMessage(currentConversationId, {
        id: `msg-${Date.now()}-response`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      });

      return response;
    } catch (err) {
      // Add error message
      addMessage(currentConversationId, {
        id: `msg-${Date.now()}-error`,
        role: 'assistant',
        content: `Error: ${err instanceof Error ? err.message : 'Failed to send message'}`,
        timestamp: new Date(),
      });
      throw err;
    }
  };

  return {
    messages: getMessages(currentConversationId),
    currentConversationId,
    sendMessage,
    setCurrentConversation,
  };
};
