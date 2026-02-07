import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Uuid

from pgvector.sqlalchemy import Vector
from app.db.base import Base

class KnowledgeBaseDocument(Base):
    __tablename__ = "knowledge_base"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True) # e.g. "manual.pdf"
    
    # Embedding vector (384 dim is common for small models, 1536 for OpenAI)
    embedding = Column(Vector(1536), nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)
