import { create } from 'zustand';
import * as Types from '@/lib/types';

interface DashboardState {
  // Metrics
  metrics: Types.DashboardMetrics | null;
  revenueTrend: Types.RevenueTrend | null;
  topProducts: Types.TopProducts | null;
  growth: Types.GrowthMetric | null;

  // UI State
  selectedPeriod: 'today' | 'week' | 'month' | 'quarter' | 'year';
  isLoading: boolean;
  error: string | null;

  // Chat
  conversations: Map<string, Types.ChatMessage[]>;
  currentConversationId: string;

  // Actions
  setMetrics: (metrics: Types.DashboardMetrics) => void;
  setRevenueTrend: (trend: Types.RevenueTrend) => void;
  setTopProducts: (products: Types.TopProducts) => void;
  setGrowth: (growth: Types.GrowthMetric) => void;
  setPeriod: (period: 'today' | 'week' | 'month' | 'quarter' | 'year') => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Chat actions
  addMessage: (conversationId: string, message: Types.ChatMessage) => void;
  getMessages: (conversationId: string) => Types.ChatMessage[];
  setCurrentConversation: (conversationId: string) => void;
  clearMessages: (conversationId: string) => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  metrics: null,
  revenueTrend: null,
  topProducts: null,
  growth: null,
  selectedPeriod: 'month',
  isLoading: false,
  error: null,
  conversations: new Map(),
  currentConversationId: 'default',

  setMetrics: (metrics) => set({ metrics }),
  setRevenueTrend: (trend) => set({ revenueTrend: trend }),
  setTopProducts: (products) => set({ topProducts: products }),
  setGrowth: (growth) => set({ growth }),
  setPeriod: (period) => set({ selectedPeriod: period }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  addMessage: (conversationId, message) => {
    const state = get();
    const conversations = new Map(state.conversations);
    const messages = conversations.get(conversationId) || [];
    conversations.set(conversationId, [...messages, message]);
    set({ conversations });
  },

  getMessages: (conversationId) => {
    const state = get();
    return state.conversations.get(conversationId) || [];
  },

  setCurrentConversation: (conversationId) => {
    set({ currentConversationId: conversationId });
  },

  clearMessages: (conversationId) => {
    const state = get();
    const conversations = new Map(state.conversations);
    conversations.delete(conversationId);
    set({ conversations });
  },
}));
