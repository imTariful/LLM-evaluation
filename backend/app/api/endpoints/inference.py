"""Inference execution endpoint for running prompts through LLMs."""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app import schemas
from app.api import deps
from app.services.inference_service import inference_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/run", response_model=schemas.InferenceResponse)
async def run_inference(
    request: schemas.InferenceRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
) -> schemas.InferenceResponse:
    """
    Execute a prompt version with specific variables.
    
    - Resolves prompt by ID or name
    - Interpolates variables into templates
    - Runs through selected LLM provider
    - Logs trace to database
    - Triggers async evaluation in background
    
    Returns InferenceResponse with output and metrics.
    """
    try:
        return await inference_service.run_inference(db, request, background_tasks)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


