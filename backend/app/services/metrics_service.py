from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models

class MetricsService:
    def get_aggregate_metrics(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """
        Returns time-series data for the dashboard.
        Aggregates Latency, Cost, and Quality Scores.
        """
        # In TimescaleDB, we would use time_bucket(). 
        # For standard Postgres compat in this demo, we'll use date_trunc.
        # SQLite fallback
        from app.core.config import settings
        
        if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
             bucket_expr = "strftime('%Y-%m-%d %H:00:00', timestamp)"
        else:
             bucket_expr = "date_trunc('hour', timestamp)"

        query = text(f"""
            SELECT 
                {bucket_expr} as bucket,
                AVG(latency_ms) as avg_latency,
                AVG(cost_usd) as avg_cost
            FROM inference_traces
            WHERE timestamp > :start_time
            GROUP BY bucket
            ORDER BY bucket ASC
        """)
        
        start_time = datetime.utcnow() - timedelta(days=days)
        result = db.execute(query, {"start_time": start_time}).fetchall()
        
        # Format for Recharts (Frontend)
        return [
            {
                "timestamp": row[0],
                "latency": float(row[1] or 0),
                "cost": float(row[2] or 0)
            }
            for row in result
        ]

    def get_quality_trend(self, db: Session, days: int = 7) -> List[Dict]:
        """
        Joins Traces with Evaluations to show Quality over time.
        """
        from app.core.config import settings
        if "sqlite" in settings.SQLALCHEMY_DATABASE_URI:
             bucket_expr = "strftime('%Y-%m-%d %H:00:00', t.timestamp)"
        else:
             bucket_expr = "date_trunc('hour', t.timestamp)"

        query = text(f"""
            SELECT 
                {bucket_expr} as bucket,
                AVG(e.score) as avg_score
            FROM inference_traces t
            JOIN evaluation_results e ON e.trace_id = t.id
            WHERE t.timestamp > :start_time
            GROUP BY bucket
            ORDER BY bucket ASC
        """)
        start_time = datetime.utcnow() - timedelta(days=days)
        result = db.execute(query, {"start_time": start_time}).fetchall()
        
        return [
            {"timestamp": row[0], "score": float(row[1] or 0)}
            for row in result
        ]

metrics_service = MetricsService()
