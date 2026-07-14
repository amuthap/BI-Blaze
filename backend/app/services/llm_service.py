"""LLM service for Claude API integration via OpenAI-compatible endpoint."""

import logging
from openai import OpenAI
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LLMService:
    """Service for integrating Claude LLM for natural language queries."""

    SYSTEM_PROMPT = """You are an expert business intelligence analyst and SQL expert.
You have access to a business database with the following tables:

1. customers - customer information
   - id, zoho_id, name, email, phone, status, etc.

2. products - product/service catalog
   - id, zoho_id, name, description, sku, selling_price, etc.

3. invoices - financial records
   - id, zoho_id, invoice_number, customer_id, invoice_date, due_date, total, status, payment_status

4. invoice_line_items - invoice details
   - id, invoice_id, product_id, quantity, unit_price, item_total

5. payments - payment records
   - id, invoice_id, customer_id, payment_date, amount, payment_method

When a user asks a business question:
1. Analyze what they're asking for
2. Identify which tables are needed
3. Provide a SQL query to answer the question (PostgreSQL syntax)
4. Explain the results in business terms

Important constraints:
- Only use SELECT statements (read-only queries)
- Use proper date handling with PostgreSQL functions
- Always join tables properly to avoid cartesian products
- Format dates as YYYY-MM-DD
- Include LIMIT clauses for performance (default 100)

Format your response as JSON:
{
  "question": "the user's question",
  "sql_query": "the SQL query to execute",
  "explanation": "brief explanation of what this query does"
}"""

    def __init__(self, api_key: str):
        """Initialize Claude client via OpenAI-compatible endpoint."""
        self.client = OpenAI(
            base_url="http://135.181.170.46:4000/v1",
            api_key=api_key
        )
        self.conversation_history = {}

    def chat(self, question: str, conversation_id: str = "default") -> dict:
        """Process a natural language question about business data."""
        logger.info(f"Processing question: {question}")

        # Initialize conversation history if needed
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]

        # Add user message to history
        self.conversation_history[conversation_id].append({
            "role": "user",
            "content": question
        })

        # Call Claude via OpenAI-compatible endpoint
        response = self.client.chat.completions.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=self.conversation_history[conversation_id]
        )

        assistant_message = response.choices[0].message.content

        # Add assistant response to history
        self.conversation_history[conversation_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        logger.info(f"Claude response: {assistant_message[:100]}...")

        return {
            "conversation_id": conversation_id,
            "question": question,
            "response": assistant_message,
            "model": "claude-opus-4-8",
        }

    def generate_insights(self, data_context: dict) -> str:
        """Generate business insights from data context."""
        prompt = f"""Based on this business data, provide 3-5 key insights:

{data_context}

Focus on:
1. Revenue trends
2. Customer patterns
3. Sales performance
4. Growth opportunities"""

        response = self.client.chat.completions.create(
            model="claude-opus-4-8",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.choices[0].message.content

    def format_report(self, title: str, data: dict) -> str:
        """Format data into a business report."""
        prompt = f"""Format this business data into a professional report titled '{title}':

{data}

Include:
1. Executive Summary
2. Key Metrics
3. Trends and Analysis
4. Recommendations"""

        response = self.client.chat.completions.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.choices[0].message.content
