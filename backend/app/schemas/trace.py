"""Schemas for inference traces and evaluation results."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


# ============================================================================
# Inference Trace Schemas
# ============================================================================

class InferenceTraceBase(BaseModel):
    """Base schema for inference trace."""
    prompt_version_id: UUID
    inputs: Dict[str, Any]
    output: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: float
    model: str


class InferenceTraceCreate(InferenceTraceBase):
    """Create new inference trace."""
    pass


class InferenceTraceOut(InferenceTraceBase):
    """Return inference trace from API."""
    trace_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Evaluation Result Schemas
# ============================================================================

class EvaluationScores(BaseModel):
    """Structured evaluation scores."""
    correctness: Optional[float] = None
    completeness: Optional[float] = None
    safety: Optional[float] = None
    clarity: Optional[float] = None
    hallucination_risk: Optional[float] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


class EvaluationResultBase(BaseModel):
    """Base schema for evaluation result."""
    trace_id: UUID
    evaluator_id: str  # e.g., 'judge-gpt4', 'hallucination-detector'
    scores: Dict[str, Any]  # Flexible JSON for various evaluators
    overall_score: float  # Aggregate 0-10
    reasoning: str


class EvaluationResultCreate(EvaluationResultBase):
    """Create new evaluation result."""
    pass


class EvaluationResultOut(EvaluationResultBase):
    """Return evaluation result from API."""
    eval_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


class EvaluationResultWithTrace(EvaluationResultOut):
    """Evaluation result with associated trace details."""
    trace: InferenceTraceOut


# ============================================================================
# Aggregated Stats Schemas
# ============================================================================

class TraceMetricsAgg(BaseModel):
    """Aggregated metrics for traces over a period."""
    prompt_version_id: UUID
    count: int
    avg_latency_ms: float
    avg_tokens_in: float
    avg_tokens_out: float
    avg_cost_usd: float
    min_latency_ms: int
    max_latency_ms: int


class EvaluationStatsAgg(BaseModel):
    """Aggregated evaluation stats over a period."""
    prompt_version_id: UUID
    count: int
    avg_score: float
    min_score: float
    max_score: float
    evaluators: List[str]  # List of evaluators that ran
