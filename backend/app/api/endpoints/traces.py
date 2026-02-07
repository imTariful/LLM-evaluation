"""
Traces endpoints for retrieving inference traces and evaluation results
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from app.db.session import get_db
from app.models.trace import InferenceTrace, EvaluationResult
from app.schemas.inference import TraceResponse, TraceDetailResponse, EvaluationResponse

router = APIRouter()


@router.get("/traces", response_model=List[TraceResponse])
async def list_traces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("timestamp", regex="^(timestamp|score|latency|cost)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of inference traces with optional sorting and pagination"""
    try:
        query = select(InferenceTrace)
        
        # Sort
        if sort_by == "timestamp":
            query = query.order_by(desc(InferenceTrace.timestamp) if order == "desc" else InferenceTrace.timestamp)
        elif sort_by == "score":
            query = query.order_by(desc(InferenceTrace.overall_score) if order == "desc" else InferenceTrace.overall_score)
        elif sort_by == "latency":
            query = query.order_by(desc(InferenceTrace.latency_ms) if order == "desc" else InferenceTrace.latency_ms)
        elif sort_by == "cost":
            query = query.order_by(desc(InferenceTrace.cost_usd) if order == "desc" else InferenceTrace.cost_usd)
        else:
            query = query.order_by(desc(InferenceTrace.timestamp))
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        traces = result.scalars().all()
        return traces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch traces: {str(e)}")


@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
async def get_trace(
    trace_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific trace"""
    try:
        from uuid import UUID
        # Convert string to UUID
        try:
            trace_uuid = UUID(trace_id)
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid trace ID format")
        
        result = await db.execute(
            select(InferenceTrace).where(InferenceTrace.trace_id == trace_uuid)
        )
        trace = result.scalars().first()
        
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return trace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trace: {str(e)}")


@router.get("/traces/{trace_id}/evaluations", response_model=List[EvaluationResponse])
async def get_trace_evaluations(
    trace_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get evaluation results for a specific trace"""
    try:
        from uuid import UUID
        # Convert string to UUID
        try:
            trace_uuid = UUID(trace_id)
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid trace ID format")
        
        result = await db.execute(
            select(EvaluationResult)
            .where(EvaluationResult.trace_id == trace_uuid)
            .order_by(desc(EvaluationResult.timestamp))
        )
        evaluations = result.scalars().all()
        
        if not evaluations:
            # Return empty list if no evaluations found (not an error)
            return []
        
        return evaluations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch evaluations: {str(e)}")
