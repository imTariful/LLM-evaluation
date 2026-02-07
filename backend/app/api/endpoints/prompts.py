from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Prompt])
async def read_prompts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return await crud.prompt.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Prompt)
async def create_prompt(
    *,
    db: AsyncSession = Depends(deps.get_db),
    prompt_in: schemas.PromptCreate,
) -> Any:
    prompt = await crud.prompt.get_by_name_async(db, name=prompt_in.name)
    if prompt:
        raise HTTPException(status_code=400, detail="Prompt with this name already exists")
    prompt = await crud.prompt.create_async(db, obj_in=prompt_in)
    return prompt


@router.post("/{prompt_id}/versions", response_model=schemas.PromptVersion)
async def create_prompt_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    prompt_id: UUID,
    version_in: schemas.PromptVersionCreate,
) -> Any:
    prompt = await crud.prompt.get_async(db, id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    try:
        version = await crud.prompt.create_version_async(db, prompt_id=prompt_id, obj_in=version_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return version


@router.get("/{prompt_id}/versions/{version}", response_model=schemas.PromptVersion)
async def get_prompt_version(
    *,
    db: AsyncSession = Depends(deps.get_db),
    prompt_id: UUID,
    version: str,
) -> Any:
    result = await crud.prompt.get_version(db, prompt_id=prompt_id, version=version)
    if not result:
        raise HTTPException(status_code=404, detail="Version not found")
    return result
