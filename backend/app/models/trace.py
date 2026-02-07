import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Numeric, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid, JSON
from app.db.base import Base


class InferenceTrace(Base):
    """Log of LLM inference calls with performance metrics."""
    __tablename__ = "inference_traces"

    # Primary identifier
    trace_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to versioned prompt
    prompt_version_id = Column(Uuid(as_uuid=True), ForeignKey("prompt_versions.id"), nullable=False)
    
    # Request/Response data
    inputs = Column(JSON, nullable=False)  # Variables passed to prompt
    output = Column(Text, nullable=False)  # LLM output
    
    # Token usage
    tokens_in = Column(Integer, nullable=False)
    tokens_out = Column(Integer, nullable=False)
    
    # Performance metrics
    latency_ms = Column(Integer, nullable=False)  # End-to-end latency in milliseconds
    cost_usd = Column(Numeric(precision=10, scale=6), nullable=False)  # Cost of inference
    
    # Model used
    model = Column(String, nullable=False)  # e.g., "gpt-4-turbo", "claude-3-sonnet"
    
    # Cached quality score (average of all evaluations)
    overall_score = Column(Float, nullable=True)
    
    # Timestamp for time-series aggregation (REQUIRED for TimescaleDB hypertable)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    prompt_version = relationship("PromptVersion")
    evaluations = relationship("EvaluationResult", back_populates="trace", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_inference_traces_prompt_version_id', 'prompt_version_id'),
        Index('ix_inference_traces_timestamp', 'timestamp'),
    )


class EvaluationResult(Base):
    """Evaluation scores from multiple evaluators (judges)."""
    __tablename__ = "evaluation_results"
    
    # Primary identifier
    eval_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to trace
    trace_id = Column(Uuid(as_uuid=True), ForeignKey("inference_traces.trace_id"), nullable=False)
    
    # Which evaluator ran this? (e.g., 'judge-gpt4', 'hallucination-detector', 'toxicity-classifier')
    evaluator_id = Column(String, nullable=False)
    
    # Structured scores: {"correctness": 8, "completeness": 7, "safety": 10}
    scores = Column(JSON, nullable=False)
    
    # Aggregate score (0-10)
    overall_score = Column(Float, nullable=False)
    
    # Reasoning/explanation from evaluator
    reasoning = Column(Text, nullable=False)
    
    # Timestamp for time-series aggregation (REQUIRED for TimescaleDB hypertable)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    trace = relationship("InferenceTrace", back_populates="evaluations")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_evaluation_results_trace_id', 'trace_id'),
        Index('ix_evaluation_results_timestamp', 'timestamp'),
        Index('ix_evaluation_results_evaluator_id', 'evaluator_id'),
    )
