"""CRUD operations for prompts and prompt versions."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.prompt import Prompt, PromptVersion
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptVersionCreate


class CRUDPrompt:
    """CRUD operations for Prompts and PromptVersions."""
    
    # ========================================================================
    # Synchronous methods (for backwards compatibility with migrations)
    # ========================================================================
    
    def get(self, db: Session, id: UUID) -> Optional[Prompt]:
        """Get prompt by ID (sync)."""
        return db.query(Prompt).filter(Prompt.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Prompt]:
        """Get prompt by name (sync)."""
        return db.query(Prompt).filter(Prompt.name == name).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Prompt]:
        """List prompts (sync)."""
        return db.query(Prompt).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: PromptCreate) -> Prompt:
        """Create prompt (sync)."""
        db_obj = Prompt(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_version(self, db: Session, prompt_id: UUID, version: str) -> Optional[PromptVersion]:
        """Get specific version (sync)."""
        return db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version
            )
        ).first()

    def get_version_by_id(self, db: Session, version_id: UUID) -> Optional[PromptVersion]:
        """Get version by ID (sync)."""
        return db.query(PromptVersion).filter(PromptVersion.id == version_id).first()

    def create_version(self, db: Session, prompt_id: UUID, obj_in: PromptVersionCreate) -> PromptVersion:
        """Create version (sync)."""
        # Check if version exists
        existing = self.get_version(db, prompt_id, obj_in.version)
        if existing:
            raise ValueError(f"Version {obj_in.version} already exists for this prompt")

        db_obj = PromptVersion(
            prompt_id=prompt_id,
            version=obj_in.version,
            system_template=obj_in.system_template,
            user_template=obj_in.user_template,
            llm_config=obj_in.llm_config,
            author=obj_in.author,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    # ========================================================================
    # Asynchronous methods (for API handlers)
    # ========================================================================
    
    async def get_async(self, db: AsyncSession, id: UUID) -> Optional[Prompt]:
        """Get prompt by ID (async)."""
        result = await db.execute(
            select(Prompt).where(Prompt.id == id)
        )
        return result.scalars().first()
    
    async def get_by_name_async(self, db: AsyncSession, name: str) -> Optional[Prompt]:
        """Get prompt by name (async)."""
        result = await db.execute(
            select(Prompt).where(Prompt.name == name)
        )
        return result.scalars().first()
    
    async def create_async(self, db: AsyncSession, obj_in: PromptCreate) -> Prompt:
        """Create prompt (async)."""
        db_obj = Prompt(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_version_by_id(self, db: AsyncSession, version_id: UUID) -> Optional[PromptVersion]:
        """Get version by ID (async)."""
        result = await db.execute(
            select(PromptVersion).where(PromptVersion.id == version_id)
        )
        return result.scalars().first()

    async def get_version(self, db: AsyncSession, prompt_id: UUID, version: str) -> Optional[PromptVersion]:
        """Get specific version (async)."""
        result = await db.execute(
            select(PromptVersion).where(
                and_(
                    PromptVersion.prompt_id == prompt_id,
                    PromptVersion.version == version
                )
            )
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Prompt]:
        """List prompts (async)."""
        result = await db.execute(select(Prompt).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_active_version_by_name(
        self,
        db: AsyncSession,
        prompt_name: str,
    ) -> Optional[PromptVersion]:
        """
        Get the latest active version for a prompt by name.
        
        Args:
            db: AsyncSession
            prompt_name: Prompt name to look up
            
        Returns:
            Latest active PromptVersion or None
        """
        # Get prompt first
        prompt_result = await db.execute(
            select(Prompt).where(Prompt.name == prompt_name)
        )
        prompt = prompt_result.scalars().first()
        if not prompt:
            return None
        
        # Get active version for this prompt, ordered by created_at desc
        result = await db.execute(
            select(PromptVersion)
            .where(
                and_(
                    PromptVersion.prompt_id == prompt.id,
                    PromptVersion.is_active == True,
                )
            )
            .order_by(PromptVersion.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
    
    async def create_version_async(
        self,
        db: AsyncSession,
        prompt_id: UUID,
        obj_in: PromptVersionCreate,
    ) -> PromptVersion:
        """Create version (async)."""
        # Check if version exists
        result = await db.execute(
            select(PromptVersion).where(
                and_(
                    PromptVersion.prompt_id == prompt_id,
                    PromptVersion.version == obj_in.version,
                )
            )
        )
        existing = result.scalars().first()
        if existing:
            raise ValueError(f"Version {obj_in.version} already exists for this prompt")
        
        db_obj = PromptVersion(
            prompt_id=prompt_id,
            version=obj_in.version,
            system_template=obj_in.system_template,
            user_template=obj_in.user_template,
            llm_config=obj_in.llm_config,
            author=obj_in.author,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


prompt = CRUDPrompt()

