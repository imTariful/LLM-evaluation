from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Shared properties
class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None

class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    pass

class PromptInDBBase(PromptBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Prompt(PromptInDBBase):
    pass

# Versions
class PromptVersionBase(BaseModel):
    system_template: Optional[str] = None
    user_template: str
    semantic_intent: Optional[str] = "behavioral diff default"
    risk_level: str = "low"
    llm_config: Dict[str, Any] = {}
    model_constraints: Optional[Dict[str, Any]] = {
        "allowed_models": ["gpt-4-turbo", "gpt-3.5-turbo"],
        "max_temperature": 0.8
    }
    parent_version_id: Optional[UUID] = None
    author: Optional[str] = None

class PromptVersionCreate(PromptVersionBase):
    version: str # User specifies "1.0.0" or system auto-increments (logic in generic)
    is_active: bool = False

class PromptVersion(PromptVersionBase):
    id: UUID
    prompt_id: UUID
    version: str
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class PromptWithVersions(Prompt):
    versions: List[PromptVersion] = []
