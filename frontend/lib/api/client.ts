import axios, { AxiosInstance } from 'axios';
import * as Types from '@/lib/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Dashboard Endpoints
  async getMetrics(period: 'today' | 'week' | 'month' | 'quarter' | 'year' = 'month'): Promise<Types.DashboardMetrics> {
    const response = await this.axiosInstance.get<Types.DashboardMetrics>(
      '/api/dashboard/metrics',
      { params: { period } }
    );
    return response.data;
  }

  async getRevenueTrend(days: number = 30): Promise<Types.RevenueTrend> {
    const response = await this.axiosInstance.get<Types.RevenueTrend>(
      '/api/dashboard/revenue-trend',
      { params: { days } }
    );
    return response.data;
  }

  async getTopProducts(limit: number = 10, period: 'week' | 'month' | 'quarter' | 'year' = 'month'): Promise<Types.TopProducts> {
    const response = await this.axiosInstance.get<Types.TopProducts>(
      '/api/dashboard/top-products',
      { params: { limit, period } }
    );
    return response.data;
  }

  async getGrowthRate(
    metric: 'revenue' | 'invoices' | 'customers' = 'revenue',
    periodDays: number = 30
  ): Promise<Types.GrowthMetric> {
    const response = await this.axiosInstance.get<Types.GrowthMetric>(
      '/api/dashboard/growth-rate',
      { params: { metric, period_days: periodDays } }
    );
    return response.data;
  }

  async getDashboardSummary(): Promise<Types.DashboardSummary> {
    const response = await this.axiosInstance.get<Types.DashboardSummary>(
      '/api/dashboard/summary'
    );
    return response.data;
  }

  // Chat & Query Endpoints
  async sendChat(request: Types.ChatRequest): Promise<Types.ChatResponse> {
    const response = await this.axiosInstance.post<Types.ChatResponse>(
      '/api/query/chat',
      request
    );
    return response.data;
  }

  async getQueryHistory(limit: number = 20, offset: number = 0): Promise<Types.QueryHistory> {
    const response = await this.axiosInstance.get<Types.QueryHistory>(
      '/api/query/history',
      { params: { limit, offset } }
    );
    return response.data;
  }

  async getInsights(): Promise<{ insights: string; generated_at: string }> {
    const response = await this.axiosInstance.post<{ insights: string; generated_at: string }>(
      '/api/query/insights'
    );
    return response.data;
  }

  async generateReport(title: string, days: number = 30, type: string = 'summary'): Promise<{ title: string; content: string; generated_at: string }> {
    const response = await this.axiosInstance.post<{ title: string; content: string; generated_at: string }>(
      '/api/query/report',
      { title, days, type }
    );
    return response.data;
  }

  // Detailed Data Endpoints
  async getInvoicesList(limit: number = 20, offset: number = 0): Promise<any> {
    const response = await this.axiosInstance.get(
      '/api/details/invoices',
      { params: { limit, offset } }
    );
    return response.data;
  }

  async getPaymentsList(limit: number = 20, offset: number = 0): Promise<any> {
    const response = await this.axiosInstance.get(
      '/api/details/payments',
      { params: { limit, offset } }
    );
    return response.data;
  }

  async getCustomersList(limit: number = 20, offset: number = 0): Promise<any> {
    const response = await this.axiosInstance.get(
      '/api/details/customers',
      { params: { limit, offset } }
    );
    return response.data;
  }

  async getInvoiceItems(invoiceId: number): Promise<any> {
    const response = await this.axiosInstance.get(
      `/api/details/invoice-items/${invoiceId}`
    );
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; app: string; env: string; version: string }> {
    const response = await this.axiosInstance.get(
      '/api/health'
    );
    return response.data;
  }
}

export const apiClient = new APIClient();
