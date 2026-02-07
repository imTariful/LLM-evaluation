"""
Metrics endpoints for retrieving platform statistics and performance metrics
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Dict, List, Any
from app.db.session import get_db
from app.models.trace import InferenceTrace, EvaluationResult
from app.models.prompt import PromptVersion
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/metrics/stats")
async def get_metrics_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get overall platform statistics"""
    try:
        # Count total inferences
        result = await db.execute(select(func.count(InferenceTrace.trace_id)))
        total_inferences = result.scalar() or 0
        
        # Get average score (from EvaluationResult)
        result = await db.execute(
            select(func.avg(EvaluationResult.overall_score))
        )
        avg_score = float(result.scalar() or 0)
        
        # Get best and worst scores
        result = await db.execute(
            select(func.max(EvaluationResult.overall_score))
        )
        best_score = float(result.scalar() or 0)
        
        result = await db.execute(
            select(func.min(EvaluationResult.overall_score))
        )
        worst_score = float(result.scalar() or 0)
        
        # Average latency (from InferenceTrace)
        result = await db.execute(
            select(func.avg(InferenceTrace.latency_ms))
            .where(InferenceTrace.latency_ms.isnot(None))
        )
        avg_latency = float(result.scalar() or 0)
        
        # Total cost
        result = await db.execute(
            select(func.sum(InferenceTrace.cost_usd))
            .where(InferenceTrace.cost_usd.isnot(None))
        )
        total_cost = float(result.scalar() or 0)
        
        # Drift (max - min of recent scores from EvaluationResult)
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(func.max(EvaluationResult.overall_score))
            .where(EvaluationResult.timestamp >= one_week_ago)
        )
        max_recent = float(result.scalar() or 0)
        
        result = await db.execute(
            select(func.min(EvaluationResult.overall_score))
            .where(EvaluationResult.timestamp >= one_week_ago)
        )
        min_recent = float(result.scalar() or 0)
        
        drift = max_recent - min_recent
        
        # Hallucination Rate (avg hallucination_probability from EvaluationResult metadata or specific evaluator)
        # For now, let's look for evaluator_id='hallucination'
        result = await db.execute(
            select(func.avg(EvaluationResult.overall_score))
            .where(EvaluationResult.evaluator_id == 'hallucination')
        )
        halluc_rate = float(result.scalar() or 0.05) # Default 5% if none
        
        return {
            "total_inferences": total_inferences,
            "avg_judge_score": round(avg_score, 2),
            "best_score": round(best_score, 2),
            "worst_score": round(worst_score, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "total_cost_usd": round(total_cost, 4),
            "hallucination_rate": round(halluc_rate, 4),
            "drift_7d": round(drift, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/metrics/by-version")
async def get_metrics_by_version(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get metrics aggregated by prompt version"""
    try:
        # Get all prompt versions with their metrics
        # Need to join Prompts to get name, and EvaluationResult for scores
        # This is a bit complex, simplifying to just Trace metrics for now + simple score avg if possible
        # Or just using Trace metrics since EvaluationResult might not exist for all
        
        # Correct approach: proper joins.
        from app.models.prompt import Prompt
        
        result = await db.execute(
            select(
                Prompt.name,
                PromptVersion.version,
                func.count(InferenceTrace.trace_id).label("count"),
                func.avg(InferenceTrace.latency_ms).label("avg_latency"),
                func.avg(InferenceTrace.cost_usd).label("avg_cost"),
                func.avg(InferenceTrace.overall_score).label("avg_score")
            )
            .select_from(PromptVersion)
            .join(Prompt, PromptVersion.prompt_id == Prompt.id)
            .outerjoin(InferenceTrace, InferenceTrace.prompt_version_id == PromptVersion.id)
            .group_by(Prompt.id, PromptVersion.id, Prompt.name, PromptVersion.version)
            .order_by(desc(PromptVersion.timestamp))
        )
        
        rows = result.all()
        
        metrics = []
        for row in rows:
            metrics.append({
                "prompt_name": row.name,
                "semantic_version": row.version,
                "count": int(row.count or 0),
                "avg_overall_score": round(float(row.avg_score or 0), 2),
                "avg_latency_ms": round(float(row.avg_latency or 0), 2),
                "avg_cost_usd": round(float(row.avg_cost or 0), 4)
            })
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch version metrics: {str(e)}")
