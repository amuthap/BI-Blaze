export interface MetricValue {
  value: number;
  change_pct: number;
}

export interface DashboardMetrics {
  total_revenue: MetricValue;
  invoice_count: MetricValue;
  customer_count: MetricValue;
  avg_transaction: MetricValue;
  period_days: number;
}

export interface RevenueTrendPoint {
  date: string;
  revenue: number;
}

export interface RevenueTrend {
  data: RevenueTrendPoint[];
  period_days: number;
}

export interface ProductSale {
  product_name: string;
  quantity_sold: number;
  revenue: number;
}

export interface TopProducts {
  data: ProductSale[];
  limit: number;
  period_days: number;
}

export interface GrowthMetric {
  metric: string;
  growth_percentage: number;
  period_days: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  conversation_id: string;
  question: string;
  response: string;
  model: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface DashboardSummary {
  metrics: DashboardMetrics;
  revenue_trend: RevenueTrend;
  top_products: TopProducts;
  growth: GrowthMetric;
  generated_at: string;
}

export interface QueryHistoryItem {
  id: number;
  query: string;
  status: string;
  created_at: string;
}

export interface QueryHistory {
  data: QueryHistoryItem[];
  total: number;
  limit: number;
  offset: number;
}
