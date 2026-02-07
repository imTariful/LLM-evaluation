from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class EvaluationCreate(BaseModel):
    trace_id: UUID
    evaluator_id: str
    score: float
    metrics: Dict[str, Any]
    reasoning: Optional[str] = None

class EvaluationOut(EvaluationCreate):
    id: UUID
    timestamp: datetime
