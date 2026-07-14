"""Pydantic schemas for API responses."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


# Dashboard Metrics
class MetricValue(BaseModel):
    """Single metric with change percentage."""
    value: float
    change_pct: float


class DashboardMetrics(BaseModel):
    """Key dashboard metrics."""
    total_revenue: MetricValue
    invoice_count: MetricValue
    customer_count: MetricValue
    avg_transaction: MetricValue
    period_days: int


class RevenueTrendPoint(BaseModel):
    """Single point in revenue trend."""
    date: str
    revenue: float


class RevenueTrend(BaseModel):
    """Revenue trend over time."""
    data: List[RevenueTrendPoint]
    period_days: int


class ProductSale(BaseModel):
    """Top selling product."""
    product_name: str
    quantity_sold: float
    revenue: float


class TopProducts(BaseModel):
    """Top products report."""
    data: List[ProductSale]
    limit: int
    period_days: int


class GrowthMetric(BaseModel):
    """Growth rate metric."""
    metric: str
    growth_percentage: float
    period_days: int


# Chat/Query
class ChatMessage(BaseModel):
    """Chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str
    conversation_id: Optional[str] = "default"
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    conversation_id: str
    question: str
    response: str
    model: str


class ReportData(BaseModel):
    """Generated report."""
    title: str
    content: str
    generated_at: str
    conversation_id: str


# Health/Status
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    env: str
    version: str
    database: str
    redis: Optional[str] = None


class SyncStatus(BaseModel):
    """Sync status response."""
    sync_id: str
    entity_type: str
    records_synced: int
    status: str  # "in_progress", "completed", "failed"
    error: Optional[str] = None


# Error Response
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str
    status_code: int
