"""CRUD operations for inference traces and evaluation results."""
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import InferenceTrace, EvaluationResult
from app.schemas.trace import (
    InferenceTraceCreate,
    EvaluationResultCreate,
    TraceMetricsAgg,
    EvaluationStatsAgg,
)


class CRUDInferenceTrace:
    """CRUD operations for InferenceTrace."""
    
    async def create(
        self,
        db: AsyncSession,
        obj_in: InferenceTraceCreate,
    ) -> InferenceTrace:
        """Create a new inference trace."""
        db_obj = InferenceTrace(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(
        self,
        db: AsyncSession,
        trace_id: UUID,
    ) -> Optional[InferenceTrace]:
        """Get trace by ID."""
        result = await db.execute(
            select(InferenceTrace).where(InferenceTrace.trace_id == trace_id)
        )
        return result.scalars().first()
    
    async def get_by_prompt_version(
        self,
        db: AsyncSession,
        prompt_version_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InferenceTrace]:
        """Get traces for a specific prompt version."""
        result = await db.execute(
            select(InferenceTrace)
            .where(InferenceTrace.prompt_version_id == prompt_version_id)
            .order_by(desc(InferenceTrace.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent(
        self,
        db: AsyncSession,
        hours: int = 24,
        limit: int = 100,
    ) -> List[InferenceTrace]:
        """Get traces from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await db.execute(
            select(InferenceTrace)
            .where(InferenceTrace.timestamp >= cutoff)
            .order_by(desc(InferenceTrace.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_metrics_by_version(
        self,
        db: AsyncSession,
        prompt_version_id: UUID,
        hours: int = 24,
    ) -> Optional[TraceMetricsAgg]:
        """Get aggregated metrics for a prompt version."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        result = await db.execute(
            select(
                func.count(InferenceTrace.trace_id).label("count"),
                func.avg(InferenceTrace.latency_ms).label("avg_latency_ms"),
                func.avg(InferenceTrace.tokens_in).label("avg_tokens_in"),
                func.avg(InferenceTrace.tokens_out).label("avg_tokens_out"),
                func.avg(InferenceTrace.cost_usd).label("avg_cost_usd"),
                func.min(InferenceTrace.latency_ms).label("min_latency_ms"),
                func.max(InferenceTrace.latency_ms).label("max_latency_ms"),
            )
            .where(
                (InferenceTrace.prompt_version_id == prompt_version_id)
                & (InferenceTrace.timestamp >= cutoff)
            )
        )
        
        row = result.first()
        if row and row[0] > 0:  # Check count
            return TraceMetricsAgg(
                prompt_version_id=prompt_version_id,
                count=row[0],
                avg_latency_ms=float(row[1] or 0),
                avg_tokens_in=float(row[2] or 0),
                avg_tokens_out=float(row[3] or 0),
                avg_cost_usd=float(row[4] or 0),
                min_latency_ms=int(row[5] or 0),
                max_latency_ms=int(row[6] or 0),
            )
        return None


class CRUDEvaluationResult:
    """CRUD operations for EvaluationResult."""
    
    async def create(
        self,
        db: AsyncSession,
        obj_in: EvaluationResultCreate,
    ) -> EvaluationResult:
        """Create a new evaluation result."""
        db_obj = EvaluationResult(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(
        self,
        db: AsyncSession,
        eval_id: UUID,
    ) -> Optional[EvaluationResult]:
        """Get evaluation by ID."""
        result = await db.execute(
            select(EvaluationResult).where(EvaluationResult.eval_id == eval_id)
        )
        return result.scalars().first()
    
    async def get_by_trace(
        self,
        db: AsyncSession,
        trace_id: UUID,
    ) -> List[EvaluationResult]:
        """Get all evaluations for a trace."""
        result = await db.execute(
            select(EvaluationResult)
            .where(EvaluationResult.trace_id == trace_id)
            .order_by(EvaluationResult.timestamp)
        )
        return result.scalars().all()
    
    async def get_by_evaluator(
        self,
        db: AsyncSession,
        evaluator_id: str,
        prompt_version_id: Optional[UUID] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> List[EvaluationResult]:
        """Get evaluations by evaluator ID (optionally filtered by prompt version)."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(EvaluationResult).where(
            (EvaluationResult.evaluator_id == evaluator_id)
            & (EvaluationResult.timestamp >= cutoff)
        )
        
        if prompt_version_id:
            # Join with trace to filter by prompt version
            query = query.join(InferenceTrace).where(
                InferenceTrace.prompt_version_id == prompt_version_id
            )
        
        query = query.order_by(desc(EvaluationResult.timestamp)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_stats_by_prompt_version(
        self,
        db: AsyncSession,
        prompt_version_id: UUID,
        hours: int = 24,
    ) -> Optional[EvaluationStatsAgg]:
        """Get aggregated evaluation stats for a prompt version."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get stats
        stats_result = await db.execute(
            select(
                func.count(EvaluationResult.eval_id).label("count"),
                func.avg(EvaluationResult.overall_score).label("avg_score"),
                func.min(EvaluationResult.overall_score).label("min_score"),
                func.max(EvaluationResult.overall_score).label("max_score"),
            )
            .select_from(EvaluationResult)
            .join(InferenceTrace)
            .where(
                (InferenceTrace.prompt_version_id == prompt_version_id)
                & (EvaluationResult.timestamp >= cutoff)
            )
        )
        
        stats = stats_result.first()
        if stats and stats[0] > 0:
            # Get unique evaluators
            eval_result = await db.execute(
                select(func.distinct(EvaluationResult.evaluator_id))
                .select_from(EvaluationResult)
                .join(InferenceTrace)
                .where(
                    (InferenceTrace.prompt_version_id == prompt_version_id)
                    & (EvaluationResult.timestamp >= cutoff)
                )
            )
            evaluators = [row[0] for row in eval_result.all()]
            
            return EvaluationStatsAgg(
                prompt_version_id=prompt_version_id,
                count=stats[0],
                avg_score=float(stats[1] or 0),
                min_score=float(stats[2] or 0),
                max_score=float(stats[3] or 0),
                evaluators=evaluators,
            )
        return None


# Singleton instances
crud_trace = CRUDInferenceTrace()
crud_evaluation = CRUDEvaluationResult()
