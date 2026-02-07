import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Uuid

from sqlalchemy.orm import relationship
from app.db.base import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")

class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(Uuid(as_uuid=True), ForeignKey("prompts.id"), nullable=False)
    
    version = Column(String, nullable=False) # e.g. "1.0.0"
    semantic_intent = Column(String, nullable=True) # "polite factual support"
    risk_level = Column(String, default="low") # low, medium, high
    
    system_template = Column(String, nullable=True)
    user_template = Column(String, nullable=False)
    
    # Model config: {"model": "gpt-4", "temperature": 0.7, ...}
    model_config = Column(JSON, nullable=False)
    
    # Operational constraints: {"allowed_models": ["gpt-4"], "max_temp": 0.4}
    model_constraints = Column(JSON, nullable=True)
    
    parent_version_id = Column(Uuid(as_uuid=True), ForeignKey("prompt_versions.id"), nullable=True)
    author = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False) # Helper to mark "prod" version?

    prompt = relationship("Prompt", back_populates="versions")

    class Config:
        # Unique constraint on prompt_id + version
        pass
    
    @property
    def llm_config(self):
        """Compatibility alias for older code expecting `llm_config`."""
        return self.model_config
