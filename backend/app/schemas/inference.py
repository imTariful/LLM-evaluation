from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class InferenceRequest(BaseModel):
    prompt_version_id: Optional[UUID] = None # If using a managed prompt
    prompt_name: Optional[str] = None # access by name (latest active)
    
    variables: Dict[str, Any] = {} # Variables to fill the template
    
    # Context
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Overrides (optional)
    model: Optional[str] = None
    temperature: Optional[float] = None

class InferenceResponse(BaseModel):
    trace_id: UUID
    output: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    model: str


class TraceResponse(BaseModel):
    trace_id: UUID
    prompt_name: Optional[str] = None
    output: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    model: str
    overall_score: Optional[float] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TraceDetailResponse(TraceResponse):
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    eval_id: UUID
    trace_id: UUID
    evaluator_id: str
    overall_score: float
    scores: Dict[str, float] = Field(default_factory=dict)
    reasoning: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
