"""Chat and query API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import logging

from app.config import get_settings
from app.db.database import get_db
from app.services.llm_service import LLMService
from app.models.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["query"])

settings = get_settings()


def get_llm_service():
    """Get LLM service instance."""
    return LLMService(api_key=settings.anthropic_api_key)


@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
):
    """Process natural language business questions."""
    try:
        # Process with Claude
        result = llm_service.chat(
            question=request.message,
            conversation_id=request.conversation_id,
        )

        # Log to query history
        from app.models.database import QueryHistory
        query_record = QueryHistory(
            natural_language_query=request.message,
            status="completed",
        )
        db.add(query_record)
        db.commit()

        return ChatResponse(
            conversation_id=result["conversation_id"],
            question=result["question"],
            response=result["response"],
            model=result["model"],
        )

    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_query_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get history of previous queries."""
    from app.models.database import QueryHistory

    total = db.query(QueryHistory).count()
    queries = (
        db.query(QueryHistory)
        .order_by(QueryHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "data": [
            {
                "id": q.id,
                "query": q.natural_language_query,
                "status": q.status,
                "created_at": str(q.created_at),
            }
            for q in queries
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/insights")
async def get_insights(
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
):
    """Generate business insights from current data."""
    try:
        from app.services.dashboard_service import DashboardService

        dashboard = DashboardService(db)
        metrics = dashboard.get_key_metrics(period_days=30)
        products = dashboard.get_top_products(limit=5, period_days=30)

        data_context = f"""
Current Business Metrics (Last 30 Days):
- Total Revenue: ${metrics['total_revenue']['value']:,.2f} ({metrics['total_revenue']['change_pct']:+.1f}%)
- Invoices: {metrics['invoice_count']['value']}
- Unique Customers: {metrics['customer_count']['value']}
- Avg Transaction: ${metrics['avg_transaction']['value']:,.2f}

Top 5 Products:
{json.dumps(products, indent=2)}
"""

        insights = llm_service.generate_insights(data_context)

        return {
            "insights": insights,
            "generated_at": str(__import__("datetime").datetime.utcnow()),
        }

    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report")
async def generate_report(
    request: dict,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
):
    """Generate a formatted business report."""
    try:
        from app.services.dashboard_service import DashboardService

        title = request.get("title", "Business Report")
        days = request.get("days", 30)

        dashboard = DashboardService(db)
        metrics = dashboard.get_key_metrics(period_days=days)
        trend = dashboard.get_revenue_trend(days=days)
        products = dashboard.get_top_products(limit=10, period_days=days)

        data_context = {
            "metrics": metrics,
            "revenue_trend": trend,
            "top_products": products,
        }

        report_content = llm_service.format_report(title, data_context)

        return {
            "title": title,
            "content": report_content,
            "generated_at": str(__import__("datetime").datetime.utcnow()),
        }

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
